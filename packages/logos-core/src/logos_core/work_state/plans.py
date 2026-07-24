"""Durable task plan records."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logos_core.work_state.ids import new_plan_id
from logos_core.work_state.jsonl import write_json


def create_plan_record(
    *,
    user_request: str,
    title: str | None = None,
    steps: list[dict[str, Any]] | None = None,
    plan_id: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "plan_id": plan_id or new_plan_id(title or user_request),
        "title": title or user_request[:120],
        "user_request": user_request,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "steps": steps or [],
        "open_items": [],
        "blockers": [],
        "target_files": [],
    }


def write_active_plan(root: Path, plan: dict[str, Any]) -> None:
    plan_id = str(plan["plan_id"])
    write_json(root / ".logos" / "plans" / f"{plan_id}.json", plan)
    write_json(root / ".logos" / "plans" / "active-plan.json", plan)
