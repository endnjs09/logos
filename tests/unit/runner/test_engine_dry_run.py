from __future__ import annotations

from logos_runner.engine import run_planning_sequence
from logos_runner.state.store import PlanStore


def test_run_planning_sequence_dry_run_reaches_execute(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("게시판 기능 구현해줘")

    result = run_planning_sequence(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=True,
    )

    state = store.read_state(plan.plan_id)

    assert result.status == "ready_for_execute"
    assert result.completed_stages == ("scan", "intake", "spec", "plan", "review_lite")
    assert state["status"] == "ready_for_execute"
    assert state["current_stage"] == "execute"
    assert (plan.plan_dir / "scan-result.json").exists()
    assert (plan.plan_dir / "intake-result.json").exists()
    assert (plan.plan_dir / "spec.json").exists()
    assert (plan.plan_dir / "task-plan.json").exists()
    assert (plan.plan_dir / "review-lite.json").exists()

