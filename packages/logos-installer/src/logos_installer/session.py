"""Installer-facing Nous Mode session commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from logos_core.session.state import (
    activate_nous,
    deactivate_nous,
    read_or_default_session_state,
)


def set_nous_mode(root: Path, enabled: bool, *, source: str) -> dict[str, Any]:
    if enabled:
        return activate_nous(root, activated_by=source)
    return deactivate_nous(root, activated_by=source)


def read_session_state(root: Path) -> dict[str, Any]:
    return read_or_default_session_state(root)
