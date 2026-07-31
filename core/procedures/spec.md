---
id: logos.procedure.spec
kind: procedure
name: spec
description: Step procedure for converting intake and exploration evidence into a complexity-appropriate specification.
status: active
version: 0.1.0
outputs:
  - spec-result
schemas:
  - schemas/spec-result.schema.json
depends_on:
  - logos.procedure.intake
  - logos.procedure.exploration
  - logos.role.sp
related_rules:
  - logos.rule.context-handoff
  - logos.rule.verification
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.1.0 -->

# Spec

## Purpose

Define what should be built before Task Plan or execution. Spec is separate from
planning: Spec states the intended behavior and boundaries; Task Plan states how
to implement it.

## Use When

- Exploration returns `next_step: spec`.
- Intake and exploration provide enough evidence to describe the requested work.

## Inputs

- `intake-result`
- `exploration-result`
- Interview Draft updates
- User answers
- Code evidence and project intent

## Complexity-Based Spec

Choose the lightest spec that fits the evidence.

## Low Fast Path

Use when the request is small, clear, low-risk, and locally scoped.

- Full Spec may be omitted.
- Record a one-line plan.
- Keep success criteria implicit only when they are obvious from the request.

## Middle Mini Spec

Use for ordinary implementation work.

Required fields:

- `Goal`
- `Success Criteria`
- `Key Edge Cases`
- `Excluded Scope`

## High Structured Spec

Use when the work is broad, risky, cross-cutting, hard to reverse, or involves
security, permissions, billing, data deletion, migrations, production-like
state, secrets, or external systems.

Required fields:

- `User Story`
- `Confirmed Requirements`
- `Success Criteria`
- `Quality Gates`
- `Constraints`
- `Edge Cases`
- `Excluded Scope`
- `Open Questions`

## Open Questions

Separate blocking questions from non-blocking questions.

- `blocking_open_questions` must be empty before Task Plan.
- Non-blocking open questions may remain in the structured spec when they do not
  prevent safe planning.

## Success Criteria

Write observable criteria. Avoid vague success criteria such as "works well" or
"improves quality" unless paired with concrete behavior or verification.

## Procedure

1. Read intake and exploration results.
2. Choose `spec_type` from complexity and evidence.
3. Convert confirmed decisions and code evidence into requirements.
4. Define excluded scope explicitly.
5. Write observable success criteria.
6. Add quality gates only when the complexity and risk require them.
7. If blocking open questions remain, set `next_step` to `clarification`.
8. If no blocking open questions remain, set `next_step` to `task_plan`.

## Outputs

- `spec-result`

## Output Contract

Return this structure:

```yaml
schema_version: 1
complexity: low | middle | high
spec_type: low_fast_path | mini_spec | structured_spec
source_refs:
  - "<intake-result | exploration-result | user answer | file path>"
one_line_plan: "<required for low_fast_path>"
mini_spec:
  goal: "<required for mini_spec>"
  success_criteria:
    - "<observable success>"
  key_edge_cases:
    - "<edge case>"
  excluded_scope:
    - "<not included>"
structured_spec:
  user_story: "<required for structured_spec>"
  confirmed_requirements:
    - "<requirement>"
  success_criteria:
    - "<observable success>"
  quality_gates:
    - "<quality gate>"
  constraints:
    - "<constraint>"
  edge_cases:
    - "<edge case>"
  excluded_scope:
    - "<not included>"
  open_questions:
    - "<non-blocking question>"
blocking_open_questions:
  - "<question that must be answered before Task Plan>"
interview_draft_update:
  confirmed_decisions:
    - "<decision added or confirmed by the spec>"
  open_questions:
    - "<open question carried forward>"
  excluded_scope:
    - "<excluded scope confirmed by the spec>"
next_step: task_plan | clarification
```

## Failure Handling

If the evidence cannot support a Spec, return `next_step: clarification` with
blocking questions. Do not proceed to Task Plan with unresolved blocking
questions.
