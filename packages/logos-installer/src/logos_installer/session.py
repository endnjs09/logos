"""Nous mode session state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SESSION_PATH = Path(".logos/session/nous-state.json")


def default_session_state() -> dict[str, Any]:
    return {
        "nous_mode": False,
        "target": "gemini-cli",
        "profile": "default",
        "activated_at": None,
        "activation_source": None,
        "notes": [],
    }


def read_session_state(root: Path) -> dict[str, Any]:
    path = root / SESSION_PATH
    if not path.exists():
        return default_session_state()
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_session_state()
    if not isinstance(loaded, dict):
        return default_session_state()
    state = default_session_state()
    state.update(loaded)
    return state


def write_session_state(root: Path, state: dict[str, Any]) -> None:
    path = root / SESSION_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def set_nous_mode(root: Path, enabled: bool, *, source: str) -> dict[str, Any]:
    state = read_session_state(root)
    state["nous_mode"] = enabled
    state["target"] = state.get("target") or "gemini-cli"
    state["profile"] = state.get("profile") or "default"
    state["activation_source"] = source
    state["activated_at"] = datetime.now(timezone.utc).isoformat() if enabled else None
    write_session_state(root, state)
    return state
