# Codex PreToolUse Hard Deny Probe

This document records the V8-2-A probe for Codex `PreToolUse` hard-deny
behavior.

## Purpose

Logos currently uses project hooks as advisory guardrails: warnings, approval
notes, procedure pointers, and evidence metadata. It must not claim hard
blocking unless a Codex runtime proves that a hook output actually stops the
tool call.

The Codex manual confirms that `PreToolUse` can block or rewrite a call, but the
current local documentation excerpt does not provide the exact hard-deny JSON
schema. OMO uses the candidate shape below. Logos treats it as `reported` until
verified in a real Codex session.

## Candidate Output

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Logos hard-deny probe requested denial.",
    "additionalContext": "Logos hard-deny probe fired."
  }
}
```

## Probe Script

Use:

```text
scripts/codex-pretool-hard-deny-probe.py
```

This script always emits the candidate deny output for a `PreToolUse` payload.
It is intentionally not installed by default.

## Manual Verification Routine

Run this only in a throwaway project.

1. Install Logos for the Codex target.
2. Replace the installed `.codex/hooks/pre_tool_use.py` command in
   `.codex/hooks.json` with the probe script, or temporarily copy the probe over
   `.codex/hooks/pre_tool_use.py`.
3. Start Codex in that throwaway project.
4. Ask Codex to run a harmless command such as `git status`.
5. Observe the result.

Expected classifications:

| Result | Classification |
|---|---|
| Codex refuses to run the tool call without showing an approval prompt | `confirmed` |
| Codex shows the deny message but still asks for approval | `partial` |
| Codex marks the hook failed or ignores the output | `unsupported` |

## Logos Policy

- Do not use this shape in default installed hooks until the result is
  `confirmed`.
- If the result is `partial` or `unsupported`, use Codex native approval,
  sandbox, and optional `execpolicy` instead.
- Even if confirmed, use hard deny only for narrow Logos invariants. Do not turn
  it into a broad shell-command denylist.
