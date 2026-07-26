"""Run and evidence records for Logos work-state."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logos_core.work_state.ids import new_run_id
from logos_core.work_state.jsonl import append_jsonl, read_json, write_json
from logos_core.work_state.memory import add_run_index_entry


def create_run(
    root: Path,
    *,
    selected_mode: str = "nous",
    plan_id: str | None = None,
    user_request: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    resolved_run_id = run_id or new_run_id()
    run = {
        "schema_version": 1,
        "run_id": resolved_run_id,
        "plan_id": plan_id,
        "selected_mode": selected_mode,
        "status": "active",
        "started_at": _now(),
        "ended_at": None,
        "user_request": user_request,
        "summary": "",
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
        "artifact_paths": artifact_paths(plan_id),
    }
    write_json(_run_dir(root, str(run["run_id"])) / "run.json", run)
    add_run_index_entry(root, run)
    return run


def ensure_current_run(root: Path) -> dict[str, Any]:
    active = read_json(root / ".logos" / "memory" / "active-work.json") or {}
    active_run_id = active.get("active_run_id")
    if isinstance(active_run_id, str):
        run = read_json(_run_dir(root, active_run_id) / "run.json")
        if run is not None:
            return run
    return create_run(root)


def record_command(
    root: Path,
    *,
    command: str,
    cwd: str | None = None,
    tool_name: str | None = None,
    summary: str | None = None,
    exit_code: int | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    run = _resolve_run(root, run_id)
    record = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "recorded_at": _now(),
        "command": command,
        "cwd": cwd,
        "tool_name": tool_name,
        "exit_code": exit_code,
        "summary": summary or command[:240],
    }
    append_jsonl(_run_dir(root, str(run["run_id"])) / "commands.jsonl", record)
    run["command_count"] = int(run.get("command_count", 0)) + 1
    run["last_command"] = command
    if exit_code not in (None, 0):
        run["last_error"] = summary or f"command exited with {exit_code}"
    write_json(_run_dir(root, str(run["run_id"])) / "run.json", run)
    return record


def record_file_change(
    root: Path,
    *,
    path: str,
    change_type: str = "modified",
    detected_by: str = "git-status",
    run_id: str | None = None,
) -> dict[str, Any]:
    run = _resolve_run(root, run_id)
    normalized_path = normalize_touched_path(path)
    if not normalized_path:
        return {}
    record = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "recorded_at": _now(),
        "path": normalized_path,
        "change_type": change_type,
        "detected_by": detected_by,
    }
    append_jsonl(_run_dir(root, str(run["run_id"])) / "files.jsonl", record)
    touched = run.setdefault("touched_files", [])
    if isinstance(touched, list) and normalized_path not in touched:
        touched.append(normalized_path)
    write_json(_run_dir(root, str(run["run_id"])) / "run.json", run)
    return record


def record_guard(
    root: Path,
    *,
    guard_id: str,
    decision: str,
    reason: str,
    target: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    run = _resolve_run(root, run_id)
    record = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "recorded_at": _now(),
        "guard_id": guard_id,
        "decision": decision,
        "reason": reason,
        "target": target,
    }
    append_jsonl(_run_dir(root, str(run["run_id"])) / "guards.jsonl", record)
    run["guard_decision_count"] = int(run.get("guard_decision_count", 0)) + 1
    write_json(_run_dir(root, str(run["run_id"])) / "run.json", run)
    return record


def record_test_result(
    root: Path,
    *,
    name: str | None = None,
    command: str | None = None,
    status: str,
    summary: str | None = None,
    passed_count: int | None = None,
    failed_count: int | None = None,
    detected_by: str = "runner-stage-artifact",
    run_id: str | None = None,
) -> dict[str, Any]:
    run = _resolve_run(root, run_id)
    normalized_failed_count = max(failed_count or 0, 0)
    record = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "recorded_at": _now(),
        "name": name,
        "command": command,
        "status": status,
        "summary": summary or status,
        "passed_count": max(passed_count or 0, 0),
        "failed_count": normalized_failed_count,
        "detected_by": detected_by,
    }
    append_jsonl(_run_dir(root, str(run["run_id"])) / "tests.jsonl", record)
    run["test_count"] = int(run.get("test_count", 0)) + 1
    run["failed_test_count"] = int(run.get("failed_test_count", 0)) + normalized_failed_count
    run["test_summary"] = summarize_tests(run, record)
    write_json(_run_dir(root, str(run["run_id"])) / "run.json", run)
    return record


def _resolve_run(root: Path, run_id: str | None) -> dict[str, Any]:
    if run_id:
        existing = read_json(_run_dir(root, run_id) / "run.json")
        return existing or create_run(root, run_id=run_id)
    return ensure_current_run(root)


def _run_dir(root: Path, run_id: str) -> Path:
    return root / ".logos" / "runs" / run_id


def artifact_paths(plan_id: str | None) -> dict[str, str]:
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


def summarize_tests(run: dict[str, Any], latest: dict[str, Any]) -> str:
    status = latest.get("status") or "recorded"
    summary = latest.get("summary") or ""
    count = int(run.get("test_count", 0))
    failed = int(run.get("failed_test_count", 0))
    if failed:
        return f"{count} test record(s); {failed} failed. Latest: {status}. {summary}".strip()
    return f"{count} test record(s), all recorded as passing or non-failing. Latest: {status}. {summary}".strip()


def normalize_touched_path(path: str) -> str:
    normalized = path.strip().strip("'\"").replace("\\", "/")
    if not normalized:
        return ""
    if normalized.startswith(".logos/") or normalized == ".logos":
        return ""
    if normalized.startswith("/"):
        return ""
    if "/" not in normalized:
        return ""
    return normalized


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
