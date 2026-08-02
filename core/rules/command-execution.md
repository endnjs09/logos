---
id: logos.rule.command-execution
kind: rule
name: command-execution
description: Applies when an agent plans, runs, or reports shell commands.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [execute, verify]
globs: []
related_guards:
  - logos.guard.dangerous-command-denylist
  - logos.guard.approval-gate
  - logos.guard.working-tree-checkpoint
detail_reference: .agents/logos/rules/references/command-execution-details.md
---

# Command Execution

## Rule
Run commands deliberately, narrowly, and for a clear task purpose.

## Must
- Prefer read-only inspection or focused verification commands.
- Report command intent and relevant results when they affect the task.
- Let Codex approval and Logos guards handle risky execution.

## Must Not
- Run broad, destructive, external, or credential-sensitive commands as routine.
- Treat a command prompt note as proof that a hard guard blocked execution.

## Details
See `.agents/logos/rules/references/command-execution-details.md`.
