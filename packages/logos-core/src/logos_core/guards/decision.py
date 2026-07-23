"""Guard decision model and merge helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DecisionValue = Literal["allow", "ask", "block", "record_only"]

DECISION_RANK = {
    "allow": 0,
    "record_only": 1,
    "ask": 2,
    "block": 3,
}


@dataclass(frozen=True)
class GuardDecision:
    guard_id: str
    decision: DecisionValue
    severity: int
    reason: str
    matched: list[str] = field(default_factory=list)
    evidence: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "guard": self.guard_id,
            "decision": self.decision,
            "severity": self.severity,
            "reason": self.reason,
            "matched": self.matched,
            "evidence": self.evidence,
        }


def allow(guard_id: str, reason: str = "allowed") -> GuardDecision:
    return GuardDecision(guard_id=guard_id, decision="allow", severity=0, reason=reason)


def ask(
    guard_id: str,
    reason: str,
    *,
    severity: int = 2,
    matched: list[str] | None = None,
    evidence: dict[str, object] | None = None,
) -> GuardDecision:
    return GuardDecision(
        guard_id=guard_id,
        decision="ask",
        severity=severity,
        reason=reason,
        matched=matched or [],
        evidence=evidence or {},
    )


def block(
    guard_id: str,
    reason: str,
    *,
    severity: int = 3,
    matched: list[str] | None = None,
    evidence: dict[str, object] | None = None,
) -> GuardDecision:
    return GuardDecision(
        guard_id=guard_id,
        decision="block",
        severity=severity,
        reason=reason,
        matched=matched or [],
        evidence=evidence or {},
    )


def record_only(
    guard_id: str,
    reason: str,
    *,
    severity: int = 1,
    matched: list[str] | None = None,
    evidence: dict[str, object] | None = None,
) -> GuardDecision:
    return GuardDecision(
        guard_id=guard_id,
        decision="record_only",
        severity=severity,
        reason=reason,
        matched=matched or [],
        evidence=evidence or {},
    )


def merge_most_restrictive(decisions: list[GuardDecision]) -> GuardDecision:
    if not decisions:
        return allow("logos.guard.none", "no guards ran")
    return max(decisions, key=lambda item: DECISION_RANK[item.decision])
