# Frontmatter Reference

This document defines the YAML frontmatter contract for Logos Markdown assets.

Frontmatter is the machine-readable boundary between free-form instructions and
the Logos assembler, installer, validator, and future benchmark tooling.

## Common Fields

All agent-facing Markdown files must include these fields.

```yaml
---
id: logos.<kind>.<name>
kind: <document-kind>
name: <name>
description: <short description>
status: draft
version: 0.1.0
---
```

| Field | Required | Description |
|---|---:|---|
| `id` | yes | Globally unique asset identifier |
| `kind` | yes | Document type |
| `name` | yes | Short machine-readable name |
| `description` | yes | Trigger-oriented description |
| `status` | yes | `draft`, `active`, `deprecated`, or `experimental` |
| `version` | yes | Asset behavior version |
| `owner` | no | Owning package or domain |
| `applies_to` | no | Target hosts or modes |
| `depends_on` | no | Other Logos asset ids |
| `related_rules` | no | Rule ids that inform this asset or are centrally embedded for traceability |
| `outputs` | no | Output artifacts produced |
| `schemas` | no | Schemas used by outputs |
| `tags` | no | Search and grouping tags |

## Version Semantics

Instruction asset versions use semver.

| Segment | Meaning |
|---|---|
| `patch` | Text-only clarification that does not change selection, decisions, required outputs, schemas, or enforcement |
| `minor` | Backward-compatible behavior addition or optional output |
| `major` | Changed trigger, decision criteria, required output, schema contract, or guard enforcement behavior |

Do not use version bumps as decoration. If a benchmark uses an asset, a later
benchmark must be able to explain whether behavior changed by comparing asset
versions and the assembled asset hash.

## Status Semantics

| Status | Meaning | May Be Assembled By Default |
|---|---|---|
| `draft` | Incomplete or under review | no |
| `experimental` | Usable only in an explicit experiment profile | no |
| `active` | Approved for normal runtime use | yes |
| `deprecated` | Historical or compatibility asset | no |

Default assembly must include only `active` assets. Any profile that includes
`experimental` or `deprecated` assets must record the inclusion in the run log
and measurement log.

## ID Format

Use this pattern:

```text
logos.<kind>.<name>
```

Examples:

```text
logos.role.pln
logos.implementation-role.fd
logos.skill.nous
logos.command.nous
logos.rule.test-discipline
logos.guard.secret-scan
logos.workflow.socratic-intake
```

## Kind Values

Allowed values:

```text
role
implementation-role
skill
command
rule
guard
workflow
procedure
rubric
template
hook
```

Do not invent new `kind` values without updating
`docs/reference/document-types.md`.

## Description Rules

Descriptions are used by humans and may later be used for selection or trigger
matching. Make them concrete.

Good:

```yaml
description: Use when Logos nous mode is active and a user request needs task planning before implementation.
```

Bad:

```yaml
description: Helps with planning.
```

Rules:

- State when the asset applies.
- Include task phrases when relevant.
- Keep it concise.
- Avoid marketing language.
- Avoid vague labels such as "general helper".

Do not rely on `description` as the only selection mechanism. Any asset that may
be selected automatically should also provide structured selection fields such
as `triggers`, `do_not_trigger_when`, `applies_to`, `modes`, `domains`, or
`globs`.

## Command Fields

```yaml
---
id: logos.command.nous
kind: command
name: nous
description: Activate Logos nous mode for the current Gemini CLI project session.
status: draft
version: 0.1.0
target: gemini-cli
argument_hint: ""
loads:
  - logos.skill.nous
approval_required: false
---
```

Recommended fields:

- `target`
- `argument_hint`
- `loads`
- `allowed_tools`
- `approval_required`

`approval_required` is a declarative hint for command authors and UI surfaces.
It does not grant or remove permission by itself. Runtime enforcement always
comes from hooks and guards, especially `logos.guard.approval-gate`. If a command
sets `approval_required: false` but a guard returns `ask`, the guard decision
wins.

