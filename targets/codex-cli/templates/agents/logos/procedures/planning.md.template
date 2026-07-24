---
id: logos.procedure.planning
kind: procedure
name: planning
description: Step procedure for creating the final Logos task plan, context handoff, and review-lite gate before execution.
status: active
version: 0.2.0
outputs:
  - task-plan-result
  - context-handoff
  - verification-plan
schemas:
  - schemas/task-plan-result.schema.json
  - schemas/context-handoff.schema.json
depends_on:
  - logos.procedure.intake
  - logos.procedure.exploration
  - logos.procedure.spec
  - logos.role.pln
related_rules:
  - logos.rule.context-handoff
  - logos.rule.filesystem
  - logos.rule.verification
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.2.0 -->

# Planning

## Purpose

Turn the accepted Spec into an execution-ready Task Plan, decide whether Context
Handoff is needed, and run a light review before any implementation starts.

## Use When

- Intake, exploration, and Spec have enough information to plan implementation.
- The next step may edit files, run tests, change dependencies, or route work to
  implementation roles.
- The executor needs target files, ordered steps, verification, and boundaries.

## Procedure

1. Read the latest intake, exploration, and Spec outputs.
2. Restate the implementation goal in one concise sentence.
3. Build the Task Plan:
   - `target_files`: files or narrow file areas expected to change.
   - `role_routing`: role codes expected for each implementation area.
   - `steps`: ordered implementation steps.
   - `verification_plan`: concrete checks, commands, or manual checks.
   - `risk_notes`: sensitive files, broad changes, dependencies, data, auth,
     security, git, or irreversible operations.
   - `rollback_criteria`: when to stop, revert, or ask the user.
   - `excluded_scope`: work that must not be done in this task.
4. Decide Context Handoff:
   - `low`: default `apply: false`.
   - `middle`: default `apply: false`; set `apply: true` when multiple files,
     multiple roles, meaningful risk, or context loss risk exists.
   - `high`: default `apply: true`.
5. If Context Handoff applies, extract only the fields needed by the next role.
6. Run Review-Lite before execution.
7. Set `next_step` to `executor`, `clarification`, or `spec`.

## Task Plan Rules

- Do not edit files in this procedure.
- Do not invent target files that were not supported by exploration evidence.
- Keep target files narrow enough for the executor to reason about.
- Use role codes instead of long role names:
  `exe`, `bd`, `fd`, `db`, `sys`, `test`, `sec`, `rv`, `vf`, `mem`.
- Every implementation step must have a verification or review expectation.
- Excluded scope must be explicit even when the list is short.

## Context Handoff Rules

Context Handoff is a compact payload for the next role. It is not a transcript
dump and must not include unrelated exploration notes.

When `apply: true`, include:

- `goal`
- `success_criteria`
- `target_files`
- `excluded_scope`
- `verification_plan`
- `risk_notes`

If any required handoff field is missing, do not proceed to execution.

## Review-Lite

Check these items before returning `next_step: executor`:

- `blocking_open_questions` is empty.
- `target_files` is non-empty unless the task is documentation-only or
  explicitly no-edit.
- `steps` are ordered and actionable.
- `verification_plan` is non-empty.
- `excluded_scope` is present.
- The Task Plan does not conflict with the Spec.
- Risk notes from Spec and exploration are reflected in the plan.
- `high` complexity has `context_handoff.apply: true`.
- The executor has enough information to start without rereading the whole
  conversation.

If Review-Lite fails, return to:

- `clarification` when a blocking user decision is missing.
- `spec` when success criteria, excluded scope, or intended behavior is unclear
  or conflicts with the plan.

## Outputs

- `task-plan-result`
- `context-handoff`
- `verification-plan`

## Output Contract

Return a `task-plan-result` object:

```yaml
schema_version: 1
plan_id: "<stable plan id>"
source_spec: "<spec id or short reference>"
complexity: low | middle | high
goal: "<one sentence implementation goal>"
target_files:
  - "<path or narrow file area>"
role_routing:
  - role_code: exe | bd | fd | db | sys | test | sec | rv | vf | mem
    reason: "<why this role is needed>"
steps:
  - id: "<step id>"
    role_code: "<role code>"
    description: "<implementation step>"
    target_files:
      - "<path>"
verification_plan:
  - "<command or concrete check>"
risk_notes:
  - "<risk or empty list item omitted>"
rollback_criteria:
  - "<when to stop, revert, or ask>"
excluded_scope:
  - "<explicit non-goal>"
blocking_open_questions: []
context_handoff:
  apply: true | false
  handoff_to:
    - exe
  reason: "<why handoff is or is not needed>"
  missing_required_fields: []
review_lite:
  passed: true | false
  findings:
    - "<finding>"
next_step: executor | clarification | spec
```

## Failure Handling

If target files cannot be identified from evidence, return to `spec` or
`clarification` instead of guessing. If the Spec and plan conflict, return to
`spec`. If user input is required before safe planning, return to
`clarification`.
