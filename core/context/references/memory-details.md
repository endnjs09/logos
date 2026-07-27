---
id: logos.reference.memory-details
kind: reference
name: memory-details
description: Detailed reference for Logos memory files and recovery behavior.
status: active
version: 0.1.0
applies_to:
  - logos.context.memory
depends_on: []
related_workflows:
  - logos.workflow.recovery
---

# Memory Details

## Memory Files

`resume-snapshot.md`

- First file to read after context loss.
- Human-readable and compact.
- Should name the active plan, current stage, last verified status, touched
  files, open items, and next safe step.

`active-work.json`

- Machine-readable pointer to the current active work.
- Should identify plan id, run id, current stage, status, next action, and
  important artifact paths.

`run-index.json`

- Compact index of recent runs.
- Used only when the active snapshot is insufficient or when the user asks about
  previous work.

`open-items.json`

- Tracks unresolved questions, blockers, follow-up risks, and unfinished
  verification items.

## Read Policy

Normal task start should not scan memory. Read memory when:

- the user asks to continue previous Logos work;
- context was compacted or lost;
- the active stage is unclear;
- the agent needs to avoid repeating completed work;
- verification requires a named prior artifact.

## Write Policy

Write memory from structured artifacts, not from raw transcript. Prefer:

- `spec.json`
- `task-plan.json`
- `context-handoff.json`
- `execution-result.json`
- `verification-result.json`
- `run.json`

Do not write:

- concrete secret values;
- entire user conversation;
- raw terminal output unless shortened into a summary;
- speculative conclusions without evidence.

## Stale State

If memory conflicts with current files, current files win. Record the mismatch
and continue from the safest earlier stage.