## Skill Fields

```yaml
---
id: logos.skill.nous
kind: skill
name: nous
description: Use when Logos nous mode is active for coding tasks in a Logos-installed project.
status: draft
version: 0.1.0
triggers:
  - Logos-installed coding project
  - implementation request
do_not_trigger_when:
  - user asks for conceptual explanation only
references:
  - references/workflow.md
outputs:
  - task-plan
  - final-response
depends_on:
  - logos.procedure.exploration
related_rules:
  - logos.rule.context-handoff
  - logos.rule.verification
---
```

Recommended fields:

- `triggers`
- `do_not_trigger_when`
- `references`
- `scripts`
- `assets`
- `outputs`
- `depends_on`
- `related_rules`

`do_not_trigger_when` lists conditions that should prevent automatic or
suggested skill selection. Use it to avoid over-triggering on conceptual,
read-only, or unrelated requests.

`depends_on` lists Logos asset ids that the skill actually delegates to,
requires, or explicitly routes through. Do not leave it empty when the body
requires another skill, workflow, guard, rule, or role.

`related_rules` lists rule ids that inform the skill. For a central workflow
skill, these may be the rules embedded once into that skill. For specialty
skills, prefer listing related rules without embedding their full text again.
Use this field to preserve traceability without duplicating rule text across
multiple skills.

## Procedure Fields

```yaml
---
id: logos.procedure.intake
kind: procedure
name: intake
description: Step procedure for deciding whether essential information is sufficient before exploration.
status: active
version: 0.2.0
outputs:
  - intake-result
schemas:
  - schemas/intake-result.schema.json
depends_on:
  - logos.role.intk
related_rules:
  - logos.rule.context-handoff
---
```

Recommended fields:

- `outputs`
- `schemas`
- `depends_on`
- `related_rules`

Procedure files are not independent trigger targets. They are installed as
step-level operating documents and are referenced by a primary skill, such as
`logos.skill.nous`. Do not use `triggers` or `do_not_trigger_when` in procedure
frontmatter; use the body section `Use When` to describe when the primary skill
should apply that procedure.

When a procedure output has a schema, include it in `schemas`. For intake,
`intake-result` records essential information status, internal complexity,
blocking questions, safe assumptions, Interview Draft updates, and whether the
next step is `ask_user` or `exploration`.

For exploration, `exploration-result` records read-only project evidence,
feature scan findings, project intent, likely target files, read-only context,
remaining question candidates, Interview Draft updates, and whether the next
step is `clarification` or `spec`.

For spec, `spec-result` records Low Fast Path, Mini Spec, or Structured Spec
output. It keeps "what to build" separate from the Task Plan's "how to build."

For planning, `task-plan-result` records the execution-ready Task Plan after
Spec. It must include target files, role routing, ordered steps, verification
plan, rollback criteria, excluded scope, blocking questions, Review-Lite result,
and the next step.

Planning may also produce `context-handoff`. Context Handoff is a compact,
role-specific payload for execution or specialist roles. It is not a transcript
dump. Use it to pass only the fields needed by the next role: goal, success
criteria, target files, excluded scope, verification plan, and risk notes. High
complexity work should use Context Handoff by default; middle complexity work
should use it only when multiple files, multiple roles, meaningful risk, or
context-loss risk exists.

## Role Fields

```yaml
---
id: logos.role.pln
kind: role
name: pln
description: Converts user requests into scoped specs and task plans.
status: draft
version: 0.1.0
role_code: pln
layer: orchestration
outputs:
  - spec
  - task-plan
depends_on:
  - logos.workflow.socratic-intake
triggers:
  - user request needs planning
  - requirements are ambiguous
do_not_trigger_when:
  - user only asks for conceptual explanation
---
```

Recommended fields:

