---
id: logos.reference.handoff-details
kind: reference
name: handoff-details
description: Detailed reference for role-specific context handoff fields.
status: active
version: 0.1.0
applies_to:
  - logos.context.handoff
depends_on: []
related_workflows:
  - logos.workflow.context-handoff
---

# Handoff Details

## Role-Specific Fields

`exp`

- relevant files
- read-only context files
- discovered patterns
- likely target files
- unknowns that code cannot answer

`intk`

- essential information status
- required questions
- confirmed decisions
- blocking unknowns
- assumptions allowed by project evidence

`sp`

- goal
- success criteria
- constraints
- edge cases
- excluded scope
- non-blocking open questions

`pln`

- target files
- allowed write paths
- implementation steps
- handoff targets
- verification plan
- rollback criteria

`exe`

- target files
- allowed write paths
- implementation steps
- selected specialist roles
- execution deviation policy

`sec`

- sensitive surfaces
- assumptions affecting auth, authorization, payment, secrets, data deletion, or
  external systems
- guard enforcement status when relevant

`vf`

- success criteria
- verification plan
- changed files
- commands run
- tests run
- skipped checks
- remaining risk

## Write Boundary Link

`allowed_write_paths` must come from the approved task plan or context handoff.
It is dynamic per task, not a repository-wide static allow-list.

If execution needs a file outside the approved paths, record an execution
deviation and return to planning when the change expands scope or risk.

`handoff_to` is the compact handoff form of planning role routing. It names only
the next roles that need the payload, not the full implementation plan.

Open questions are not handoff payload. Blocking open questions belong to the
Spec or Task Plan gate and must stop execution. Non-blocking questions remain in
Spec or Task Plan artifacts for review and final risk reporting.

## Compression Rules

Keep handoff short. Prefer IDs, paths, and bullet summaries over copied source.
Do not pass raw evidence unless the next role cannot verify without it.
