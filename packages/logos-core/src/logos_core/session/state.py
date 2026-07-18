"""Nous Mode session state model and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SESSION_STATE_VERSION = 1
SESSION_PATH = Path(".logos/session/nous-state.json")


@dataclass(frozen=True)
class SessionValidationIssue:
    message: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_session_state(
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
    now: str | None = None,
) -> dict[str, Any]:
    timestamp = now or utc_now()
    return {
        "schema_version": SESSION_STATE_VERSION,
        "nous_mode": False,
        "activated_at": None,
        "activated_by": None,
        "last_updated_at": timestamp,
        "target": target,
        "profile": profile,
    }


def read_session_state(root: Path) -> dict[str, Any]:
    path = root / SESSION_PATH
    if not path.exists():
        return default_session_state()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("Session state must be a JSON object.")
    return loaded


def write_session_state(root: Path, state: dict[str, Any]) -> None:
    path = root / SESSION_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def init_session_state(
    root: Path,
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
) -> dict[str, Any]:
    state = default_session_state(target=target, profile=profile)
    write_session_state(root, state)
    return state


def activate_nous(root: Path, *, activated_by: str = "logos nous on") -> dict[str, Any]:
    state = read_or_default_session_state(root)
    now = utc_now()
    state.update(
        {
            "schema_version": SESSION_STATE_VERSION,
            "nous_mode": True,
            "activated_at": now,
            "activated_by": activated_by,
            "last_updated_at": now,
            "target": state.get("target") or "gemini-cli",
            "profile": state.get("profile") or "gemini",
        }
    )
    write_session_state(root, state)
    return state


def deactivate_nous(root: Path, *, activated_by: str = "logos nous off") -> dict[str, Any]:
    state = read_or_default_session_state(root)
    state.update(
        {
            "schema_version": SESSION_STATE_VERSION,
            "nous_mode": False,
            "activated_at": None,
            "activated_by": activated_by,
            "last_updated_at": utc_now(),
            "target": state.get("target") or "gemini-cli",
            "profile": state.get("profile") or "gemini",
        }
    )
    write_session_state(root, state)
    return state


def is_nous_active(root: Path) -> bool:
    return bool(read_or_default_session_state(root).get("nous_mode"))


def read_or_default_session_state(root: Path) -> dict[str, Any]:
    try:
        loaded = read_session_state(root)
    except (json.JSONDecodeError, ValueError):
        return default_session_state()
    state = default_session_state()
    state.update(loaded)
    return normalize_legacy_state(state)


def normalize_legacy_state(state: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(state)
    if "schema_version" not in normalized:
        normalized["schema_version"] = SESSION_STATE_VERSION
    if "activated_by" not in normalized and "activation_source" in normalized:
        normalized["activated_by"] = normalized.get("activation_source")
    normalized.pop("activation_source", None)
    normalized.pop("notes", None)
    normalized.setdefault("last_updated_at", utc_now())
    normalized.setdefault("target", "gemini-cli")
    normalized.setdefault("profile", "gemini")
    return normalized


def validate_session_state_payload(value: object) -> list[SessionValidationIssue]:
    issues: list[SessionValidationIssue] = []
    if not isinstance(value, dict):
        return [SessionValidationIssue("Session state must be a JSON object.")]

    if value.get("schema_version") != SESSION_STATE_VERSION:
        issues.append(
            SessionValidationIssue(
                f"Session state requires schema_version {SESSION_STATE_VERSION}."
            )
        )
    if not isinstance(value.get("nous_mode"), bool):
        issues.append(SessionValidationIssue("Session state requires boolean nous_mode."))

    for field in ("target", "profile"):
        if not isinstance(value.get(field), str) or not value.get(field):
            issues.append(SessionValidationIssue(f"Session state requires string {field}."))

    if not is_nullable_string(value.get("activated_by")):
        issues.append(SessionValidationIssue("Session state activated_by must be null or string."))
    if not is_nullable_iso_datetime(value.get("activated_at")):
        issues.append(
            SessionValidationIssue("Session state activated_at must be null or ISO datetime.")
        )
    if not is_iso_datetime(value.get("last_updated_at")):
        issues.append(SessionValidationIssue("Session state requires ISO datetime last_updated_at."))

    return issues


def is_nullable_string(value: object) -> bool:
    return value is None or isinstance(value, str)


def is_nullable_iso_datetime(value: object) -> bool:
    return value is None or is_iso_datetime(value)


def is_iso_datetime(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True
