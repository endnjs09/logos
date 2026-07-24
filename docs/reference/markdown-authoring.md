# Markdown Authoring Guide

This guide defines how Logos Markdown assets must be written.

In Logos, Markdown is not just documentation. Agent-facing Markdown is
instruction source code. It is parsed, selected, assembled, injected into a
target host, and later measured. Treat every instruction file as an operational
asset with a clear contract.

## Goals

Logos Markdown must be:

- predictable enough to assemble into prompts
- explicit enough to audit
- narrow enough to avoid duplicated instructions
- stable enough for benchmark reproducibility
- structured enough for future validation tools

## Audiences

Logos Markdown has two audiences.

| Audience | Files | Style |
|---|---|---|
| Agent-facing | `core/`, `.agents/`, `targets/`, `plugins/` | Instructional, structured, contract-driven |
| Human-facing | `docs/`, `README.md`, ADRs | Explanatory, navigational, rationale-driven |

Do not mix the two. A role, rule, command, guard, workflow, or skill file is not
an essay. It must tell the receiving agent or runtime exactly what to do, what
not to do, what inputs to use, and what outputs to produce.

## Core Principle

Every agent-facing Markdown file must answer these questions:

1. What kind of asset is this?
2. When is it used?
3. What inputs does it require?
4. What procedure does it impose?
5. What outputs must be produced?
6. What must not happen?
7. What happens on failure?
8. Which other assets does it depend on?

If a file cannot answer these questions, it is not ready to be used as a Logos
instruction asset.

## Required Frontmatter

All agent-facing instruction files must use YAML frontmatter.

Minimum fields:

```yaml
---
id: logos.<kind>.<name>
kind: <role|implementation-role|skill|command|rule|guard|workflow|procedure|rubric|template|hook>
name: <machine-readable-name>
description: <short trigger-oriented description>
status: draft
version: 0.1.0
---
```

Rules:

- `id` must be globally unique.
- `kind` must match one of the supported document types.
- `name` must use lowercase letters, numbers, and hyphens.
- `description` must explain when the asset applies, not market what it is.
- `status` must be one of `draft`, `active`, `deprecated`, or `experimental`.
- `version` must follow Logos asset semver.
- `guard` files must include `enforcement_status`.

Detailed frontmatter rules live in
`docs/reference/frontmatter-reference.md`.

## Asset Versioning

Logos uses semantic versioning for instruction assets because asset behavior is
part of benchmark reproducibility.

Use this meaning:

| Change | When To Use |
|---|---|
| `patch` | Wording, examples, typo fixes, or clarifications that do not change selection, decisions, outputs, or enforcement |
| `minor` | Backward-compatible behavior additions, optional steps, extra examples, new non-required outputs, or stricter wording that does not break existing schemas |
| `major` | Changed decision criteria, changed required outputs, changed schema expectations, changed guard behavior, changed trigger conditions, or removed behavior |

Examples:

- `0.1.0 -> 0.1.1`: clarify wording in a role without changing its duties.
- `0.1.0 -> 0.2.0`: add an optional review step to a workflow.
- `0.1.0 -> 1.0.0`: change a guard from approval to hard block.

Benchmark reports must record the Logos harness version and enough asset
identity to explain behavior changes. At minimum, measurement records should be
able to identify the harness git SHA and the versions or hash of assembled core
assets.

## Status Lifecycle

Use `status` to control whether an asset may be assembled into runtime
instructions.

| Status | Meaning | Assembly Rule |
|---|---|---|
| `draft` | Incomplete or under review | Must not be included in normal Nous Mode or benchmark assembly |
| `experimental` | Usable only for named experiments | Include only when the active profile explicitly enables experimental assets |
| `active` | Approved for runtime use | May be included by normal assembly |
| `deprecated` | Kept for compatibility or historical comparison | Must not be included unless a pinned benchmark profile requests it |

Default prompt assembly must include only `active` assets. Any run that includes
`experimental` or `deprecated` assets must record that fact in the measurement
log.

## Assembly Priority

When multiple instruction assets are assembled, conflicts must resolve by layer
and enforcement strength.

Priority from strongest to weakest:

1. Runtime hard guard decisions
2. Target host safety constraints
3. `core/guards/` hard policies
4. `core/workflows/` state transitions
5. `core/roles/` active role procedure
6. `.agents/skills/` active skill procedure
7. `core/rules/` soft model guidance
8. `core/prompts/` style or response fragments
9. User preference, unless it conflicts with any higher layer

