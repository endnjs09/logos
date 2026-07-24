# Document Types

This document defines the supported Logos Markdown document types and their
required structure.

## Type Matrix

| Kind | Primary Location | Runtime Role |
|---|---|---|
| `role` | `core/roles/`, `.agents/logos/roles/` | Orchestration persona and procedure |
| `implementation-role` | `core/roles/exe/`, `.agents/logos/roles/` | Domain specialist behavior |
| `skill` | `.agents/skills/`, `plugins/*/skills/` | Reusable workflow package |
| `command` | `.gemini/commands/`, `targets/*/commands/` | User or host entrypoint |
| `rule` | `core/rules/` | Soft model instruction |
| `guard` | `core/guards/` | Hard runtime policy |
| `workflow` | `core/workflows/` | State transition and task lifecycle |
| `procedure` | `.agents/logos/procedures/`, `docs/procedures/` | Installed step-level operating procedure |
| `rubric` | `core/evaluation/` | Evaluation criteria |
| `template` | `core/prompts/`, `docs/templates/` | Output shape |
| `hook` | `targets/*/hooks/` | Host lifecycle intervention |

## Role

Use for orchestration roles such as `orch`, `intk`, `exp`, `sp`, `pln`, `exe`,
`sec`, `rv`, `vf`, and `mem`.

Role codes:

- `orch`: overall workflow coordinator
- `intk`: intake and bounded clarification
- `exp`: codebase exploration
- `sp`: specification writing
- `pln`: planning and task-plan shaping
- `exe`: implementation coordinator
- `sec`: security and sensitive-change review
- `rv`: general review
- `vf`: verification
- `mem`: resume and work-state recovery

Required sections:

- `Mission`
- `When To Use`
- `Inputs`
- `Outputs`
- `Responsibilities`
- `Non-Goals`
- `Procedure`
- `Escalation Rules`
- `Failure Modes`
- `Completion Criteria`
- `Related Documents`

Do not put implementation-domain details here unless they apply to every domain.

## Implementation Role

Use for implementation specialists selected by `exe`.

Implementation role codes:

- `bd`: backend, API, service, and server-side logic
- `fd`: frontend, UI, client state, and accessibility
- `db`: database, schema, migration, and persistence work
- `sys`: system, infrastructure, runtime, build, and deployment surfaces
- `test`: test implementation and automated verification support

Required sections:

- `Mission`
- `Activation Conditions`
- `Inputs`
- `Outputs`
- `Domain Responsibilities`
- `Boundaries`
- `Implementation Procedure`
- `Risk Checks`
- `Verification Requirements`
- `Failure Modes`

Implementation roles are selected by `exe` or planned by `pln` when a task
touches their domain.

## Skill

Use for reusable task procedures.

Required sections:

- `Purpose`
- `Use When`
- `Do Not Use When`
- `Required Context`
- `Procedure`
- `Outputs`
- `Failure Handling`
- `References`

Skill directories may include:

```text
references/
examples/
scripts/
assets/
```

Keep `SKILL.md` concise. Put long details into references.

## Command

Use for slash commands or host commands.

Required sections:

- `Purpose`
- `Input`
- `Preconditions`
- `Command Instruction`
- `Loaded Assets`
- `Output`
- `Failure Handling`

Commands should usually load a skill or workflow. They should not duplicate full
skill logic.

## Rule

Use for soft model instructions.

Required sections:

- `Rule Statement`
- `Rationale`
- `Applies To`
- `Must`
- `Must Not`
- `Exceptions`
- `Enforcement`
- `Related Guards`
- `Examples`

Rules may influence model behavior, but they do not guarantee enforcement.

## Guard

Use for hard runtime policies.

Required sections:

- `Threat Model`
- `Decision Type`
- `Inputs`
- `Allow Conditions`
- `Block Conditions`
- `Approval Conditions`
- `Evidence To Record`
- `Failure Behavior`
- `Test Cases`
- `Related Rules`

Guard files must be testable. Each block condition should map to at least one
future test case.

Guard files must also declare implementation state in frontmatter:

```yaml
enforcement_status: policy-only
```

Use `policy-only` until runtime code exists. Use `implemented` only after the
guard is wired into the target path. Use `verified` only after tests or recorded
verification evidence prove the guard fires as intended.

## Workflow

Use for multi-step state transitions.

Required sections:

- `Entry Conditions`
- `Exit Conditions`
- `Modes`
- `States`
- `Steps`
- `State Transitions`
- `Required Outputs`
- `Retry Policy`
- `Failure Handling`

When a workflow waits for user input, define the waiting state explicitly.

## Procedure

Use for installed step-level instructions that are referenced by a primary
skill but should not be auto-selected as standalone skills.

Required sections:

- `Purpose`
- `Use When`
- `Procedure`
- `Outputs`
- `Output Contract`
- `Failure Handling`

Procedures are useful when a host discovers every `SKILL.md` as an independent
candidate but the project needs one central skill to route the workflow.

The `intake` procedure is the first gate for coding work. It decides whether
essential information is sufficient before exploration, sets internal
complexity, and asks blocking questions only when necessary.

The `exploration` procedure is a read-only evidence pass. It gathers code
evidence, project intent, likely target files, and remaining question candidates
before Spec and Task Plan creation.

The `spec` procedure converts intake and exploration evidence into the lightest
adequate specification: Low Fast Path, Mini Spec, or Structured Spec.

The `planning` procedure converts Spec into an execution-ready Task Plan. It
defines target files, role routing, ordered implementation steps, verification
plan, rollback criteria, excluded scope, Context Handoff decision, and
Review-Lite result before execution starts.

## Rubric

Use for evaluation and quality gates.

Required sections:

- `Purpose`
- `Evaluated Artifact`
- `Criteria`
- `Scoring`
- `Pass Conditions`
- `Fail Conditions`
- `Evidence Required`
- `Examples`

Rubrics should evaluate observable evidence, not the model's confidence.
They must name the artifact being evaluated and the evidence required for a pass
or fail decision. If a rubric is used for benchmark scoring, changing criteria or
scoring requires a major version bump.

## Template

Use for output shapes.

Required sections:

- `Purpose`
- `When To Use`
- `Fields`
- `Required Fields`
- `Format`
- `Validation Notes`
- `Example`

Templates should align with schemas when schemas exist.
They must name required fields and validation notes. If a template changes a
required field or output structure, update the matching schema and bump the
template major version.

## Hook

Use for target lifecycle behavior.

Required sections:

- `Event`
- `Matcher`
- `Inputs`
- `Procedure`
- `Decision Output`
- `Failure Behavior`
- `Evidence`
- `Related Guards`

Hooks should describe target-specific behavior. Shared policy belongs in
`core/guards/` or `core/rules/`.
