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
    run = {
        "schema_version": 1,
        "run_id": run_id or new_run_id(),
        "plan_id": plan_id,
        "selected_mode": selected_mode,
        "status": "active",
        "started_at": _now(),
        "ended_at": None,
        "user_request": user_request,
        "summary": "",
        "touched_files": [],
        "command_count": 0,
        "guard_decision_count": 0,
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
    record = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "recorded_at": _now(),
        "path": path,
        "change_type": change_type,
        "detected_by": detected_by,
    }
    append_jsonl(_run_dir(root, str(run["run_id"])) / "files.jsonl", record)
    touched = run.setdefault("touched_files", [])
    if isinstance(touched, list) and path not in touched:
        touched.append(path)
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


def _resolve_run(root: Path, run_id: str | None) -> dict[str, Any]:
    if run_id:
        existing = read_json(_run_dir(root, run_id) / "run.json")
        return existing or create_run(root, run_id=run_id)
    return ensure_current_run(root)


def _run_dir(root: Path, run_id: str) -> Path:
    return root / ".logos" / "runs" / run_id


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
