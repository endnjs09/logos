"""Approval gate classifier for Codex permission requests."""

from __future__ import annotations

from logos_core.guards.decision import GuardDecision, allow, ask, block
from logos_core.guards.events import GuardEvent

GUARD_ID = "logos.guard.approval-gate"


def evaluate(event: GuardEvent) -> GuardDecision:
    raw_text = str(event.raw_input).lower()
    if "danger-full-access" in raw_text:
        return block(GUARD_ID, "danger-full-access permission request", evidence=event.raw_input)
    if "network" in raw_text:
        return ask(GUARD_ID, "network permission request", evidence=event.raw_input)
    if "outside" in raw_text and "workspace" in raw_text:
        return ask(GUARD_ID, "workspace boundary permission request", evidence=event.raw_input)
    if "mcp" in raw_text:
        return ask(GUARD_ID, "MCP permission request", evidence=event.raw_input)
    return allow(GUARD_ID, "unknown permission request")