- `role_code`
- `layer`
- `inputs`
- `outputs`
- `depends_on`
- `allowed_tools`
- `triggers`
- `do_not_trigger_when`

Allowed orchestration role codes:

```text
orch
intk
exp
sp
pln
exe
sec
rv
vf
mem
```

Use `role_code` to keep installed role cards, doctor checks, and future role
routing aligned. The file name under `.agents/logos/roles/` should match
`role_code`.

## Implementation Role Fields

```yaml
---
id: logos.implementation-role.bd
kind: implementation-role
name: bd
description: Handles API, service, authentication, and server-side business logic implementation.
status: draft
version: 0.1.0
role_code: bd
layer: implementation
domains:
  - backend
  - api
  - auth
triggers:
  - server-side implementation
  - API or authentication change
do_not_trigger_when:
  - frontend-only visual change
---
```

Recommended fields:

- `role_code`
- `domains`
- `inputs`
- `outputs`
- `risk_areas`
- `triggers`
- `do_not_trigger_when`

Allowed implementation role codes:

```text
bd
fd
db
sys
test
```

Implementation roles are selected by `logos.role.exe`; they are not standalone
Codex skills.

## Rule Fields

```yaml
---
id: logos.rule.user-approval
kind: rule
name: user-approval
description: Requires explicit user confirmation before risky or ambiguous work proceeds.
status: draft
version: 0.1.0
enforcement: soft
triggers:
  - risky or ambiguous work
do_not_trigger_when:
  - no action is being taken
related_guards:
  - logos.guard.approval-gate
---
```

Required rule-specific field:

- `enforcement: soft`

Optional fields:

- `globs`
- `applies_to`
- `triggers`
- `do_not_trigger_when`
- `related_guards`

## Guard Fields

```yaml
---
id: logos.guard.file-write-boundary
kind: guard
name: file-write-boundary
description: Blocks file writes outside the current task plan's allowed write paths.
status: draft
version: 0.1.0
enforcement: hard
enforcement_status: policy-only
decision: allow_block_ask
risk_level: high
severity: 3
inputs:
  - task_plan.target_files
  - context_handoff.allowed_write_paths
  - attempted_write_path
outputs:
  - guard-result
schemas:
  - schemas/guard-result.schema.json
---
```

Required guard-specific fields:

- `enforcement: hard`
- `enforcement_status`
- `decision`
- `risk_level`
- `severity`
- `inputs`
- `outputs`

`enforcement_status` values:

| Value | Meaning |
|---|---|
| `policy-only` | The guard is documented but not implemented in runtime code |
| `implemented` | Runtime code exists and is wired into the target path |
| `verified` | Runtime code exists and has passing tests or recorded verification evidence |

Decision values:

```text
allow_block
allow_block_ask
record_only
```

`record_only` is not a blocking decision. Use it only for low-risk observability
guards where failure cannot leak secrets, alter data, delete files, mutate git
history, install dependencies, or change production behavior.

Validators must reject `decision: record_only` for these guard ids or tags:

- `logos.guard.secret-scan`
- `logos.guard.high-risk-override-block`
- `logos.guard.protected-branch-guard`
- `logos.guard.dangerous-command-denylist`
- `logos.guard.file-write-boundary`
- `logos.guard.working-tree-checkpoint`
- any guard with `risk_level: high`
- any guard with `severity: 3`

`risk_level` and `severity` are related but not identical.

- `risk_level` describes the impact area if the guard fails.
- `severity` describes the strength of the current guard decision or required
  response.

For example, a guard can have `risk_level: high` and `severity: 2` when the
domain is sensitive but the specific event can be routed through mandatory
approval instead of an immediate hard block. A guard with `risk_level: high` and
`severity: 0` is invalid because high-risk domains cannot be informational only.

Risk levels:

| Value | Meaning |
|---|---|
| `low` | Observability, formatting, or non-mutating advisory behavior |
| `medium` | May affect local developer workflow or non-sensitive files |
| `high` | May affect secrets, protected branches, destructive commands, data deletion, dependency installation, payments, auth, or production-like state |

