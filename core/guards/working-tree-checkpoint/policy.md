---
id: logos.guard.working-tree-checkpoint
kind: guard
name: working-tree-checkpoint
description: Record git working-tree recovery metadata before risky operations.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
enforcement: hard
enforcement_status: implemented
risk_level: medium
severity: 2
decision: ask
depends_on: []
---

# Working Tree Checkpoint

Before risky operations, record the current git branch, `HEAD`, and
`git status --short` under `.logos/checkpoints/`.

This guard does not automatically reset, stash, or discard user work. It creates
recovery metadata so the user and agent can understand what state existed before
the risky operation.
