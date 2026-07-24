from __future__ import annotations

from logos_runner.engine import run_execute_stage, run_planning_sequence, run_verify_stage
from logos_runner.state.store import PlanStore


def test_verify_dry_run_completes_plan(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("README 제목을 바꿔줘")

    planning = run_planning_sequence(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=True,
    )
    execution = run_execute_stage(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=True,
    )
    verification = run_verify_stage(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=True,
    )
    state = store.read_state(plan.plan_id)
    result = store.read_stage_result(plan.plan_id, "verification-result.json")

    assert planning.status == "ready_for_execute"
    assert execution.status == "ready_for_verify"
    assert verification.status == "verified"
    assert state["status"] == "verified"
    assert state["current_stage"] == "complete"
    assert "verify" in state["completed_stages"]
    assert result["plan_id"] == plan.plan_id
    assert result["passed"] is True
    assert result["next_step"] == "complete"

