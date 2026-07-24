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
                "created_at": created_at,
                "updated_at": created_at,
                "completed_stages": [],
            },
        )
        return CreatedPlan(plan_id=plan_id, plan_dir=plan_dir)

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


def _next_stage_name(stage_name: str) -> str | None:
    names = [stage.name for stage in STAGE_REGISTRY]
    try:
        index = names.index(stage_name)
    except ValueError:
        return None
    next_index = index + 1
    return names[next_index] if next_index < len(names) else None


def _clear_waiting_fields(state: dict[str, object]) -> None:
    state.pop("pending_questions", None)
    state.pop("blocking_unknowns", None)
    state.pop("waiting_since", None)
    state.pop("answered", None)
