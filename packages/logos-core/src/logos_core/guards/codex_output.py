"""Codex hook output adapter."""

from __future__ import annotations

from logos_core.guards.decision import GuardDecision


def decision_to_codex_output(decision: GuardDecision) -> dict[str, object]:
    if decision.decision == "allow":
        return {}
    if decision.decision == "ask":
        return {
            "systemMessage": (
                f"Logos approval note: {decision.reason}. "
                "Codex approval and sandbox policy remain authoritative."
            )
        }
    if decision.decision == "block":
        return {
            "systemMessage": (
                f"Logos guard warning: {decision.reason}. "
                "Codex approval and sandbox policy remain authoritative; "
                "Logos does not claim hard block enforcement for this hook output."
            )
        }
    return {"systemMessage": f"Logos note: {decision.reason}"}
