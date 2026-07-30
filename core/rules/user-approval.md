---
id: logos.rule.user-approval
kind: rule
name: user-approval
description: Applies when a task needs user confirmation before risky, external, irreversible, or scope-expanding work.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [intake, planning, execute, review]
globs: []
related_guards:
  - logos.guard.approval-gate
  - logos.guard.high-risk-override-block
detail_reference: core/rules/references/user-approval-details.md
---

# User Approval

## Rule
Ask before crossing a meaningful risk, scope, or external-effect boundary.

## Must
- Ask for missing policy decisions that code cannot infer.
- Use Codex native approval for risky command execution.
- Keep approval questions specific and actionable.

## Must Not
- Ask about cosmetic or trivial choices that do not affect correctness or safety.
- Treat approval for one risk as approval for unrelated risks.

## Details
See `core/rules/references/user-approval-details.md`.
