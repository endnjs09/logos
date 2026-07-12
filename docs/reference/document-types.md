# Document Types

This document defines the supported Logos Markdown document types and their
required structure.

## Type Matrix

| Kind | Primary Location | Runtime Role |
|---|---|---|
| `role` | `core/roles/` | Orchestration persona and procedure |
| `implementation-role` | `core/roles/implementation/` | Domain specialist behavior |
| `skill` | `.agents/skills/`, `plugins/*/skills/` | Reusable workflow package |
| `command` | `.gemini/commands/`, `targets/*/commands/` | User or host entrypoint |
| `rule` | `core/rules/` | Soft model instruction |
| `guard` | `core/guards/` | Hard runtime policy |
| `workflow` | `core/workflows/` | State transition and task lifecycle |
| `rubric` | `core/evaluation/` | Evaluation criteria |
| `template` | `core/prompts/`, `docs/templates/` | Output shape |
| `hook` | `targets/*/hooks/` | Host lifecycle intervention |

## Role

Use for orchestration roles such as planner, explorer, gap-analyzer,
plan-reviewer, executor, tester, and reviewer.

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

Use for domain specialists such as frontend, backend, database, system-infra,
security, test, and docs-dx.

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

Implementation roles are selected by the executor or planner when a task touches
their domain.

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
