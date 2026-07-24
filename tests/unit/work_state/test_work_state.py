import json
from pathlib import Path

from logos_core.work_state.memory import initialize_memory_state, update_resume_snapshot
from logos_core.work_state.plans import create_plan_record, write_active_plan
from logos_core.work_state.runs import create_run, record_command, record_file_change, record_guard


def test_initialize_memory_state_creates_resume_files(tmp_path: Path) -> None:
    initialize_memory_state(tmp_path)

    assert (tmp_path / ".logos/memory/active-work.json").exists()
    assert (tmp_path / ".logos/memory/run-index.json").exists()
    assert (tmp_path / ".logos/memory/open-items.json").exists()
    assert (tmp_path / ".logos/memory/resume-snapshot.md").exists()

    active = json.loads((tmp_path / ".logos/memory/active-work.json").read_text())
    assert active["status"] == "idle"
    assert active["active_run_id"] is None


def test_run_records_update_index_and_jsonl(tmp_path: Path) -> None:
    run = create_run(tmp_path, user_request="로그인 기능 구현해줘")

    record_command(tmp_path, command="pytest", cwd=str(tmp_path), tool_name="Bash")
    record_file_change(tmp_path, path="src/auth/login.py", change_type="modified")
    record_guard(
        tmp_path,
        guard_id="logos.guard.dangerous-command-denylist",
        decision="ask",
        reason="git state change",
    )

    run_json = json.loads(
        (tmp_path / ".logos/runs" / run["run_id"] / "run.json").read_text(encoding="utf-8")
    )
    assert run_json["command_count"] == 1
    assert run_json["guard_decision_count"] == 1
    assert run_json["touched_files"] == ["src/auth/login.py"]
    assert (tmp_path / ".logos/runs" / run["run_id"] / "commands.jsonl").exists()
    assert (tmp_path / ".logos/runs" / run["run_id"] / "files.jsonl").exists()
    assert (tmp_path / ".logos/runs" / run["run_id"] / "guards.jsonl").exists()

    index = json.loads((tmp_path / ".logos/memory/run-index.json").read_text())
    assert index["runs"][0]["run_id"] == run["run_id"]


def test_plan_record_and_resume_snapshot(tmp_path: Path) -> None:
    plan = create_plan_record(
        user_request="로그인 기능 구현해줘",
        steps=[{"id": "P1", "title": "Explore auth", "status": "pending"}],
    )
    write_active_plan(tmp_path, plan)
    update_resume_snapshot(
        tmp_path,
        current_task="로그인 기능 구현",
        completed=["인증 구조 확인"],
        remaining=["로그인 API 구현"],
        touched_files=["src/auth/login.py"],
        last_run_id="run-1",
    )

    assert (tmp_path / ".logos/plans/active-plan.json").exists()
    snapshot = (tmp_path / ".logos/memory/resume-snapshot.md").read_text(encoding="utf-8")
    assert "로그인 기능 구현" in snapshot
    assert "src/auth/login.py" in snapshot
