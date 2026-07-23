"""Dangerous command denylist guard."""

from __future__ import annotations

import re
import shlex

from logos_core.guards.decision import GuardDecision, allow, ask, block
from logos_core.guards.events import GuardEvent

GUARD_ID = "logos.guard.dangerous-command-denylist"

READ_ONLY_PATTERNS = [
    re.compile(r"^git\s+(?:status|diff|log|show|rev-parse)\b"),
    re.compile(r"^git\s+branch\s+--show-current\b"),
    re.compile(r"^(?:pwd|ls|dir|rg)\b"),
]

SEGMENT_SPLIT_PATTERN = re.compile(r"\s*(?:&&|\|\||[;|])\s*")

BLOCK_PATTERNS = [
    (re.compile(r"\brm\s+-[A-Za-z]*r[A-Za-z]*f\b"), "recursive forced delete"),
    (re.compile(r"\brm\s+-rf\s+(?:/|\.git|\.)(?:\s|$)"), "dangerous rm target"),
    (re.compile(r"\brmdir\s+/s\b", re.IGNORECASE), "recursive directory delete"),
    (re.compile(r"\brd\s+/s\b", re.IGNORECASE), "recursive directory delete"),
    (re.compile(r"\bdel\s+/[fqsa]+\b", re.IGNORECASE), "forced Windows delete"),
    (
        re.compile(r"\bRemove-Item\b(?=.*\b-Recurse\b)(?=.*\b-Force\b)", re.IGNORECASE),
        "forced recursive PowerShell delete",
    ),
    (re.compile(r"\bgit\s+push\b.*\s(?:--force|-f|--force-with-lease)\b"), "force push"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "hard git reset"),
    (re.compile(r"\bgit\s+clean\s+-[A-Za-z]*[fxd][A-Za-z]*\b"), "destructive git clean"),
    (re.compile(r"\bgit\s+(?:checkout|restore)\s+--?\s+\.\b"), "bulk checkout or restore"),
    (re.compile(r"\bgit\s+branch\s+-D\b"), "forced branch deletion"),
    (
        re.compile(
            r"\b(?:curl|wget)\b.+\|\s*(?:sh|bash|pwsh|powershell|python|python3)\b",
            re.IGNORECASE,
        ),
        "remote script execution",
    ),
    (re.compile(r"\bInvoke-WebRequest\b.+\|\s*iex\b", re.IGNORECASE), "remote PowerShell execution"),
    (re.compile(r"\bterraform\s+destroy\b"), "terraform destroy"),
    (re.compile(r"\bkubectl\s+delete\b"), "kubernetes delete"),
    (re.compile(r"\bdocker\s+system\s+prune\b.*\s-a\b"), "docker system prune all"),
]

ASK_PATTERNS = [
    (re.compile(r"\bgit\s+(?:add|commit|push|merge|rebase|tag)\b"), "git state change"),
    (re.compile(r"\bgit\s+(?:checkout|switch|branch)\b"), "git branch or checkout change"),
]

DEPENDENCY_ACTIONS = {
    "npm": {
        "install": "JavaScript dependency install",
        "i": "JavaScript dependency install",
        "add": "JavaScript dependency add",
        "remove": "JavaScript dependency remove",
        "uninstall": "JavaScript dependency remove",
        "update": "JavaScript dependency update",
        "upgrade": "JavaScript dependency upgrade",
        "ci": "JavaScript lockfile install",
    },
    "pnpm": {
        "install": "JavaScript dependency install",
        "i": "JavaScript dependency install",
        "add": "JavaScript dependency add",
        "remove": "JavaScript dependency remove",
        "update": "JavaScript dependency update",
        "upgrade": "JavaScript dependency upgrade",
    },
    "yarn": {
        "install": "JavaScript dependency install",
        "add": "JavaScript dependency add",
        "remove": "JavaScript dependency remove",
        "upgrade": "JavaScript dependency upgrade",
    },
    "bun": {
        "install": "JavaScript dependency install",
        "add": "JavaScript dependency add",
        "remove": "JavaScript dependency remove",
        "update": "JavaScript dependency update",
    },
    "pip": {
        "install": "Python dependency install",
        "uninstall": "Python dependency remove",
    },
    "pip3": {
        "install": "Python dependency install",
        "uninstall": "Python dependency remove",
    },
    "uv": {
        "add": "Python dependency add",
        "remove": "Python dependency remove",
        "sync": "Python dependency sync",
        "pip": "Python dependency operation",
    },
    "poetry": {
        "add": "Python dependency add",
        "remove": "Python dependency remove",
        "update": "Python dependency update",
        "install": "Python dependency install",
    },
    "cargo": {
        "add": "Rust dependency add",
        "remove": "Rust dependency remove",
        "update": "Rust dependency update",
    },
    "go": {
        "get": "Go dependency change",
        "install": "Go tool install",
    },
    "composer": {
        "require": "PHP dependency add",
        "remove": "PHP dependency remove",
        "update": "PHP dependency update",
        "install": "PHP dependency install",
    },
    "dotnet": {
        "add": "dotnet dependency add",
        "remove": "dotnet dependency remove",
        "restore": "dotnet dependency restore",
    },
}


