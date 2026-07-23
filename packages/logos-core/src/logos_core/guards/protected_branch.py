"""Protected branch guard."""

from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path

from logos_core.guards.dangerous_command import normalize_command, strip_git_global_options
from logos_core.guards.decision import GuardDecision, allow, ask, block
from logos_core.guards.events import GuardEvent

GUARD_ID = "logos.guard.protected-branch-guard"
PROTECTED_BRANCHES = ("main", "master", "production", "release/*")

READ_ONLY_GIT = re.compile(r"^git\s+(?:status|diff|log|show|rev-parse|branch\s+--show-current)\b")
BLOCK_GIT = re.compile(
    r"\bgit\s+(?:push\b.*\s(?:--force|-f|--force-with-lease)|reset\s+--hard|clean\s+-[A-Za-z]*[fxd][A-Za-z]*|branch\s+-D)\b"
)
ASK_GIT = re.compile(r"\bgit\s+(?:add|commit|push|merge|rebase|tag|checkout|switch|branch)\b")


def evaluate(event: GuardEvent, *, branch: str | None = None) -> GuardDecision:
    if not event.command:
        return allow(GUARD_ID, "no shell command found")
    normalized = strip_git_global_options(normalize_command(event.command))
    if not normalized.startswith("git "):
        return allow(GUARD_ID, "not a git command")
    if READ_ONLY_GIT.search(normalized):
        return allow(GUARD_ID, "read-only git command")

    current_branch = branch if branch is not None else detect_branch(event.cwd)
    if current_branch is None:
        if BLOCK_GIT.search(normalized):
            return block(
                GUARD_ID,
                "dangerous git command with unknown branch",
                matched=[event.command],
                evidence={"branch": "unknown"},
            )
        if ASK_GIT.search(normalized):
            return ask(
                GUARD_ID,
                "git state change with unknown branch",
                matched=[event.command],
                evidence={"branch": "unknown"},
            )
        return allow(GUARD_ID, "git command does not mutate protected state")

    if not is_protected_branch(current_branch):
        return allow(GUARD_ID, "current branch is not protected")
    if BLOCK_GIT.search(normalized):
        return block(
            GUARD_ID,
            "dangerous git command on protected branch",
            matched=[event.command],
            evidence={"branch": current_branch},
        )
    if ASK_GIT.search(normalized):
        return ask(
            GUARD_ID,
            "git state change on protected branch",
            matched=[event.command],
            evidence={"branch": current_branch},
        )
    return allow(GUARD_ID, "git command allowed on protected branch")


def is_protected_branch(branch: str) -> bool:
    return any(fnmatch.fnmatch(branch, pattern) for pattern in PROTECTED_BRANCHES)


def detect_branch(cwd: str) -> str | None:
    if not cwd:
        return None
    path = Path(cwd)
    if not path.exists():
        return None
    try:
        completed = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=path,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    branch = completed.stdout.strip()
    return branch or None
