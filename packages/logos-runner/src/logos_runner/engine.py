from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from logos_runner.state.store import PlanStore
from logos_runner.stages.execution_gate import check_execution_gate, require_execution_gate
from logos_runner.stages.executor_prompt import build_executor_prompt
from logos_runner.stages.prompt_builder import build_stage_prompt
from logos_runner.stages.registry import PLANNING_SEQUENCE, StageDefinition, get_stage
from logos_runner.stages.result_materializer import materialize_stage_result
from logos_runner.stages.verification_gate import check_verification_gate, require_verification_gate
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
    prompt_path = prepare_stage_prompt(
        project_root=project_root,
        plan_id=plan_id,
        stage=stage,
        rebuild_prompt=rebuild_prompt,
    )
    return StageRunResult(
        stage=stage.name,
        status="prompt_ready",
        result_path=prompt_path,
        message="native subagent prompt ready; run this stage through Codex multi_agent_v1",
    )


def prepare_stage_prompt(
    *,
    project_root: Path,
    plan_id: str,
    stage: StageDefinition,
    rebuild_prompt: bool,
) -> Path:
    store = PlanStore(project_root)
    prompt_path = store.stage_prompt_path(plan_id, stage.name)

    if not prompt_path.exists() or rebuild_prompt:
        prompt = (
            build_executor_prompt(project_root, plan_id)
            if stage.name == "execute"
            else build_verification_prompt(project_root, plan_id)
            if stage.name == "verify"
            else build_stage_prompt(project_root, plan_id, stage)
        )
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt, encoding="utf-8")
        store.mark_stage_prompted(plan_id, stage.name, prompt_path)

    return prompt_path


def record_stage_result(
    *,
    project_root: Path,
    plan_id: str,
    stage: StageDefinition,
    raw_text: str,
) -> StageRunResult:
    store = PlanStore(project_root)
    raw_output_path = store.stage_raw_path(plan_id, stage.name)
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_output_path.write_text(raw_text, encoding="utf-8")
    store.mark_stage_output_ready(plan_id, stage.name, raw_output_path)
    materialized = materialize_stage_result(
        plan_dir=store.plan_dir(plan_id),
        stage=stage,
        raw_output_path=raw_output_path,
        stage_result_path=store.stage_result_path(plan_id, stage.name),
        official_result_path=store.official_result_path(plan_id, stage.output_file),
        error_path=store.stage_error_path(plan_id, stage.name),
    )
    if not materialized.ok:
        message = materialized.error or "result materialization failed"
        store.mark_stage_failed(plan_id, stage.name, message)
        return StageRunResult(
            stage=stage.name,
            status="failed",
            result_path=None,
            message=message,
        )

    store.mark_stage_result_ready(plan_id, stage.name, raw_output_path, materialized.result_path)
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
    names = _sequence_slice(from_stage, until_stage)
    if not names:
        return SequenceRunResult(plan_id, "failed", (), "empty stage sequence")
    prompt = prepare_stage_prompt(
            project_root=project_root,
            plan_id=plan_id,
        stage=get_stage(names[0]),
        rebuild_prompt=True,
    )
    return SequenceRunResult(
        plan_id,
        "prompt_ready",
        (),
        f"native subagent prompt ready: {prompt}",
    )


def run_execute_stage(
    *,
    project_root: Path,
    plan_id: str,
    timeout_seconds: int | None,
    dry_run: bool,
) -> StageRunResult:
    require_execution_gate(project_root, plan_id)
    stage = get_stage("execute")
    prompt = prepare_stage_prompt(
        project_root=project_root,
        plan_id=plan_id,
        stage=stage,
        rebuild_prompt=True,
    )
    return StageRunResult("execute", "prompt_ready", prompt, "native executor prompt ready")