def evaluate(event: GuardEvent) -> GuardDecision:
    if not event.command:
        return allow(GUARD_ID, "no shell command found")
    segments = split_command_segments(event.command)
    segment_decisions: list[GuardDecision] = []
    for segment in segments:
        segment_decisions.append(evaluate_segment(segment, event.command))
    return max(segment_decisions, key=lambda item: {"allow": 0, "record_only": 1, "ask": 2, "block": 3}[item.decision])


def evaluate_segment(segment: str, original_command: str) -> GuardDecision:
    normalized = normalize_command(segment)
    normalized_for_git = strip_git_global_options(normalized)
    for pattern in READ_ONLY_PATTERNS:
        if pattern.search(normalized_for_git):
            return allow(GUARD_ID, "read-only command")
    for pattern, reason in BLOCK_PATTERNS:
        if pattern.search(normalized_for_git):
            return block(
                GUARD_ID,
                reason,
                matched=[segment],
                evidence={"command": original_command, "segment": segment},
            )
    dependency_reason = classify_dependency_operation(normalized)
    if dependency_reason is not None:
        return ask(
            GUARD_ID,
            dependency_reason,
            matched=[segment],
            evidence={"command": original_command, "segment": segment},
        )
    for pattern, reason in ASK_PATTERNS:
        if pattern.search(normalized_for_git):
            return ask(
                GUARD_ID,
                reason,
                matched=[segment],
                evidence={"command": original_command, "segment": segment},
            )
    return allow(GUARD_ID, "no dangerous command pattern matched")


def split_command_segments(command: str) -> list[str]:
    return [segment.strip() for segment in SEGMENT_SPLIT_PATTERN.split(command) if segment.strip()]


def classify_dependency_operation(command: str) -> str | None:
    parts = command.split()
    if not parts:
        return None
    manager = parts[0].lower()
    actions = DEPENDENCY_ACTIONS.get(manager)
    if actions is None:
        return None
    if manager == "dotnet" and len(parts) >= 3 and parts[1].lower() in {"add", "remove"}:
        action = f"{parts[1].lower()} {parts[2].lower()}"
        if action in {"add package", "remove package"}:
            return actions[parts[1].lower()]
    if manager == "uv" and len(parts) >= 3 and parts[1].lower() == "pip":
        pip_action = parts[2].lower()
        if pip_action in {"install", "uninstall"}:
            return "Python dependency install" if pip_action == "install" else "Python dependency remove"
    action = parts[1].lower() if len(parts) > 1 else "install"
    return actions.get(action)


def normalize_command(command: str) -> str:
    try:
        tokens = shlex.split(command, posix=False)
    except ValueError:
        tokens = command.split()
    return " ".join(tokens)


def strip_git_global_options(command: str) -> str:
    parts = command.split()
    if not parts or parts[0] != "git":
        return command
    output = ["git"]
    index = 1
    while index < len(parts):
        token = parts[index]
        if token in {"-C", "-c"} and index + 1 < len(parts):
            index += 2
            continue
        if token.startswith("--git-dir=") or token.startswith("--work-tree="):
            index += 1
            continue
        output.extend(parts[index:])
        break
    return " ".join(output)