If two assets at the same priority conflict, prompt assembly must stop and record
a conflict instead of silently choosing one. Guard decisions always override
rules, skills, and role text.

## Document Types

Use one file type per responsibility.

| Kind | Purpose |
|---|---|
| `role` | Orchestration role such as `orch`, `intk`, `exp`, `sp`, `pln`, `exe`, `rv`, `vf` |
| `implementation-role` | Specialist role such as `bd`, `fd`, `db`, `sys`, `test` |
| `skill` | Reusable procedural package loaded when a task pattern matches |
| `command` | User or host entrypoint, usually a thin wrapper around a skill |
| `rule` | Soft instruction that guides model behavior |
| `guard` | Hard policy that must be enforced by code |
| `workflow` | Ordered state transition or task lifecycle |
| `procedure` | Step-level procedure referenced by a primary skill |
| `rubric` | Evaluation criteria |
| `template` | Required output shape |
| `hook` | Lifecycle event behavior for a target host |

Detailed type requirements live in `docs/reference/document-types.md`.

## Rules vs Guards

This distinction is mandatory.

`rules` are instructions to the model.

Examples:

- prefer smallest sufficient change
- ask clarification before high-risk implementation
- summarize verification honestly

`guards` are deterministic or host-enforced gates.

Examples:

- block dangerous shell commands
- block writes outside task-plan boundaries
- detect secrets in diffs
- prevent protected branch mutation
- require approval before dependency installation

Do not put hard safety requirements only in `core/rules/`. If violating the
policy could damage files, leak secrets, alter production data, or invalidate
research results, it belongs in `core/guards/` and must eventually be enforced
by code.

## Progressive Disclosure

Keep high-frequency files within explicit size budgets and move detail
downward.

Size targets:

| Asset | Target Size | Hard Review Threshold |
|---|---:|---:|
| Command file | 40-120 lines | 160 lines |
| `SKILL.md` | 80-220 lines | 300 lines |
| Role file | 60-180 lines | 240 lines |
| Rule file | 40-140 lines | 200 lines |
| Guard policy | 80-220 lines | 320 lines |
| Workflow file | 80-260 lines | 360 lines |
| Rubric file | 60-180 lines | 240 lines |
| Template file | 40-160 lines | 220 lines |

When a file crosses the hard review threshold, split detailed material into
`references/`, `examples/`, or a narrower sibling file unless the added length is
required for a single atomic procedure.

Recommended pattern for skills:

```text
skill-name/
├─ SKILL.md
├─ references/
├─ examples/
├─ scripts/
└─ assets/
```

Use:

- `SKILL.md` for core workflow and trigger behavior
- `references/` for detailed domain knowledge
- `examples/` for concrete cases and outputs
- `scripts/` for deterministic repeated operations
- `assets/` for reusable output resources

Do not duplicate detailed policy in both `SKILL.md` and `references/`. The
shorter file should point to the longer one.

## Command Design

Commands should be thin entrypoints.

Good command behavior:

- activate a mode
- load a skill
- pass user arguments into a workflow
- define preconditions and failure behavior

Avoid command files that duplicate full skill logic. If a command needs more
than a short procedure, create or reference a skill.

## Skill Design

Skills are procedural packages. They should describe how to do a task, not just
what the task is.

Every `SKILL.md` must include:

- trigger conditions
- negative trigger conditions
- activation conditions
- required context
- procedure
- outputs
- failure behavior
- references to detailed files

The frontmatter `description` is critical. It should include concrete phrases or
task patterns that should trigger the skill.

Use `do_not_trigger_when` to prevent a skill from matching broad or conceptual
requests. Use `depends_on` when the skill body delegates to or requires another
Logos asset; the dependency list must match the procedure, not just optional
background reading. Use `related_rules` for rules that guide the skill without
being duplicated across generated files.

## Role Design

Roles define identity, boundaries, and outputs. They should not contain target
host implementation details.

Every role must include:

- mission
- when to use
- inputs
- outputs
- responsibilities
- non-goals
- procedure
- escalation rules
- failure modes
- completion criteria

Orchestration roles and implementation specialist roles must be separated.

## Workflow Design

Workflows define state transitions. They must not be vague prose.

Every workflow must include:

- entry conditions
- exit conditions
- modes
- steps
- state transitions
- required outputs
- retry policy
- failure handling

If a workflow can pause for user input, approval, or external feedback, define
the waiting state explicitly.

