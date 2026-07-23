---
id: logos.guard.protected-branch-guard
kind: guard
name: protected-branch-guard
description: Classify git mutation on protected branches before execution.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
enforcement: hard
enforcement_status: implemented
decision: allow_block_ask
risk_level: high
severity: 3
depends_on:
  - logos.guard.dangerous-command-denylist
---

# Protected Branch Guard

Protected branches are `main`, `master`, `production`, and `release/*`.

Allow read-only git commands on protected branches.

Ask before ordinary git mutation on protected branches.

Block destructive git commands such as force push, hard reset, destructive clean,
and forced branch deletion.

If the current branch cannot be detected, ask for ordinary git mutation and block
destructive git commands.
