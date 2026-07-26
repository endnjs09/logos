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


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


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

    def mark_ready_for_verify(self, plan_id: str) -> None:
        state = self.read_state(plan_id)
        state["status"] = "ready_for_verify"
        state["current_stage"] = "verify"
        state["updated_at"] = _now()
        _clear_waiting_fields(state)
        _write_json(self.plan_dir(plan_id) / "plan-state.json", state)

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
            "touched_files": [],
            "command_count": 0,
            "guard_decision_count": 0,
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
            runs[:] = [
                item for item in runs if not isinstance(item, dict) or item.get("run_id") != run.get("run_id")
            ]
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
        lines = [
            "# Logos Resume Snapshot",
            "",
            "Read this file only when continuing after context loss, compaction, or an unclear work state.",
            "Do not scan raw `.logos/runs` or `.logos/evidence` first.",
            "",
            f"Updated: {_now()}",
            f"Current task: {run.get('summary') or 'Active Logos work'}",
            f"Last run id: {run.get('run_id')}",
            f"Active plan id: {run.get('plan_id')}",
            "",
            "## Touched Files",
        ]
        lines.extend([f"- {item}" for item in touched[:20]] or ["- None"])
        lines.extend(
            [
                "",
                "## Where To Look Next",
                "- .logos/memory/active-work.json",
                "- .logos/memory/run-index.json",
            ]
        )
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
