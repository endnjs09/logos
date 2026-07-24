from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from logos_runner.errors import LogosRunnerError
from logos_runner.state.store import PlanStore


@dataclass(frozen=True)
class ExecutionGateResult:
    ok: bool
    reason: str | None = None


def check_execution_gate(project_root: Path, plan_id: str) -> ExecutionGateResult:
    store = PlanStore(project_root)
    state = store.read_state(plan_id)
    plan_dir = store.plan_dir(plan_id)

    if state.get("status") != "ready_for_execute":
        return ExecutionGateResult(False, "plan is not ready for execute")

    task_plan_path = plan_dir / "task-plan.json"
    if not task_plan_path.exists():
        return ExecutionGateResult(False, "task-plan.json is missing")

    review_path = plan_dir / "review-lite.json"
    if not review_path.exists():
        return ExecutionGateResult(False, "review-lite.json is missing")

    try:
        task_plan = store.read_stage_result(plan_id, "task-plan.json")
        review = store.read_stage_result(plan_id, "review-lite.json")
    except (OSError, ValueError) as exc:
        return ExecutionGateResult(False, f"failed to read execution inputs: {exc}")

    if task_plan.get("next_step") != "executor":
        return ExecutionGateResult(False, "task plan next_step is not executor")

    blocking = task_plan.get("blocking_open_questions")
    if isinstance(blocking, list) and blocking:
        return ExecutionGateResult(False, "task plan has blocking open questions")

    review_lite = task_plan.get("review_lite")
    if isinstance(review_lite, dict) and review_lite.get("passed") is not True:
        return ExecutionGateResult(False, "task plan embedded review-lite did not pass")

    if review.get("passed") is not True:
        return ExecutionGateResult(False, "review-lite did not pass")

    if review.get("next_step") != "executor":
        return ExecutionGateResult(False, "review-lite next_step is not executor")

    return ExecutionGateResult(True)


def require_execution_gate(project_root: Path, plan_id: str) -> None:
    result = check_execution_gate(project_root, plan_id)
    if not result.ok:
        raise LogosRunnerError(result.reason or "execution gate failed")

