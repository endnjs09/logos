"""Small resume-oriented memory files.

These files are intentionally compact. Agents should read these before raw run
or evidence logs when continuing after context loss.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logos_core.work_state.jsonl import read_json, write_json


def initialize_memory_state(root: Path) -> None:
    memory = root / ".logos" / "memory"
    memory.mkdir(parents=True, exist_ok=True)
    write_json_if_missing(
        memory / "active-work.json",
        {
            "schema_version": 1,
            "status": "idle",
            "active_plan_id": None,
            "active_run_id": None,
            "updated_at": _now(),
        },
    )
    write_json_if_missing(
        memory / "run-index.json",
        {"schema_version": 1, "runs": [], "updated_at": _now()},
    )
    write_json_if_missing(
        memory / "open-items.json",
        {"schema_version": 1, "items": [], "updated_at": _now()},
    )
    snapshot = memory / "resume-snapshot.md"
    if not snapshot.exists():
        snapshot.write_text(
            "# Logos Resume Snapshot\n\n"
            "Status: idle\n\n"
            "No active Logos work has been recorded yet.\n",
            encoding="utf-8",
        )


def add_run_index_entry(root: Path, run: dict[str, Any]) -> None:
    initialize_memory_state(root)
    path = root / ".logos" / "memory" / "run-index.json"
    index = read_json(path) or {"schema_version": 1, "runs": []}
    runs = index.setdefault("runs", [])
    if isinstance(runs, list):
        runs[:] = [
            item for item in runs if not isinstance(item, dict) or item.get("run_id") != run["run_id"]
        ]
        runs.append(
            {
                "run_id": run["run_id"],
                "plan_id": run.get("plan_id"),
                "status": run.get("status"),
                "started_at": run.get("started_at"),
                "summary": run.get("summary", ""),
                "touched_files": run.get("touched_files", []),
            }
        )
        del runs[:-25]
    index["updated_at"] = _now()
    write_json(path, index)

    active = read_json(root / ".logos" / "memory" / "active-work.json") or {}
    active.update(
        {
            "schema_version": 1,
            "status": "active",
            "active_plan_id": run.get("plan_id"),
            "active_run_id": run.get("run_id"),
            "updated_at": _now(),
        }
    )
    write_json(root / ".logos" / "memory" / "active-work.json", active)


def update_resume_snapshot(
    root: Path,
    *,
    current_task: str | None = None,
    completed: list[str] | None = None,
    in_progress: list[str] | None = None,
    remaining: list[str] | None = None,
    touched_files: list[str] | None = None,
    blockers: list[str] | None = None,
    last_run_id: str | None = None,
) -> None:
    initialize_memory_state(root)
    lines = [
        "# Logos Resume Snapshot",
        "",
        "Read this file only when continuing after context loss, compaction, or an unclear",
        "work state. Do not scan raw `.logos/runs` or `.logos/evidence` first.",
        "",
        f"Updated: {_now()}",
        f"Current task: {current_task or 'None'}",
        f"Last run id: {last_run_id or 'None'}",
        "",
    ]
    lines.extend(_section("Completed", completed or []))
    lines.extend(_section("In Progress", in_progress or []))
    lines.extend(_section("Remaining", remaining or []))
    lines.extend(_section("Touched Files", touched_files or []))
    lines.extend(_section("Blockers", blockers or []))
    (root / ".logos" / "memory" / "resume-snapshot.md").write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def write_json_if_missing(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        return
    write_json(path, payload)


def _section(title: str, items: list[str]) -> list[str]:
    lines = [f"## {title}"]
    if not items:
        lines.append("- None")
    else:
        lines.extend(f"- {item}" for item in items[:20])
    lines.append("")
    return lines


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
