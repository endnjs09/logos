from __future__ import annotations

import json

from logos_runner.engine import (
    apply_stage_gate,
    record_stage_result,
    run_execute_stage,
    run_planning_sequence,
    run_verify_stage,
)
from logos_runner.cli import build_parser
from logos_runner.state.interview import merge_interview_draft
from logos_runner.state.store import PlanStore
from logos_runner.stages.registry import get_stage


def test_runner_prepares_prompt_then_records_stage_result(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Add board CRUD.")

    prepared = run_planning_sequence(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=False,
    )

    assert prepared.status == "prompt_ready"
    assert store.read_state(plan.plan_id)["current_stage"] == "scan"
    assert (plan.plan_dir / "stages" / "scan" / "prompt.md").exists()

    recorded = record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("scan"),
        raw_text=_json(
            {
                "schema_version": 1,
                "exploration_summary": "Spring service with existing auth package.",
                "files_read": ["src/main/java/example/AuthController.java"],
                "question_candidates": [],
                "blocking_unknowns": [],
                "next_step": "intake",
            }
        ),
    )
    advanced = apply_stage_gate(tmp_path, plan.plan_id, "scan")

    assert recorded.status == "result_ready"
    assert recorded.result_path == plan.plan_dir / "stages" / "scan" / "result.json"
    assert advanced.status == "next_prompt_ready"
    assert store.read_state(plan.plan_id)["current_stage"] == "intake"
    assert (plan.plan_dir / "stages" / "intake" / "prompt.md").exists()
    assert not (plan.plan_dir / "scan-result.json").exists()


def test_execute_and_verify_use_recorded_results_for_state_transition(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Update README.")
    _prepare_ready_for_execute(tmp_path, plan.plan_id)

    execution_prompt = run_execute_stage(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=False,
    )
    record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("execute"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan.plan_id,
                "status": "completed",
                "implemented_steps": ["Updated README title."],
                "modified_files": ["README.md"],
                "commands_run": [{"command": "inspect README", "exit_code": 0, "summary": "Inspected."}],
                "tests_run": [
                    {
                        "name": "README inspection",
                        "command": "inspect README",
                        "status": "passed",
                        "passed_count": 1,
                        "failed_count": 0,
                        "summary": "Inspection passed.",
                    }
                ],
                "verification_notes": ["No runtime change."],
                "deviations_from_plan": [],
                "next_step": "verify",
            }
        ),
    )
    execution_gate = apply_stage_gate(tmp_path, plan.plan_id, "execute")

    assert execution_prompt.status == "prompt_ready"
    assert execution_prompt.result_path == plan.plan_dir / "stages" / "execute" / "prompt.md"
    assert execution_gate.status == "ready_for_verify"
    assert store.read_state(plan.plan_id)["current_stage"] == "verify"
    assert (plan.plan_dir / "stages" / "execute" / "result.json").exists()
    assert (plan.plan_dir / "execution-result.json").exists()
    run_after_execute = store.read_run(plan.plan_id)
    assert run_after_execute is not None
    assert "Updated README title" in str(run_after_execute["execution_summary"])
    assert run_after_execute["touched_files"] == ["README.md"]
    assert run_after_execute["artifact_paths"]["scan_result"].endswith("/stages/scan/result.json")
    assert run_after_execute["artifact_paths"]["intake_result"].endswith("/stages/intake/result.json")
    assert run_after_execute["test_count"] == 1
    assert (tmp_path / ".logos/runs" / str(run_after_execute["run_id"]) / "tests.jsonl").exists()

    verification_prompt = run_verify_stage(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        timeout_seconds=None,
        dry_run=False,
    )
    record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("verify"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan.plan_id,
                "passed": True,
                "checked_files": ["README.md"],
                "commands_run": [{"command": "inspect README", "exit_code": 0, "summary": "Inspected."}],
                "tests_run": [
                    {
                        "name": "README inspection",
                        "command": "inspect README",
                        "status": "passed",
                        "passed_count": 1,
                        "failed_count": 0,
                        "summary": "Final inspection passed.",
                    }
                ],
                "success_criteria_status": [],
                "quality_gate_status": [],
                "modified_files_review": [],
                "remaining_risk": [],
                "findings": [],
                "next_step": "complete",
            }
        ),
    )
    verification_gate = apply_stage_gate(tmp_path, plan.plan_id, "verify")

    assert verification_prompt.status == "prompt_ready"
    assert verification_prompt.result_path == plan.plan_dir / "stages" / "verify" / "prompt.md"
    assert verification_gate.status == "verified"
    assert store.read_state(plan.plan_id)["status"] == "verified"
    assert store.read_state(plan.plan_id)["current_stage"] == "complete"
    run_after_verify = store.read_run(plan.plan_id)
    assert run_after_verify is not None
    assert run_after_verify["status"] == "completed"
    assert "passed=True" in str(run_after_verify["verification_summary"])


