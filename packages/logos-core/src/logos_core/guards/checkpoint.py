"""Working-tree checkpoint metadata helpers."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class WorkingTreeCheckpoint:
    schema_version: int
    recorded_at: str
    cwd: str
    reason: str
    head: str | None
    branch: str | None
    status_short: str
    dirty: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "recorded_at": self.recorded_at,
            "cwd": self.cwd,
            "reason": self.reason,
            "head": self.head,
            "branch": self.branch,
            "status_short": self.status_short,
            "dirty": self.dirty,
        }


def capture_checkpoint(cwd: Path, reason: str) -> WorkingTreeCheckpoint:
    status = git_output(cwd, ["status", "--short"]) or ""
    return WorkingTreeCheckpoint(
        schema_version=1,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        cwd=str(cwd),
        reason=reason,
        head=git_output(cwd, ["rev-parse", "HEAD"]),
        branch=git_output(cwd, ["branch", "--show-current"]),
        status_short=status,
        dirty=bool(status.strip()),
    )


def git_output(cwd: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()