Severity values:

| Value | Meaning |
|---:|---|
| `0` | Informational |
| `1` | Warning |
| `2` | Blocking unless explicitly approved |
| `3` | Hard block or mandatory approval path; never record-only |

Validators should reject inconsistent combinations:

- `risk_level: high` with `severity: 0`
- `risk_level: high` with `decision: record_only`
- `severity: 3` with `decision: record_only`
- `risk_level: low` with `severity: 3` unless an explicit `rationale` field
  explains why a low-impact domain must hard block

For high-risk guards, prefer `allow_block` or `allow_block_ask`. Secret leakage,
high-risk override, protected branch mutation, and destructive command attempts
must never be represented as `record_only`.

## Workflow Fields

```yaml
---
id: logos.workflow.socratic-intake
kind: workflow
name: socratic-intake
description: Refines ambiguous user requests into scoped specs through bounded questions.
status: draft
version: 0.1.0
modes:
  - low
  - middle
  - high
outputs:
  - intake
  - spec
  - task-plan
---
```

Recommended fields:

- `modes`
- `entry_state`
- `exit_state`
- `outputs`
- `depends_on`

## Hook Fields

```yaml
---
id: logos.hook.before-tool
kind: hook
name: before-tool
description: Runs guard checks before Gemini CLI tool execution.
status: draft
version: 0.1.0
target: gemini-cli
event: before-tool
target_support:
  status: assumed
  notes: Gemini CLI hook support must be confirmed or emulated by the Logos adapter.
guards:
  - logos.guard.file-write-boundary
  - logos.guard.dangerous-command-denylist
guard_resolution: most_restrictive
---
```

Recommended fields:

- `target`
- `target_support`
- `event`
- `matcher`
- `guards`
- `guard_resolution`
- `timeout_ms`
- `failure_behavior`

`target_support.status` values:

| Value | Meaning |
|---|---|
| `assumed` | Desired lifecycle point is designed but host support is not yet confirmed |
| `confirmed` | Target host natively supports this lifecycle point |
| `emulated` | Logos implements this lifecycle point through a wrapper, command, or adapter |
| `unsupported` | Target host cannot support or emulate this hook |

Hooks with `target_support.status: assumed` may be documented, but they must not
be counted as implemented runtime guarantees. Hooks with `unsupported` must not
be included in active target assembly.

Guard resolution values:

```text
most_restrictive
ordered_first_terminal
record_all_then_decide
```

Default: `most_restrictive`.

For `most_restrictive`, combine guard decisions as follows:

1. Any `block` result makes the whole hook decision `block`.
2. If there is no `block` but at least one `ask`, the hook decision is `ask`.
3. If all guards allow, the hook decision is `allow`.
4. `record_only` results may add evidence but must not downgrade `block` or
   `ask`.

This default should be used for `before-tool`, command execution, file write,
git, dependency, and secret-related hooks.

## Validation Notes

Future validators should reject:

- missing `id`, `kind`, `name`, `description`, `status`, or `version`
- unknown `kind`
- duplicate `id`
- `guard` assets without `enforcement: hard`
- `guard` assets without `enforcement_status`
- high-risk `guard` assets with `decision: record_only`
- severity `3` `guard` assets with `decision: record_only`
- `risk_level: high` guard assets with `severity: 0`
- `rule` assets with `enforcement: hard`
- command files that duplicate full skill content instead of loading a skill
- default assembly that includes `draft` assets
- benchmark assembly that includes `experimental` or `deprecated` assets without recording them
- `depends_on` references to unknown asset ids
- circular `depends_on` graphs
- hook assets with multiple guards but no explicit or defaultable `guard_resolution`
- active hook assets with `target_support.status: assumed` unless the active
  profile explicitly allows assumptions
- active hook assets with `target_support.status: unsupported`
