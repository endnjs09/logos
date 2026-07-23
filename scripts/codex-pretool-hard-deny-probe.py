#!/usr/bin/env python3
"""Experimental Codex PreToolUse hard-deny probe.

Install this script manually as a temporary PreToolUse hook in a throwaway
project. It is not part of the default Logos Codex target because the output
schema must be verified in a real Codex runtime before Logos can claim hard
blocking.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    raw = sys.stdin.read()
    if raw.strip():
        try:
            json.loads(raw)
        except json.JSONDecodeError:
            return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Logos hard-deny probe requested denial.",
                    "additionalContext": (
                        "Logos hard-deny probe fired. If Codex still runs or asks approval for "
                        "the tool call, this schema is not confirmed for hard blocking."
                    ),
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
