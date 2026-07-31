---
id: logos.procedure.resume
kind: procedure
name: resume
description: Step procedure for resuming Logos work after context loss without scanning raw logs by default.
status: active
version: 0.1.0
outputs:
  - resume-context
depends_on:
  - logos.role.mem
related_rules:
  - logos.rule.context-handoff
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.1.0 -->

# Resume

## Purpose

Recover enough context to continue without rereading all logs.

## Use When

- Context was compacted or lost.
- The user asks to continue previous work.
- The active plan, changed files, or verification state is unclear.

## Procedure

1. Read `.logos/memory/resume-snapshot.md` first.
2. If insufficient, read `.logos/memory/active-work.json`.
3. If still insufficient, read `.logos/memory/run-index.json`.
4. Open only the specific plan or run record needed.
5. Read raw evidence JSONL only for verification or debugging.

## Outputs

- `resume-context`

## Output Contract

Return current task, completed work, remaining work, touched files, blockers,
and the next action.

## Failure Handling

If state files are missing or stale, inspect current files and report uncertainty.