def test_run_state_filters_internal_and_ambiguous_touched_files(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Update auth.")

    store.merge_touched_files(
        plan.plan_id,
        [
            ".logos/plans/example/stages/scan/raw.md",
            "UserService.java",
            "src/main/java/example/UserService.java",
            {"path": "src/test/java/example/UserServiceTest.java"},
        ],
    )

    run = store.read_run(plan.plan_id)

    assert run is not None
    assert run["touched_files"] == [
        "src/main/java/example/UserService.java",
        "src/test/java/example/UserServiceTest.java",
    ]


def test_record_stage_rejects_invalid_json_and_removes_stale_result(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Add board CRUD.")
    stage = get_stage("scan")
    stale = plan.plan_dir / "scan-result.json"
    stale.write_text('{"schema_version": 1}\n', encoding="utf-8")

    recorded = record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=stage,
        raw_text='{"schema_version": 1, "exploration_summary": "broken"',
    )

    state = store.read_state(plan.plan_id)
    assert recorded.status == "failed"
    assert state["status"] == "failed"
    assert not stale.exists()
    assert (plan.plan_dir / "errors" / "scan-parse-error.json").exists()


def test_verify_gate_rejects_invalid_required_artifact(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Update README.")
    _prepare_ready_for_execute(tmp_path, plan.plan_id)
    (plan.plan_dir / "spec.json").write_text('{"schema_version": 1, "broken": "unterminated}', encoding="utf-8")

    record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("execute"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan.plan_id,
                "status": "completed",
                "implemented_steps": [],
                "modified_files": [],
                "commands_run": [],
                "tests_run": [],
                "verification_notes": [],
                "deviations_from_plan": [],
                "next_step": "verify",
            }
        ),
    )
    apply_stage_gate(tmp_path, plan.plan_id, "execute")
    record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("verify"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan.plan_id,
                "passed": True,
                "checked_files": [],
                "commands_run": [],
                "tests_run": [],
                "success_criteria_status": [],
                "quality_gate_status": [],
                "modified_files_review": [],
                "remaining_risk": [],
                "findings": [],
                "next_step": "complete",
            }
        ),
    )

    verification_gate = apply_stage_gate(tmp_path, plan.plan_id, "verify")

    assert verification_gate.status == "failed"
    assert "invalid JSON artifact spec.json" in verification_gate.message
    assert store.read_state(plan.plan_id)["status"] == "failed"


def test_cli_no_longer_exposes_complete_command() -> None:
    parser = build_parser()

    try:
        parser.parse_args(["complete", "plan_1", "verify"])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("complete command should not be available")


def test_cli_exposes_report_command() -> None:
    parser = build_parser()

    args = parser.parse_args(["report", "plan_1"])

    assert args.command == "report"


def test_interview_draft_clears_open_questions_when_intake_is_sufficient(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Add point top-up.")
    scan_result = store.stage_result_path(plan.plan_id, "scan")
    scan_result.parent.mkdir(parents=True, exist_ok=True)
    scan_result.write_text(
        _json(
            {
                "schema_version": 1,
                "interview_draft_update": {"open_questions": ["Which provider?"]},
            }
        ),
        encoding="utf-8",
    )
    intake_result = store.stage_result_path(plan.plan_id, "intake")
    intake_result.parent.mkdir(parents=True, exist_ok=True)
    intake_result.write_text(
        _json(
            {
                "schema_version": 1,
                "essential_information_status": "sufficient",
                "questions": [],
                "required_questions": [],
                "optional_questions": [],
                "blocking_unknowns": [],
                "interview_draft_update": {"open_questions": ["Amount conversion rule?"]},
            }
        ),
        encoding="utf-8",
    )
    (plan.plan_dir / "spec.json").write_text(
        _json(
            {
                "schema_version": 1,
                "blocking_open_questions": [],
                "structured_spec": {"open_questions": []},
            }
        ),
        encoding="utf-8",
    )

    path = merge_interview_draft(tmp_path, plan.plan_id)
    draft = json.loads(path.read_text(encoding="utf-8"))

    assert draft["open_questions"] == []


def test_completed_run_moves_deviations_out_of_last_error(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Update README.")
    _prepare_ready_for_execute(tmp_path, plan.plan_id)

    record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("execute"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan.plan_id,
                "status": "completed",
                "implemented_steps": ["Updated README."],
                "modified_files": ["README.md"],
                "commands_run": [],
                "tests_run": [],
                "verification_notes": [],
                "deviations_from_plan": ["README title stayed unchanged because it already matched."],
                "next_step": "verify",
            }
        ),
    )
    apply_stage_gate(tmp_path, plan.plan_id, "execute")
    record_stage_result(
        project_root=tmp_path,
        plan_id=plan.plan_id,
        stage=get_stage("verify"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan.plan_id,
                "passed": True,
                "checked_files": ["README.md"],
                "commands_run": [],
                "tests_run": [],
                "success_criteria_status": [],
                "quality_gate_status": [],
                "modified_files_review": [],
                "remaining_risk": [],
                "findings": [],
                "next_step": "complete",
            }
        ),
    )
    apply_stage_gate(tmp_path, plan.plan_id, "verify")

    run = store.read_run(plan.plan_id)

    assert run is not None
    assert run["status"] == "completed"
    assert run["last_error"] is None
    assert run["execution_deviations"] == ["README title stayed unchanged because it already matched."]


