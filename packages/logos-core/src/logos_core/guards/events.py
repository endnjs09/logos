"""Guard event adapter models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GuardEvent:
    schema_version: int
    target: str
    hook_event_name: str
    tool_name: str
    cwd: str
    command: str
    raw_input: dict[str, Any] = field(default_factory=dict)


def codex_input_to_guard_event(payload: dict[str, Any], *, hook_event_name: str) -> GuardEvent:
    return GuardEvent(
        schema_version=1,
        target="codex-cli",
        hook_event_name=hook_event_name,
        tool_name=extract_tool_name(payload),
        cwd=extract_string(payload, ("cwd", "working_directory", "workdir")) or "",
        command=extract_command(payload),
        raw_input=payload,
    )


def extract_tool_name(payload: dict[str, Any]) -> str:
    return extract_string(payload, ("tool_name", "tool", "name")) or ""


def extract_command(payload: object) -> str:
    for key in ("command", "cmd", "script", "shell_command"):
        value = find_key(payload, key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for value in iter_strings(payload):
        if looks_like_shell_command(value):
            return value.strip()
    return ""


def extract_string(payload: object, keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = find_key(payload, key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def find_key(value: object, key: str) -> object:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for nested in value.values():
            found = find_key(nested, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = find_key(nested, key)
            if found is not None:
                return found
    return None


def iter_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from iter_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_strings(nested)


def looks_like_shell_command(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith(
        (
            "rm ",
            "rmdir ",
            "rd ",
            "del ",
            "remove-item ",
            "git ",
            "curl ",
            "wget ",
            "npm ",
            "pnpm ",
            "yarn ",
            "bun ",
            "pip ",
            "pip3 ",
            "uv ",
            "poetry ",
            "cargo ",
            "go ",
            "terraform ",
            "kubectl ",
            "docker ",
        )
    )