## Guard Design

Guard documents are policy contracts for code. They must be testable.

Every guard must include:

- threat model
- decision type
- inputs
- allow conditions
- block conditions
- approval conditions
- evidence to record
- failure behavior
- test cases
- related rules

Every guard must declare its implementation state:

```yaml
enforcement_status: policy-only
```

Allowed values:

| Value | Meaning |
|---|---|
| `policy-only` | Policy is documented but not enforced by runtime code |
| `implemented` | Runtime code exists and is wired to a hook or execution path |
| `verified` | Runtime code exists and has passing tests or recorded verification evidence |

Do not describe a guard as enforced unless its `enforcement_status` is
`implemented` or `verified`. Benchmark safety claims may rely only on `verified`
guards.

Guard language must be deterministic. Avoid words like "probably", "maybe",
"reasonable", or "safe enough" unless they are tied to explicit thresholds.

## Rubric Design

Rubrics define evaluation criteria for plans, implementations, reviews, final
responses, and benchmark scoring.

Every rubric must include:

- evaluated artifact
- observable criteria
- scoring scale
- pass conditions
- fail conditions
- evidence required
- examples

Rubrics must evaluate evidence, not confidence. A rubric should prefer
"test command passed with captured output" over "agent believes tests are
sufficient."

## Template Design

Templates define required output shapes.

Every template must include:

- purpose
- when to use
- fields
- required fields
- format
- validation notes
- example

When a schema exists, the template must reference it. If a required field changes
in a template, update the matching schema and bump the template major version.

## Output Contracts

Agent-facing assets must specify their outputs. Use names that can map to files
or schemas.

Examples:

- `spec`
- `task-plan`
- `context-handoff`
- `guard-result`
- `measurement-log`
- `final-response`

If an output has a schema, reference it.

## Writing Style

Use direct instructional language.

Prefer:

```text
Read the task plan, extract allowed write paths, and block writes outside that
set.
```

Avoid:

```text
It would be good to be careful about files that may be outside scope.
```

Rules:

- Write in English unless the file is explicitly Korean-facing.
- Use active voice.
- Use short paragraphs.
- Use ordered steps for procedures.
- Use tables only for structured comparison.
- Do not use motivational language.
- Do not use marketing language.
- Do not include secrets, tokens, private paths, or personal credentials.
- Do not rely on unstated host behavior.

## Linking

Reference other Logos assets by `id` when possible.

Example:

```yaml
depends_on:
  - logos.workflow.socratic-intake
  - logos.guard.file-write-boundary
```

In prose, include paths only when they help maintainers locate the asset.

## Change Discipline

Changing an agent-facing Markdown file can change model behavior. Treat it like
code.

For behavior-changing edits:

- update `version`
- update related schemas if output changes
- update templates if structure changes
- record rationale in docs or ADR when the change is architectural
- add or update examples when trigger behavior changes

## File Placement

Use these locations:

```text
core/roles/                  # Source orchestration and specialist roles
core/rules/                  # Soft model instructions
core/guards/                 # Hard guard policies
core/workflows/              # Lifecycle and state-machine instructions
core/evaluation/             # Rubrics and quality gates
core/prompts/                # Reusable prompt fragments
.agents/                     # Installed/shared agent-facing skills and commands
targets/<target>/            # Target-specific installed templates and wrappers
plugins/<plugin>/            # Optional extension assets
docs/reference/              # Human-facing specification docs
docs/templates/              # Authoring templates
```

## Required Templates

Use the templates in `docs/templates/` when adding new instruction assets:

- `role.template.md`
- `implementation-role.template.md`
- `skill.template.md`
- `command.template.md`
- `rule.template.md`
- `guard-policy.template.md`
- `workflow.template.md`
- `hook.template.md`
- `rubric.template.md`

Do not create a new file shape without first updating the authoring guide and
template set.

## Template-First Workflow

Create instruction assets from templates. Do not start from a blank Markdown
file.

Use this process:

1. Select the matching template in `docs/templates/`.
2. Copy it to the target location.
3. Fill frontmatter before writing body content.
4. Keep required sections even when the first draft is short.
5. Mark unfinished assets as `status: draft`.
6. Use `enforcement_status: policy-only` for guard policies until runtime code
   exists.
7. Run the asset validator before marking the asset `active`.

This keeps authoring fast while preserving a stable shape for prompt assembly
and benchmark reproducibility.