def test_interview_draft_keeps_questions_while_waiting_user(tmp_path) -> None:
    store = PlanStore(tmp_path)
    plan = store.create_plan("Add point top-up.")
    (plan.plan_dir / "intake-result.json").write_text(
        _json(
            {
                "schema_version": 1,
                "essential_information_status": "insufficient",
                "questions": [{"question": "Which provider?"}],
                "required_questions": [{"question": "Which provider?"}],
                "optional_questions": [],
                "blocking_unknowns": ["provider"],
            }
        ),
        encoding="utf-8",
    )
    store.mark_waiting_user(plan.plan_id, "intake", [{"question": "Which provider?"}], ["provider"])

    path = merge_interview_draft(tmp_path, plan.plan_id)
    draft = json.loads(path.read_text(encoding="utf-8"))

    assert draft["open_questions"] == ["Which provider?"]


def _prepare_ready_for_execute(project_root, plan_id: str) -> None:
    scan = get_stage("scan")
    record_stage_result(
        project_root=project_root,
        plan_id=plan_id,
        stage=scan,
        raw_text=_json(
            {
                "schema_version": 1,
                "exploration_summary": "README-only change.",
                "files_read": ["README.md"],
                "question_candidates": [],
                "blocking_unknowns": [],
                "next_step": "intake",
            }
        ),
    )
    apply_stage_gate(project_root, plan_id, "scan")

    record_stage_result(
        project_root=project_root,
        plan_id=plan_id,
        stage=get_stage("intake"),
        raw_text=_json(
            {
                "schema_version": 1,
                "intake_summary": "Request is clear.",
                "essential_information_status": "sufficient",
                "complexity": "low",
                "questions": [],
                "required_questions": [],
                "optional_questions": [],
                "blocking_unknowns": [],
                "next_step": "spec",
            }
        ),
    )
    apply_stage_gate(project_root, plan_id, "intake")

    record_stage_result(
        project_root=project_root,
        plan_id=plan_id,
        stage=get_stage("spec"),
        raw_text=_json(
            {
                "schema_version": 1,
                "complexity": "low",
                "spec_type": "one_line_plan",
                "blocking_open_questions": [],
                "next_step": "task_plan",
            }
        ),
    )
    apply_stage_gate(project_root, plan_id, "spec")

    record_stage_result(
        project_root=project_root,
        plan_id=plan_id,
        stage=get_stage("plan"),
        raw_text=_json(
            {
                "schema_version": 1,
                "plan_id": plan_id,
                "goal": "Update README.",
                "target_files": ["README.md"],
                "steps": [{"id": "step-1", "description": "Update README."}],
                "verification_plan": ["Inspect README diff."],
                "context_handoff": {
                    "schema_version": 1,
                    "apply": False,
                    "handoff_to": [],
                    "reason": "Small change.",
                    "required_fields": [],
                    "payload": {},
                    "missing_required_fields": [],
                },
                "next_step": "executor",
            }
        ),
    )
    apply_stage_gate(project_root, plan_id, "plan")

    record_stage_result(
        project_root=project_root,
        plan_id=plan_id,
        stage=get_stage("review_lite"),
        raw_text=_json({"schema_version": 1, "passed": True, "findings": [], "next_step": "executor"}),
    )
    apply_stage_gate(project_root, plan_id, "review_lite")


def _json(data: dict[str, object]) -> str:
    return json.dumps(data, ensure_ascii=False)
