from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from logos_runner.paths import RunnerPaths
from logos_runner.stages.registry import STAGE_REGISTRY, StageDefinition, get_stage


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_paths(plan_id: str | None) -> dict[str, str]:
    if not plan_id:
        return {}
    base = f".logos/plans/{plan_id}"
    return {
        "plan_state": f"{base}/plan-state.json",
        "request": f"{base}/request.json",
        "scan_result": f"{base}/stages/scan/result.json",
        "intake_result": f"{base}/stages/intake/result.json",
        "spec": f"{base}/spec.json",
        "task_plan": f"{base}/task-plan.json",
        "context_handoff": f"{base}/context-handoff.json",
        "review_lite": f"{base}/review-lite.json",
        "execution_result": f"{base}/execution-result.json",
        "verification_result": f"{base}/verification-result.json",
    }


@dataclass(frozen=True)
class CreatedPlan:
    plan_id: str
    plan_dir: Path
    run_id: str


class PlanStore:
    def __init__(self, project_root: Path) -> None:
        self.paths = RunnerPaths(project_root)

    def required_install_paths(self) -> tuple[Path, ...]:
        return (
            self.paths.root_agents,
            self.paths.nous_skill,
            self.paths.agents_dir / "logos" / "procedures",
            self.paths.procedures_dir / "intake.md",
            self.paths.procedures_dir / "exploration.md",
            self.paths.procedures_dir / "spec.md",
            self.paths.procedures_dir / "planning.md",
            self.paths.procedures_dir / "review.md",
            self.paths.procedures_dir / "execution.md",
            self.paths.procedures_dir / "verification.md",
            self.paths.procedures_dir / "resume.md",
            self.paths.agents_dir / "logos" / "roles",
            self.paths.roles_dir / "orch.md",
            self.paths.roles_dir / "intk.md",
            self.paths.roles_dir / "exp.md",
            self.paths.roles_dir / "sp.md",
            self.paths.roles_dir / "pln.md",
            self.paths.roles_dir / "exe.md",
            self.paths.roles_dir / "bd.md",
            self.paths.roles_dir / "fd.md",
            self.paths.roles_dir / "db.md",
            self.paths.roles_dir / "sys.md",
            self.paths.roles_dir / "test.md",
            self.paths.roles_dir / "sec.md",
            self.paths.roles_dir / "rv.md",
            self.paths.roles_dir / "vf.md",
            self.paths.roles_dir / "mem.md",
            self.paths.project_root / ".codex" / "config.toml",
            self.paths.project_root / ".codex" / "hooks.json",
            self.paths.project_root / ".codex" / "hooks" / "pre_tool_use.py",
            self.paths.project_root / ".codex" / "hooks" / "permission_request.py",
            self.paths.project_root / ".codex" / "hooks" / "post_tool_use.py",
            self.paths.project_root / ".codex" / "hooks" / "post_compact.py",
            self.paths.logos_dir / "bin" / "logos-runner.ps1",
            self.paths.logos_dir / "bin" / "logos-runner.cmd",
            self.paths.logos_dir / "config.toml",
            self.paths.logos_dir / "target.toml",
            self.paths.logos_dir / "active-profile.toml",
            self.paths.logos_dir / "session" / "nous-state.json",
            self.paths.plans_dir,
            self.paths.runs_dir,
            self.paths.memory_dir,
            self.paths.logos_dir / "evidence",
            self.paths.logos_dir / "generated" / "install-manifest.json",
            self.paths.logos_dir / "generated" / "asset-manifest.json",
            self.paths.logos_dir / "generated" / "asset-hashes.json",
            self.paths.logos_dir / "generated" / "guards-manifest.json",
            self.paths.logos_dir / "generated" / "prompt-assembly-manifest.json",
        )

    def create_plan(self, request: str) -> CreatedPlan:
        created_at = _now()
        plan_id = f"plan_{created_at.replace(':', '').replace('-', '').replace('+', 'Z')}_{uuid4().hex[:8]}"
        run_id = f"run-{created_at.replace(':', '').replace('-', '').replace('+', 'Z')}"
        plan_dir = self.paths.plans_dir / plan_id
        plan_dir.mkdir(parents=True, exist_ok=False)

        _write_json(
            plan_dir / "request.json",
            {
                "schema_version": 1,
                "plan_id": plan_id,
                "created_at": created_at,
                "user_request": request,
            },
        )
        _write_json(
            plan_dir / "plan-state.json",
            {
                "schema_version": 1,
                "plan_id": plan_id,
                "status": "created",
                "current_stage": "scan",
                "run_id": run_id,
                "created_at": created_at,
                "updated_at": created_at,
                "completed_stages": [],
            },
        )
        self._create_run(run_id, plan_id, request, created_at)
        self._set_active_work(plan_id=plan_id, run_id=run_id, status="active", updated_at=created_at)
        return CreatedPlan(plan_id=plan_id, plan_dir=plan_dir, run_id=run_id)

    def list_plans(self) -> list[dict[str, str]]:
        if not self.paths.plans_dir.exists():
            return []

        plans: list[dict[str, str]] = []
        for plan_dir in sorted(self.paths.plans_dir.iterdir(), reverse=True):
            if not plan_dir.is_dir():
                continue
            state_path = plan_dir / "plan-state.json"
            if not state_path.exists():
                continue
            try:
                state = _read_json(state_path)
            except (OSError, json.JSONDecodeError):
                continue
            plans.append(
                {
                    "plan_id": str(state.get("plan_id", plan_dir.name)),
                    "status": str(state.get("status", "unknown")),
                    "updated_at": str(state.get("updated_at", "")),
                }
            )
        return plans

    def plan_dir(self, plan_id: str) -> Path:
        return self.paths.plans_dir / plan_id

    def stage_dir(self, plan_id: str, stage_name: str) -> Path:
        return self.plan_dir(plan_id) / "stages" / _stage_folder_name(stage_name)

    def stage_prompt_path(self, plan_id: str, stage_name: str) -> Path:
        return self.stage_dir(plan_id, stage_name) / "prompt.md"

    def stage_raw_path(self, plan_id: str, stage_name: str) -> Path:
        return self.stage_dir(plan_id, stage_name) / "raw.md"

    def stage_result_path(self, plan_id: str, stage_name: str) -> Path:
        return self.stage_dir(plan_id, stage_name) / "result.json"

    def stage_error_path(self, plan_id: str, stage_name: str, kind: str = "parse-error") -> Path:
        return self.plan_dir(plan_id) / "errors" / f"{_stage_folder_name(stage_name)}-{kind}.json"

    def legacy_stage_prompt_path(self, plan_id: str, stage_name: str) -> Path:
        return self.plan_dir(plan_id) / f"{stage_name}-prompt.md"

    def legacy_stage_raw_path(self, plan_id: str, stage_name: str) -> Path:
        return self.plan_dir(plan_id) / f"{stage_name}-raw.md"

    def legacy_stage_result_path(self, plan_id: str, stage_name: str, output_file: str) -> Path:
        if output_file.startswith(f"{stage_name}-"):
            return self.plan_dir(plan_id) / output_file
        return self.plan_dir(plan_id) / f"{stage_name}-result.json"

    def official_result_path(self, plan_id: str, output_file: str) -> Path:
        return self.plan_dir(plan_id) / output_file

    def existing_stage_result_path(self, plan_id: str, stage_name: str, output_file: str) -> Path:
        candidates = (
            self.official_result_path(plan_id, output_file),
            self.stage_result_path(plan_id, stage_name),
            self.legacy_stage_result_path(plan_id, stage_name, output_file),
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def read_state(self, plan_id: str) -> dict[str, object]:
        return _read_json(self.plan_dir(plan_id) / "plan-state.json")

    def read_request(self, plan_id: str) -> dict[str, object]:
        return _read_json(self.plan_dir(plan_id) / "request.json")

    def current_stage(self, plan_id: str) -> StageDefinition:
        state = self.read_state(plan_id)
        return get_stage(str(state.get("current_stage", "scan")))

    def mark_stage_prompted(self, plan_id: str, stage_name: str, prompt_path: Path) -> None:
        state = self.read_state(plan_id)
        state["status"] = "prompt_ready"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        state["current_prompt"] = str(prompt_path)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_stage_completed(self, plan_id: str, stage_name: str) -> None:
        state = self.read_state(plan_id)
        completed = list(state.get("completed_stages", []))
        if stage_name not in completed:
            completed.append(stage_name)
        next_stage = _next_stage_name(stage_name)
        state["completed_stages"] = completed
        state["current_stage"] = next_stage or stage_name
        state["status"] = "complete" if next_stage is None else "ready"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)
        self._touch_active_run(plan_id, status=str(state["status"]))

    def mark_stage_running(self, plan_id: str, stage_name: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "running"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_stage_failed(self, plan_id: str, stage_name: str, error: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "failed"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        state["last_error"] = error
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)
        self._touch_active_run(plan_id, status="failed", summary=error)

    def mark_stage_output_ready(self, plan_id: str, stage_name: str, raw_output_path: Path) -> None:
        state = self.read_state(plan_id)
        state["status"] = "output_ready"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        state["current_raw_output"] = str(raw_output_path)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_stage_result_ready(
        self, plan_id: str, stage_name: str, raw_output_path: Path, result_path: Path
    ) -> None:
        state = self.read_state(plan_id)
        state["status"] = "result_ready"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        state["current_raw_output"] = str(raw_output_path)
        state["current_result"] = str(result_path)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_waiting_user(
        self,
        plan_id: str,
        stage_name: str,
        questions: list[object],
        blocking_unknowns: list[object],
    ) -> None:
        state = self.read_state(plan_id)
        state["status"] = "waiting_user"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        state["waiting_since"] = state["updated_at"]
        state["answered"] = False
        state["pending_questions"] = questions
        state["blocking_unknowns"] = blocking_unknowns
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)
        self._touch_active_run(plan_id, status="active", summary=f"Waiting for user at {stage_name}")

    def mark_answered(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "answered"
        state["updated_at"] = _now()
        state["answered"] = True
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_ready_for_execute(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "ready_for_execute"
        state["current_stage"] = "execute"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)
        self._touch_active_run(plan_id, status="active", summary="Planning gates passed; ready for execute")

    def mark_ready_for_verify(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "ready_for_verify"
        state["current_stage"] = "verify"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)
        self._touch_active_run(plan_id, status="active", summary="Execution complete; ready for verify")

    def mark_verified(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "verified"
        state["current_stage"] = "complete"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)
        self._finish_run(plan_id)

    def mark_needs_rework(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "needs_rework"
        state["current_stage"] = "execute"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_needs_plan_revision(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "needs_plan_revision"
        state["current_stage"] = "plan"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def mark_redirect(self, plan_id: str, stage_name: str, reason: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "ready"
        state["current_stage"] = stage_name
        state["updated_at"] = _now()
        state["redirect_reason"] = reason
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

    def read_stage_result(self, plan_id: str, output_file: str) -> dict[str, object]:
        for stage in STAGE_REGISTRY:
            if stage.output_file == output_file:
                return _read_json(self.existing_stage_result_path(plan_id, stage.name, output_file))
        return _read_json(self.plan_dir(plan_id) / output_file)

    def read_run(self, plan_id: str) -> dict[str, object] | None:
        state = self.read_state(plan_id)
        run_id = state.get("run_id")
        if not isinstance(run_id, str):
            return None
        try:
            return _read_json(self.paths.runs_dir / run_id / "run.json")
        except (OSError, json.JSONDecodeError):
            return None

    def write_run(self, run: dict[str, object]) -> None:
        run_id = run.get("run_id")
        if not isinstance(run_id, str):
            return
        _write_json(self.paths.runs_dir / run_id / "run.json", run)
        self._update_run_index(run)
        self._update_resume_snapshot(run)

    def append_command_records(self, plan_id: str, commands: object) -> None:
        run = self.read_run(plan_id)
        if run is None or not isinstance(commands, list):
            return
        for item in commands:
            if not isinstance(item, dict):
                continue
            command = item.get("command")
            if not isinstance(command, str) or not command.strip():
                continue
            exit_code = item.get("exit_code")
            record = {
                "schema_version": 1,
                "run_id": run["run_id"],
                "recorded_at": _now(),
                "command": command,
                "cwd": item.get("cwd"),
                "tool_name": item.get("tool_name"),
                "exit_code": exit_code if isinstance(exit_code, int) else None,
                "summary": str(item.get("summary") or item.get("result") or command[:240]),
                "detected_by": "runner-stage-artifact",
            }
            _append_jsonl(self.paths.runs_dir / str(run["run_id"]) / "commands.jsonl", record)
            run["command_count"] = int(run.get("command_count", 0)) + 1
            run["last_command"] = command
            if isinstance(exit_code, int) and exit_code != 0:
                run["last_error"] = record["summary"]
        self.write_run(run)

    def append_test_records(self, plan_id: str, tests: object) -> None:
        run = self.read_run(plan_id)
        if run is None or not isinstance(tests, list):
            return
        for item in tests:
            if not isinstance(item, dict):
                continue
            normalized = _normalize_test_record(item)
            record = {
                "schema_version": 1,
                "run_id": run["run_id"],
                "recorded_at": _now(),
                **normalized,
                "detected_by": "runner-stage-artifact",
            }
            _append_jsonl(self.paths.runs_dir / str(run["run_id"]) / "tests.jsonl", record)
            run["test_count"] = int(run.get("test_count", 0)) + 1
            run["failed_test_count"] = int(run.get("failed_test_count", 0)) + int(record.get("failed_count", 0))
            run["test_summary"] = _summarize_tests(run, record)
        self.write_run(run)

    def merge_touched_files(self, plan_id: str, files: object) -> None:
        run = self.read_run(plan_id)
        if run is None or not isinstance(files, list):
            return
        touched = run.setdefault("touched_files", [])
        if not isinstance(touched, list):
            touched = []
            run["touched_files"] = touched
        for item in files:
            path = item if isinstance(item, str) else item.get("path") if isinstance(item, dict) else None
            if not isinstance(path, str) or not path:
                continue
            normalized = _normalize_touched_path(path)
            if not normalized:
                continue
            path = normalized
            if path not in touched:
                touched.append(path)
            if _file_record_exists(self.paths.runs_dir / str(run["run_id"]) / "files.jsonl", path):
                continue
            record = {
                "schema_version": 1,
                "run_id": run["run_id"],
                "recorded_at": _now(),
                "path": path,
                "change_type": item.get("change_type", "modified") if isinstance(item, dict) else "modified",
                "detected_by": "runner-stage-artifact",
            }
            _append_jsonl(self.paths.runs_dir / str(run["run_id"]) / "files.jsonl", record)
        self.write_run(run)

    def reflect_execution_result(self, plan_id: str, data: dict[str, object]) -> None:
        run = self.read_run(plan_id)
        if run is None:
            return
        run["execution_summary"] = _summarize_list(
            data.get("implemented_steps"),
            fallback=str(data.get("status") or "Execution result recorded."),
        )
        deviations = data.get("deviations_from_plan")
        if isinstance(deviations, list) and deviations:
            run["execution_deviations"] = [str(item) for item in deviations if str(item).strip()]
        self.write_run(run)
        self.merge_touched_files(plan_id, data.get("modified_files"))
        self.append_command_records(plan_id, data.get("commands_run"))
        self.append_test_records(plan_id, data.get("tests_run"))

    def reflect_verification_result(self, plan_id: str, data: dict[str, object]) -> None:
        run = self.read_run(plan_id)
        if run is None:
            return
        passed = data.get("passed")
        findings = data.get("findings")
        remaining_risk = data.get("remaining_risk")
        run["verification_summary"] = _verification_summary(data)
        if isinstance(remaining_risk, list) and remaining_risk:
            run["summary"] = "Verification completed with remaining risk"
        if passed is False:
            run["status"] = "failed"
            run["failure_reason"] = _summarize_list(findings, fallback="verification failed")
            run["last_error"] = run["failure_reason"]
        self.write_run(run)
        self.merge_touched_files(plan_id, _paths_from_modified_file_review(data.get("modified_files_review")))
        self.append_command_records(plan_id, data.get("commands_run"))
        self.append_test_records(plan_id, data.get("tests_run"))

    def append_user_answer(self, plan_id: str, answer: str) -> Path:
        state = self.read_state(plan_id)
        path = self.plan_dir(plan_id) / "user-answers.jsonl"
        record: dict[str, object] = {
            "schema_version": 1,
            "recorded_at": _now(),
            "stage": str(state.get("current_stage", "")),
            "answer": answer,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.mark_answered(plan_id)
        return path

    def read_user_answers(self, plan_id: str) -> list[dict[str, object]]:
        path = self.plan_dir(plan_id) / "user-answers.jsonl"
        if not path.exists():
            return []
        answers: list[dict[str, object]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                answers.append(data)
        return answers

    def _create_run(self, run_id: str, plan_id: str, request: str, created_at: str) -> None:
        run = {
            "schema_version": 1,
            "run_id": run_id,
            "plan_id": plan_id,
            "selected_mode": "nous",
            "status": "active",
            "started_at": created_at,
            "ended_at": None,
            "user_request": request,
            "summary": "Active Logos plan",
            "execution_summary": "",
            "execution_deviations": [],
            "verification_summary": "",
            "test_summary": "",
            "final_response_summary": "",
            "failure_reason": None,
            "last_command": None,
            "last_error": None,
            "touched_files": [],
            "command_count": 0,
            "guard_decision_count": 0,
            "test_count": 0,
            "failed_test_count": 0,
            "artifact_paths": _artifact_paths(plan_id),
        }
        _write_json(self.paths.runs_dir / run_id / "run.json", run)
        self._update_run_index(run)
        self._update_resume_snapshot(run)

    def _touch_active_run(self, plan_id: str, *, status: str, summary: str | None = None) -> None:
        state = self.read_state(plan_id)
        run_id = state.get("run_id")
        if not isinstance(run_id, str):
            return
        run_path = self.paths.runs_dir / run_id / "run.json"
        try:
            run = _read_json(run_path)
        except (OSError, json.JSONDecodeError):
            return
        run["status"] = status
        run["summary"] = summary or f"Current stage: {state.get('current_stage')}"
        if status == "failed":
            run["failure_reason"] = summary or str(state.get("last_error") or "stage failed")
            run["last_error"] = run["failure_reason"]
        self._set_active_work(plan_id=plan_id, run_id=run_id, status="active", updated_at=_now())
        _write_json(run_path, run)
        self._update_run_index(run)
        self._update_resume_snapshot(run)

    def _finish_run(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        run_id = state.get("run_id")
        if not isinstance(run_id, str):
            return
        run_path = self.paths.runs_dir / run_id / "run.json"
        try:
            run = _read_json(run_path)
        except (OSError, json.JSONDecodeError):
            return
        run["status"] = "completed"
        run["ended_at"] = _now()
        run["summary"] = "Logos plan completed and verified"
        if not run.get("failure_reason"):
            run["last_error"] = None
        _write_json(run_path, run)
        self._update_run_index(run)
        self._update_resume_snapshot(run)
        self._set_active_work(plan_id=None, run_id=run_id, status="completed", updated_at=str(run["ended_at"]))

    def _set_active_work(
        self, *, plan_id: str | None, run_id: str | None, status: str, updated_at: str
    ) -> None:
        _write_json(
            self.paths.memory_dir / "active-work.json",
            {
                "schema_version": 1,
                "status": status,
                "active_plan_id": plan_id,
                "active_run_id": run_id,
                "updated_at": updated_at,
            },
        )

    def _update_run_index(self, run: dict[str, object]) -> None:
        path = self.paths.memory_dir / "run-index.json"
        try:
            index = _read_json(path)
        except (OSError, json.JSONDecodeError):
            index = {"schema_version": 1, "runs": []}
        runs = index.setdefault("runs", [])
        if isinstance(runs, list):
            active_run_id = (
                str(run.get("run_id")) if run.get("status") == "active" else _active_run_id(self.paths.project_root)
            )
            runs[:] = [
                item for item in runs if not isinstance(item, dict) or item.get("run_id") != run.get("run_id")
            ]
            for item in runs:
                if (
                    isinstance(item, dict)
                    and item.get("status") == "active"
                    and item.get("run_id") != active_run_id
                ):
                    item["status"] = "stale"
            runs.append(
                {
                    "run_id": run.get("run_id"),
                    "plan_id": run.get("plan_id"),
                    "status": run.get("status"),
                    "started_at": run.get("started_at"),
                    "summary": run.get("summary", ""),
                    "touched_files": run.get("touched_files", []),
                }
            )
            del runs[:-25]
        index["updated_at"] = _now()
        _write_json(path, index)

    def _update_resume_snapshot(self, run: dict[str, object]) -> None:
        touched = run.get("touched_files") if isinstance(run.get("touched_files"), list) else []
        artifact_paths = run.get("artifact_paths") if isinstance(run.get("artifact_paths"), dict) else {}
        status = run.get("status") or "unknown"
        plan_id = run.get("plan_id")
        lines = [
            "# Logos Resume Snapshot",
            "",
            "Read this file only when continuing after context loss, compaction, or an unclear work state.",
            "Do not scan raw `.logos/runs` or `.logos/evidence` first.",
            "",
            f"Updated: {_now()}",
            f"Status: {status}",
            f"Current task: {run.get('summary') or 'Active Logos work'}",
            f"Last run id: {run.get('run_id')}",
            f"Active plan id: {plan_id}",
            "",
            "## Current Summaries",
            f"- Execution: {run.get('execution_summary') or 'Not recorded yet.'}",
            f"- Deviations: {_format_deviations(run.get('execution_deviations'))}",
            f"- Tests: {run.get('test_summary') or 'Not recorded yet.'}",
            f"- Verification: {run.get('verification_summary') or 'Not recorded yet.'}",
            "",
            "## Touched Files",
        ]
        lines.extend([f"- {item}" for item in touched[:20]] or ["- None"])
        look_next = [
            ".logos/memory/active-work.json",
            ".logos/memory/run-index.json",
            str(artifact_paths.get("plan_state") or f".logos/plans/{plan_id}/plan-state.json"),
            str(artifact_paths.get("task_plan") or f".logos/plans/{plan_id}/task-plan.json"),
        ]
        execution_result = artifact_paths.get("execution_result")
        verification_result = artifact_paths.get("verification_result")
        if execution_result:
            look_next.append(str(execution_result))
        if verification_result:
            look_next.append(str(verification_result))
        lines.extend(["", "## Where To Look Next"])
        lines.extend(f"- {item}" for item in look_next[:8])
        path = self.paths.memory_dir / "resume-snapshot.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _next_stage_name(stage_name: str) -> str | None:
    names = [stage.name for stage in STAGE_REGISTRY]
    try:
        index = names.index(stage_name)
    except ValueError:
        return None
    next_index = index + 1
    return names[next_index] if next_index < len(names) else None


def _stage_folder_name(stage_name: str) -> str:
    return stage_name.replace("_", "-")


def _clear_waiting_fields(state: dict[str, object]) -> None:
    state.pop("pending_questions", None)
    state.pop("blocking_unknowns", None)
    state.pop("waiting_since", None)
    state.pop("answered", None)


def _non_negative_int(value: object) -> int:
    return value if isinstance(value, int) and value > 0 else 0


def _summarize_tests(run: dict[str, object], latest: dict[str, object]) -> str:
    status = str(latest.get("status") or "recorded")
    summary = str(latest.get("summary") or "")
    count = int(run.get("test_count", 0))
    failed = int(run.get("failed_test_count", 0))
    if failed:
        return f"{count} test record(s); {failed} failed. Latest: {status}. {summary}".strip()
    return f"{count} test record(s), all recorded as passing or non-failing. Latest: {status}. {summary}".strip()


def _summarize_list(value: object, *, fallback: str) -> str:
    if isinstance(value, list) and value:
        return "; ".join(_summarize_item(item) for item in value[:5])
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _summarize_item(item: object) -> str:
    if isinstance(item, dict):
        parts: list[str] = []
        for key in ("id", "title", "description", "status", "evidence", "summary", "result"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
        return " - ".join(parts) if parts else str(item)
    return str(item)


def _format_deviations(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "None"
    return "; ".join(str(item) for item in value[:5])


def _file_record_exists(path: Path, candidate_path: str) -> bool:
    if not path.exists():
        return False
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            if isinstance(data, dict) and data.get("path") == candidate_path:
                return True
    except (OSError, json.JSONDecodeError):
        return False
    return False


def _active_run_id(project_root: Path) -> str | None:
    try:
        active = _read_json(project_root / ".logos" / "memory" / "active-work.json")
    except (OSError, json.JSONDecodeError):
        return None
    value = active.get("active_run_id")
    return value if isinstance(value, str) else None


def _verification_summary(data: dict[str, object]) -> str:
    passed = data.get("passed")
    criteria = data.get("success_criteria_status")
    gates = data.get("quality_gate_status")
    risk = data.get("remaining_risk")
    parts = [f"passed={passed}"]
    if isinstance(criteria, list):
        parts.append(f"success_criteria={len(criteria)}")
    if isinstance(gates, list):
        parts.append(f"quality_gates={len(gates)}")
    if isinstance(risk, list) and risk:
        parts.append(f"remaining_risk={len(risk)}")
    return ", ".join(parts)


def _paths_from_modified_file_review(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    paths: list[str] = []
    for item in value:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.append(str(item["path"]))
    return paths


def _normalize_touched_path(path: str) -> str:
    normalized = path.strip().strip("'\"").replace("\\", "/")
    if not normalized:
        return ""
    if normalized.startswith(".logos/") or normalized == ".logos":
        return ""
    if normalized.startswith("/"):
        return ""
    # Basename-only review entries are too ambiguous for run-level changed file state.
    if "/" not in normalized:
        return ""
    return normalized


def _normalize_test_record(item: dict[str, object]) -> dict[str, object]:
    status = str(item.get("status") or item.get("result") or "recorded")
    name = item.get("name") or item.get("scope")
    command = item.get("command")
    tests = item.get("tests")
    if command is None and isinstance(tests, list) and tests:
        command = ", ".join(str(test) for test in tests[:5])
    failed_count = _non_negative_int(item.get("failed_count"))
    passed_count = _non_negative_int(item.get("passed_count"))
    if failed_count == 0 and status.lower() in {"failed", "failure", "error"}:
        failed_count = 1
    summary = item.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        bits = []
        if isinstance(name, str) and name.strip():
            bits.append(name.strip())
        if isinstance(command, str) and command.strip():
            bits.append(command.strip())
        bits.append(status)
        summary = ": ".join(bits)
    return {
        "name": name if isinstance(name, str) else None,
        "command": command if isinstance(command, str) else None,
        "status": status,
        "summary": summary,
        "passed_count": passed_count,
        "failed_count": failed_count,
    }