def apply_recorded_execute_result(project_root: Path, plan_id: str) -> StageRunResult:
    store = PlanStore(project_root)
    stage = get_stage("execute")
    result_path = store.existing_stage_result_path(plan_id, stage.name, stage.output_file)
    valid = _validate_stage_result_file(store, plan_id, stage)
    if valid is not None:
        return valid
    data = store.read_stage_result(plan_id, stage.output_file)
    store.reflect_execution_result(plan_id, data)
    next_step = str(data.get("next_step", ""))
    status = str(data.get("status", ""))
    if status == "completed" and next_step == "verify":
        store.mark_stage_completed(plan_id, "execute")
        store.mark_ready_for_verify(plan_id)
        return StageRunResult("execute", "ready_for_verify", result_path, "ready for verify")
    if next_step == "plan":
        store.mark_redirect(plan_id, "plan", "executor requested plan revision")
        return StageRunResult("execute", "redirect", result_path, "executor requested plan revision")
    if next_step == "clarification":
        store.mark_waiting_user(
            plan_id,
            "execute",
            [str(data.get("blocked_reason", "execution requires clarification"))],
            [str(data.get("blocked_reason", "execution requires clarification"))],
        )
        return StageRunResult("execute", "waiting_user", result_path, "waiting for user clarification")

    store.mark_stage_failed(plan_id, "execute", f"unsupported execution result: {status}/{next_step}")
    return StageRunResult("execute", "failed", result_path, "unsupported execution result")


def run_verify_stage(
    *,
    project_root: Path,
    plan_id: str,
    timeout_seconds: int | None,
    dry_run: bool,
) -> StageRunResult:
    require_verification_gate(project_root, plan_id)
    stage = get_stage("verify")
    prompt = prepare_stage_prompt(
        project_root=project_root,
        plan_id=plan_id,
        stage=stage,
        rebuild_prompt=True,
    )
    return StageRunResult("verify", "prompt_ready", prompt, "native verification prompt ready")


def apply_recorded_verify_result(project_root: Path, plan_id: str) -> StageRunResult:
    store = PlanStore(project_root)
    stage = get_stage("verify")
    result_path = store.existing_stage_result_path(plan_id, stage.name, stage.output_file)
    valid = _validate_stage_result_file(store, plan_id, stage)
    if valid is not None:
        return valid
    final_valid = _validate_final_artifacts(store, plan_id)
    if final_valid is not None:
        return final_valid
    data = store.read_stage_result(plan_id, stage.output_file)
    store.reflect_verification_result(plan_id, data)
    next_step = str(data.get("next_step", ""))
    passed = data.get("passed")
    if passed is True and next_step == "complete":
        store.mark_stage_completed(plan_id, "verify")
        store.mark_verified(plan_id)
        return StageRunResult("verify", "verified", result_path, "verification passed")
    if next_step == "execute":
        store.mark_needs_rework(plan_id)
        return StageRunResult("verify", "needs_rework", result_path, "verification requires rework")
    if next_step == "plan":
        store.mark_needs_plan_revision(plan_id)
        return StageRunResult(
            "verify", "needs_plan_revision", result_path, "verification requires plan revision"
        )
    if next_step == "clarification":
        findings = list(data.get("findings", []))
        store.mark_waiting_user(plan_id, "verify", findings, findings)
        return StageRunResult("verify", "waiting_user", result_path, "verification requires clarification")

    store.mark_stage_failed(plan_id, "verify", f"unsupported verification result: {passed}/{next_step}")
    return StageRunResult("verify", "failed", result_path, "unsupported verification result")


