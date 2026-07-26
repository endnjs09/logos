---
id: logos.reference.orch-details
kind: reference
name: orch-details
description: Detailed routing and gate recovery guidance for the Orchestrator role.
status: active
version: 0.1.0
applies_to:
  - logos.role.orch
---

# Orchestrator Details

## Purpose

Provide detailed routing, gate, and recovery rules for `orch`.

## Read Only When

- Stage order is ambiguous.
- A gate failed and recovery path is unclear.
- Active work state conflicts with plan state.

## Detailed Guidance

- Treat execution as closed until intake, spec, planning, and review-lite are
  satisfied.
- Route stale context to `mem` before asking the implementation roles to guess.
- Prefer the narrowest next stage that can resolve the blocker.
- If a stage output is missing required fields, route back to that stage.

## Failure Handling

Report the failed gate, the missing or conflicting file, and the smallest repair
action.
