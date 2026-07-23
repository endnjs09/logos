"""Deterministic secret-like value scanner."""

from __future__ import annotations

import re
from dataclasses import dataclass

from logos_core.guards.decision import GuardDecision, allow, ask
from logos_core.guards.events import GuardEvent

GUARD_ID = "logos.guard.secret-scan"

SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "assigned long secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password|client[_-]?secret)\b"
            r"\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{24,})['\"]?"
        ),
    ),
]

PLACEHOLDER_PATTERN = re.compile(
    r"(?i)^(?:"
    r"YOUR_[A-Z0-9_]+|"
    r"[A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|URL)[A-Z0-9_]*|"
    r"<[^>]+>|"
    r"\$\{[A-Z0-9_]+\}|"
    r"REPLACE_ME|"
    r"CHANGE_ME|"
    r"TODO"
    r")$"
)


@dataclass(frozen=True)
class SecretFinding:
    kind: str
    sample: str


def scan_text(text: str) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for kind, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            sample = match.group(1) if match.lastindex else match.group(0)
            if is_placeholder(sample):
                continue
            findings.append(SecretFinding(kind=kind, sample=redact(sample)))
    return findings


def evaluate(event: GuardEvent) -> GuardDecision:
    text = collect_text(event.raw_input)
    if event.command:
        text = f"{event.command}\n{text}"
    findings = scan_text(text)
    if not findings:
        return allow(GUARD_ID, "no secret-like values found")
    return ask(
        GUARD_ID,
        "secret-like value detected",
        severity=3,
        matched=[finding.kind for finding in findings],
        evidence={"findings": [finding.__dict__ for finding in findings]},
    )


def collect_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(collect_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(collect_text(item) for item in value)
    return ""


def is_placeholder(value: str) -> bool:
    stripped = value.strip().strip("'\"")
    return bool(PLACEHOLDER_PATTERN.match(stripped))


def redact(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"
