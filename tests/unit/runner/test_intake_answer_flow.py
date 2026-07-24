from __future__ import annotations

from logos_runner.engine import run_planning_sequence
from logos_runner.state.interview import merge_interview_draft
from logos_runner.state.store import PlanStore


def test_intake_answer_flow_dry_run(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("게시판 기능 구현해줘")

    waiting = run_planning_sequence(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=True,
        simulate_intake_missing=True,
    )
    waiting_state = store.read_state(plan.plan_id)

    assert waiting.status == "waiting_user"
    assert waiting_state["status"] == "waiting_user"
    assert waiting_state["current_stage"] == "intake"
    assert waiting_state["pending_questions"]

    store.append_user_answer(
        plan.plan_id,
        "게시판은 CRUD, 목록, 상세, 검색, 페이징만 포함합니다.",
    )
    draft_path = merge_interview_draft(tmp_path, plan.plan_id)

    resumed = run_planning_sequence(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        from_stage="intake",
        timeout_seconds=None,
        dry_run=True,
    )
    final_state = store.read_state(plan.plan_id)

    assert draft_path.exists()
    assert resumed.status == "ready_for_execute"
    assert final_state["status"] == "ready_for_execute"
    assert "pending_questions" not in final_state
    assert (plan.plan_dir / "user-answers.jsonl").exists()

