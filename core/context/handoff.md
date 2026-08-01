---
id: logos.context.handoff
kind: context
name: handoff
description: Compact policy for passing role-specific context between Logos stages.
status: active
version: 0.1.0
outputs:
  - context-handoff-policy
depends_on: []
related_workflows:
  - logos.workflow.context-handoff
---

# Handoff Context

Context Handoff is a compact payload for the next role. It is not a transcript
and should not contain every fact discovered during planning.

## Apply

- `low`: do not apply by default.
- `middle`: apply when multiple roles, multiple target files, meaningful risk,
  or context loss risk exists.
- `high`: apply by default.

## Include

- goal
- confirmed requirements
- success criteria
- target files
- allowed write paths
- handoff targets (`handoff_to`)
- verification plan
- excluded scope
- risk notes

## Exclude

- full conversation transcripts
- large raw command output
- unrelated file listings
- concrete secret values
- repeated procedure text

## Gate

If handoff is required but `target_files`, `allowed_write_paths`, `handoff_to`,
or `verification_plan` is missing, do not proceed to execution.

Blocking open questions stay in the Spec or Task Plan gate and must stop
execution before handoff. Non-blocking open questions stay in Spec or Task Plan
artifacts; do not copy them into the handoff payload.

## Details

Read `core/context/references/handoff-details.md` only when role-specific
handoff fields, write boundaries, or schema mapping need more detail.
