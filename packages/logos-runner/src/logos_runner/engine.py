from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from logos_runner.codex.worker import run_codex_worker
from logos_runner.state.store import PlanStore
from logos_runner.stages.execution_gate import require_execution_gate
from logos_runner.stages.executor_prompt import build_executor_prompt
from logos_runner.stages.prompt_builder import build_stage_prompt
from logos_runner.stages.registry import PLANNING_SEQUENCE, StageDefinition, get_stage
from logos_runner.stages.result_materializer import materialize_stage_result
from logos_runner.stages.verification_gate import require_verification_gate
from logos_runner.stages.verification_prompt import build_verification_prompt


@dataclass(frozen=True)
class StageRunResult:
    stage: str
    status: str
    result_path: Path | None
    message: str


@dataclass(frozen=True)
class SequenceRunResult:
    plan_id: str
    status: str
    completed_stages: tuple[str, ...]
    message: str


def run_stage_once(
    *,
    project_root: Path,
    plan_id: str,
    stage: StageDefinition,
    timeout_seconds: int | None,
    dry_run: bool,
    rebuild_prompt: bool,
    simulate_intake_missing: bool = False,
) -> StageRunResult:
    store = PlanStore(project_root)
    plan_dir = store.plan_dir(plan_id)
    prompt_path = plan_dir / f"{stage.name}-prompt.md"

    if not prompt_path.exists() or rebuild_prompt:
        prompt = (
            build_executor_prompt(project_root, plan_id)
            if stage.name == "execute"
            else build_verification_prompt(project_root, plan_id)
            if stage.name == "verify"
            else build_stage_prompt(project_root, plan_id, stage)
        )
        prompt_path.write_text(prompt, encoding="utf-8")
        store.mark_stage_prompted(plan_id, stage.name, prompt_path)

    store.mark_stage_running(plan_id, stage.name)
    worker = run_codex_worker(
        project_root=project_root,
        plan_dir=plan_dir,
        stage=stage,
        plan_id=plan_id,
        prompt_path=prompt_path,
        timeout_seconds=timeout_seconds,
        dry_run=dry_run,
        simulate_intake_missing=simulate_intake_missing,
    )

    if worker.return_code != 0:
        store.mark_stage_failed(plan_id, stage.name, f"codex exec returned {worker.return_code}")
        return StageRunResult(
            stage=stage.name,
            status="failed",
            result_path=None,
            message=f"codex exec returned {worker.return_code}",
        )

    store.mark_stage_output_ready(plan_id, stage.name, worker.raw_output_path)
    materialized = materialize_stage_result(plan_dir, stage, worker.raw_output_path)
    if not materialized.ok:
        message = materialized.error or "result materialization failed"
        store.mark_stage_failed(plan_id, stage.name, message)
        return StageRunResult(
            stage=stage.name,
            status="failed",
            result_path=None,
            message=message,
        )

    store.mark_stage_result_ready(plan_id, stage.name, worker.raw_output_path, materialized.result_path)
    return StageRunResult(
        stage=stage.name,
        status="result_ready",
        result_path=materialized.result_path,
        message="result ready",
    )


def run_planning_sequence(
    *,
    project_root: Path,
    plan_id: str,
    from_stage: str = "scan",
    until_stage: str = "review_lite",
    timeout_seconds: int | None,
    dry_run: bool,
    simulate_intake_missing: bool = False,
) -> SequenceRunResult:
    store = PlanStore(project_root)
    names = _sequence_slice(from_stage, until_stage)
    completed: list[str] = []

    for stage_name in names:
        stage = get_stage(stage_name)
        result = run_stage_once(
            project_root=project_root,
            plan_id=plan_id,
            stage=stage,
            timeout_seconds=timeout_seconds,
            dry_run=dry_run,
            rebuild_prompt=True,
            simulate_intake_missing=simulate_intake_missing,
        )
        if result.status != "result_ready":
            return SequenceRunResult(plan_id, "failed", tuple(completed), result.message)

        data = store.read_stage_result(plan_id, stage.output_file)
        decision = _apply_stage_decision(store, plan_id, stage, data)
        if decision != "continue":
            if decision == "completed":
                completed.append(stage.name)
            status = "ready_for_execute" if decision == "completed" else decision
            return SequenceRunResult(plan_id, status, tuple(completed), _message_for(status))

        store.mark_stage_completed(plan_id, stage.name)
        completed.append(stage.name)

    return SequenceRunResult(plan_id, "complete", tuple(completed), "sequence complete")


def run_execute_stage(
    *,
    project_root: Path,
    plan_id: str,
    timeout_seconds: int | None,
    dry_run: bool,
) -> StageRunResult:
    require_execution_gate(project_root, plan_id)
    store = PlanStore(project_root)
    stage = get_stage("execute")
    result = run_stage_once(
        project_root=project_root,
        plan_id=plan_id,
        stage=stage,
        timeout_seconds=timeout_seconds,
        dry_run=dry_run,
        rebuild_prompt=True,
    )
    if result.status != "result_ready":
        return result

    data = store.read_stage_result(plan_id, stage.output_file)
    next_step = str(data.get("next_step", ""))
    status = str(data.get("status", ""))
    if status == "completed" and next_step == "verify":
        store.mark_stage_completed(plan_id, "execute")
        store.mark_ready_for_verify(plan_id)
        return StageRunResult("execute", "ready_for_verify", result.result_path, "ready for verify")
    if next_step == "plan":
        store.mark_redirect(plan_id, "plan", "executor requested plan revision")
        return StageRunResult("execute", "redirect", result.result_path, "executor requested plan revision")
    if next_step == "clarification":
        store.mark_waiting_user(
            plan_id,
            "execute",
            [str(data.get("blocked_reason", "execution requires clarification"))],
            [str(data.get("blocked_reason", "execution requires clarification"))],
        )
        return StageRunResult("execute", "waiting_user", result.result_path, "waiting for user clarification")

    store.mark_stage_failed(plan_id, "execute", f"unsupported execution result: {status}/{next_step}")
    return StageRunResult("execute", "failed", result.result_path, "unsupported execution result")


