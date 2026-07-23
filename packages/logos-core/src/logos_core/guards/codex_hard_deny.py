"""Experimental Codex PreToolUse hard-deny output helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodexHardDenyOutput:
    reason: str
    additional_context: str

    def to_dict(self) -> dict[str, object]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": self.reason,
                "additionalContext": self.additional_context,
            }
        }


def build_pre_tool_use_deny_output(reason: str, additional_context: str | None = None) -> dict[str, object]:
    """Build the OMO-observed Codex PreToolUse deny output candidate.

    This shape is intentionally separated from the default Logos hook output.
    Logos must not use it as a confirmed hard guard until an actual Codex
    session proves that Codex stops the tool call.
    """

    context = additional_context if additional_context is not None else reason
    return CodexHardDenyOutput(reason=reason, additional_context=context).to_dict()
