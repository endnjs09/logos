---
id: logos.procedure.execution
kind: procedure
name: execution
description: Step procedure for selecting executor role codes and applying scoped implementation changes.
status: active
version: 0.1.0
outputs:
  - implementation-result
depends_on:
  - logos.procedure.planning
  - logos.role.exe
related_rules:
  - logos.rule.command-execution
  - logos.rule.filesystem
  - logos.rule.git
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.1.0 -->

# Execution

## Purpose

Apply the smallest sufficient implementation change through the appropriate role code.

## Use When

- A task plan has enough context to edit files.

## Procedure

1. Choose relevant executor role codes: `bd`, `fd`, `db`, `sys`, or `test`.
2. Keep edits inside target files unless new evidence requires a plan update.
3. Preserve existing project patterns.
4. Record changed files and verification needs.
5. Stop and return to planning when the implementation scope changes materially.

## Outputs

- `implementation-result`

## Output Contract

Return changed files, role codes used, implementation summary, deviations from
the plan, and verification needs.

## Failure Handling

If a change cannot be completed safely, record the blocker and do not fake completion.
