---
id: logos.guard.dangerous-command-denylist
kind: guard
name: dangerous-command-denylist
description: Classify dangerous shell and git commands before execution.
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
depends_on: []
---

# Dangerous Command Denylist

Block clearly destructive shell and git commands before execution.

Ask before ordinary git mutation or dependency installation commands.

Allow read-only commands such as `git status`, `git diff`, `git log`, `git show`,
`git branch --show-current`, `git rev-parse`, `pwd`, `ls`, `dir`, and `rg`.

This guard is implemented in the Codex PreToolUse hook, but must not be marked
`verified` until Codex runtime blocking behavior is confirmed.
