"""Raw evidence records."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logos_core.work_state.jsonl import append_jsonl


def record_hook_event(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    append_jsonl(root / ".logos" / "evidence" / "hook-events.jsonl", event)
    return event