def apply_stage_gate(project_root: Path, plan_id: str, stage_name: str) -> StageRunResult:
    store = PlanStore(project_root)
    stage = get_stage(stage_name)

    if stage.name == "execute":
        return apply_recorded_execute_result(project_root, plan_id)
    if stage.name == "verify":
        return apply_recorded_verify_result(project_root, plan_id)

    valid = _validate_stage_result_file(store, plan_id, stage)
    if valid is not None:
        return valid
    if stage.name == "plan":
        context_valid = _validate_json_file(store, plan_id, "context-handoff.json", stage.name)
        if context_valid is not None:
            return context_valid
    data = store.read_stage_result(plan_id, stage.output_file)
    decision = _apply_stage_decision(store, plan_id, stage, data)
    if decision == "continue":
        store.mark_stage_completed(plan_id, stage.name)
        next_stage = store.current_stage(plan_id)
        prompt_path = prepare_stage_prompt(
            project_root=project_root,
            plan_id=plan_id,
            stage=next_stage,
            rebuild_prompt=True,
        )
        return StageRunResult(
            stage=stage.name,
            status="next_prompt_ready",
            result_path=prompt_path,
            message=f"next stage prompt ready: {next_stage.name}",
        )
    if decision == "completed":
        return StageRunResult(stage.name, "ready_for_execute", None, "ready for execute")
    return StageRunResult(stage.name, decision, None, _message_for(decision))


def check_gate_status(project_root: Path, plan_id: str, stage_name: str) -> StageRunResult:
    if stage_name == "execute":
        gate = check_execution_gate(project_root, plan_id)
        return StageRunResult(
            "execute",
            "gate_passed" if gate.ok else "gate_blocked",
            None,
            "execution gate passed" if gate.ok else gate.reason or "execution gate blocked",
        )
    if stage_name == "verify":
        gate = check_verification_gate(project_root, plan_id)
        return StageRunResult(
            "verify",
            "gate_passed" if gate.ok else "gate_blocked",
            None,
            "verification gate passed" if gate.ok else gate.reason or "verification gate blocked",
        )
    return StageRunResult(stage_name, "gate_available", None, "record stage result, then apply gate")


def _validate_stage_result_file(
    store: PlanStore, plan_id: str, stage: StageDefinition
) -> StageRunResult | None:
    invalid = _validate_json_file(store, plan_id, stage.output_file, stage.name)
    if invalid is not None:
        return invalid
    try:
        data = store.read_stage_result(plan_id, stage.output_file)
    except (OSError, json.JSONDecodeError) as exc:
        return _fail_gate(store, plan_id, stage.name, f"invalid {stage.output_file}: {exc}")
    missing = [key for key in stage.required_keys if key not in data]
    if missing:
        return _fail_gate(
            store,
            plan_id,
            stage.name,
            "missing required keys in " + stage.output_file + ": " + ", ".join(missing),
        )
    if "schema_version" in stage.required_keys and data.get("schema_version") != 1:
        return _fail_gate(store, plan_id, stage.name, f"{stage.output_file} schema_version must be 1")
    return None


def _validate_final_artifacts(store: PlanStore, plan_id: str) -> StageRunResult | None:
    required = (
        ("scan-result.json", "scan"),
        ("intake-result.json", "intake"),
        ("spec.json", "spec"),
        ("task-plan.json", "plan"),
        ("context-handoff.json", "plan"),
        ("review-lite.json", "review_lite"),
        ("execution-result.json", "execute"),
        ("verification-result.json", "verify"),
    )
    for filename, stage_name in required:
        invalid = _validate_json_file(store, plan_id, filename, stage_name)
        if invalid is not None:
            return invalid
    return None


def _validate_json_file(
    store: PlanStore, plan_id: str, filename: str, stage_name: str
) -> StageRunResult | None:
    stage = get_stage(stage_name)
    path = (
        store.existing_stage_result_path(plan_id, stage_name, filename)
        if filename == stage.output_file
        else store.plan_dir(plan_id) / filename
    )
    if not path.exists():
        return _fail_gate(store, plan_id, stage_name, f"required artifact missing: {filename}")
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _fail_gate(store, plan_id, stage_name, f"invalid JSON artifact {filename}: {exc}")
    return None


def _fail_gate(store: PlanStore, plan_id: str, stage_name: str, message: str) -> StageRunResult:
    store.mark_stage_failed(plan_id, stage_name, message)
    return StageRunResult(stage_name, "failed", None, message)


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
            questions = data.get("required_questions")
            if not isinstance(questions, list) or not questions:
                questions = data.get("questions")
            store.mark_waiting_user(
                plan_id,
                stage.name,
                list(questions or []),
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