def run_verify_stage(
    *,
    project_root: Path,
    plan_id: str,
    timeout_seconds: int | None,
    dry_run: bool,
) -> StageRunResult:
    require_verification_gate(project_root, plan_id)
    store = PlanStore(project_root)
    stage = get_stage("verify")
    result = run_stage_once(
        project_root=project_root,
        plan_id=plan_id,
        stage=stage,
        timeout_seconds=timeout_seconds,
        dry_run=dry_run,
        rebuild_prompt=True,
    )
    if result.status != "result_ready":
        return result

    data = store.read_stage_result(plan_id, stage.output_file)
    next_step = str(data.get("next_step", ""))
    passed = data.get("passed")
    if passed is True and next_step == "complete":
        store.mark_stage_completed(plan_id, "verify")
        store.mark_verified(plan_id)
        return StageRunResult("verify", "verified", result.result_path, "verification passed")
    if next_step == "execute":
        store.mark_needs_rework(plan_id)
        return StageRunResult("verify", "needs_rework", result.result_path, "verification requires rework")
    if next_step == "plan":
        store.mark_needs_plan_revision(plan_id)
        return StageRunResult(
            "verify", "needs_plan_revision", result.result_path, "verification requires plan revision"
        )
    if next_step == "clarification":
        findings = list(data.get("findings", []))
        store.mark_waiting_user(plan_id, "verify", findings, findings)
        return StageRunResult("verify", "waiting_user", result.result_path, "verification requires clarification")

    store.mark_stage_failed(plan_id, "verify", f"unsupported verification result: {passed}/{next_step}")
    return StageRunResult("verify", "failed", result.result_path, "unsupported verification result")


def _sequence_slice(from_stage: str, until_stage: str) -> tuple[str, ...]:
    start = PLANNING_SEQUENCE.index(from_stage)
    end = PLANNING_SEQUENCE.index(until_stage)
    if start > end:
        raise ValueError("from-stage must come before until-stage")
    return PLANNING_SEQUENCE[start : end + 1]


def _apply_stage_decision(
    store: PlanStore, plan_id: str, stage: StageDefinition, data: dict[str, object]
) -> str:
    next_step = str(data.get("next_step", ""))

    if stage.name == "scan":
        if next_step == "clarification":
            store.mark_waiting_user(
                plan_id,
                stage.name,
                list(data.get("question_candidates", [])),
                list(data.get("blocking_unknowns", [])),
            )
            return "waiting_user"
        if next_step == "intake":
            return "continue"

    if stage.name == "intake":
        if next_step == "ask_user":
            store.mark_waiting_user(
                plan_id,
                stage.name,
                list(data.get("questions", [])),
                list(data.get("blocking_unknowns", [])),
            )
            return "waiting_user"
        if next_step == "spec":
            return "continue"

    if stage.name == "spec":
        if next_step == "clarification":
            store.mark_waiting_user(
                plan_id,
                stage.name,
                list(data.get("blocking_open_questions", [])),
                list(data.get("blocking_open_questions", [])),
            )
            return "waiting_user"
        if next_step == "task_plan":
            return "continue"

    if stage.name == "plan":
        if next_step == "clarification":
            store.mark_waiting_user(
                plan_id,
                stage.name,
                list(data.get("blocking_open_questions", [])),
                list(data.get("blocking_open_questions", [])),
            )
            return "waiting_user"
        if next_step == "spec":
            store.mark_redirect(plan_id, "spec", "task plan requested spec revision")
            return "redirect"
        if next_step == "executor":
            return "continue"

    if stage.name == "review_lite":
        passed = data.get("passed")
        if next_step == "executor" and passed is True:
            store.mark_stage_completed(plan_id, stage.name)
            store.mark_ready_for_execute(plan_id)
            return "completed"
        if next_step == "clarification":
            store.mark_waiting_user(plan_id, stage.name, [], list(data.get("findings", [])))
            return "waiting_user"
        if next_step == "spec":
            store.mark_redirect(plan_id, "spec", "review-lite requested spec revision")
            return "redirect"
        if next_step == "plan":
            store.mark_redirect(plan_id, "plan", "review-lite requested plan revision")
            return "redirect"

    store.mark_stage_failed(plan_id, stage.name, f"unsupported next_step for {stage.name}: {next_step}")
    return "failed"


def _message_for(status: str) -> str:
    if status == "waiting_user":
        return "waiting for user clarification"
    if status == "redirect":
        return "sequence redirected"
    if status == "ready_for_execute":
        return "ready for execute"
    if status == "failed":
        return "sequence failed"
    return status
