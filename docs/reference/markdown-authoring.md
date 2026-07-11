# Markdown Authoring Guide

This guide defines how Logos Markdown assets must be written.

Logos uses Markdown files for two different audiences:

1. **Agent-facing assets**: instructions consumed by Gemini CLI, Codex CLI, or a Logos role.
2. **Human-facing documentation**: explanations for maintainers and users.

Do not mix these styles. A command, role, skill, rule, or prompt file is not a
blog post. It is an operational instruction asset.

## Asset Types

| Location | Audience | Purpose |
|---|---|---|
| `core/roles/*.md` | Agent | Define role identity, responsibilities, constraints, inputs, and outputs. |
| `core/rules/*.md` | Agent + runtime | Define policy that controls decisions and workflow behavior. |
| `core/prompts/*.md` | Agent | Reusable prompt fragments assembled into target instructions. |
| `targets/*/commands/*.md` | Agent | User-invoked workflows for a specific CLI target. |
| `targets/*/prompts/*.md` | Agent | Target-specific prompt wrappers. |
| `plugins/*/commands/*.md` | Agent | Plugin-provided workflow commands. |
| `plugins/*/roles/*.md` | Agent | Plugin-provided role definitions. |
| `plugins/*/skills/*/SKILL.md` | Agent | Domain procedure, references, and execution protocol. |
| `docs/**/*.md` | Human | Project documentation, design notes, references, and ADRs. |
| `README.md` files | Human | Directory purpose and navigation. |

## Global Rules

Use these rules for every Logos Markdown file.

- Write in English unless the file is explicitly Korean-facing.
- Use concise, direct instructions.
- Prefer concrete requirements over abstract advice.
- Define what the agent must do, must not do, and must output.
- Avoid motivational language, marketing language, and vague adjectives.
- Avoid long paragraphs in agent-facing files.
- Use headings to separate purpose, inputs, process, output, and failure rules.
- Keep reusable policy in `core/rules`, not duplicated inside every command.
- Keep target-specific behavior in `targets/*`, not in core assets.
- Keep plugin-specific behavior inside the plugin.
- Do not include secrets, real API keys, private endpoints, or personal paths.

## Frontmatter

Agent-facing Markdown files should start with YAML frontmatter when they need
metadata.

Use frontmatter for:

- name
- description
- argument hints
- target
- mode
- role
- allowed tools
- required inputs
- expected outputs
- version
- tags

Do not use frontmatter for long instructions. Put instructions in the body.

### Command Frontmatter

Use this shape for command files:

```yaml
---
name: logos-plan
description: Create a Logos task plan from a user request
argument-hint: "<request>"
target: gemini-cli
mode: high
---
```

Required fields:

- `description`

Recommended fields:

- `name`
- `argument-hint`
- `target`
- `mode`

### Role Frontmatter

Use this shape for role files:

```yaml
---
name: planner
description: Converts confirmed requirements into an auditable task plan
role: planner
---
```

Required fields:

- `name`
- `description`
- `role`

### Skill Frontmatter

Use this shape for skill files:

```yaml
---
name: security-review
description: Review implementation plans and diffs for security-sensitive risks
version: 0.1.0
tags:
  - security
  - review
---
```

Required fields:

- `name`
- `description`

Recommended fields:

- `version`
- `tags`

### Rule Frontmatter

Rules may omit frontmatter if the filename is self-explanatory. Use frontmatter
when the rule is referenced by tools or plugins.

```yaml
---
name: high-risk-override
description: Blocks unsafe user overrides for sensitive domains
applies-to:
  - mode-selection
  - clarification
  - execution
---
```

## Commands

Commands are workflow entry points. They are invoked by a user but written as
instructions for the agent.

Commands must answer:

- What is the command supposed to do?
- What input does it receive?
- What phases must it follow?
- When must it ask the user before continuing?
- What artifacts must it produce?
- What must it not do?

### Command Structure

Use this structure:

```markdown
---
description: Short action-oriented description
argument-hint: "<request>"
---

# Command Name

## Purpose

One paragraph explaining the command outcome.

## Input

- `$ARGUMENTS`: What it represents.
- Required project context.

## Preconditions

- Conditions that must be true before starting.
- Stop conditions if they are not true.

## Workflow

### Phase 1: ...

Goal:

Actions:

Output:

### Phase 2: ...

...

## User Approval Gates

- List points where the agent must stop and wait.

## Output

- Required artifact names.
- Required summary format.

## Failure Handling

- Where to return when a failure occurs.
```

### Command Writing Rules

- Use imperative instructions.
- Do not describe what the command "will" do for the user; tell the agent what
  to do.
- Include user approval gates for implementation, destructive changes, risky
  scope, or unclear requirements.
- Use `$ARGUMENTS` only when the target command system supports it.
- If a target does not support dynamic command arguments, describe the fallback
  target behavior in `targets/<target>/commands/README.md`.
- Commands should call roles, skills, rules, and workflows by name rather than
  duplicating their full content.

### Good Command Language

```markdown
Read the request, identify missing requirements, and ask blocking questions
before creating the task plan.
```

```markdown
Do not begin implementation until the user approves the selected approach.
```

```markdown
Write the final task plan with target files, implementation steps, verification
steps, risk signals, and rollback criteria.
```

### Bad Command Language

```markdown
This command helps you make a plan.
```

```markdown
You will receive a nice summary after the work is done.
```

```markdown
Try to be careful and do a good job.
```

## Roles

Roles define reusable agent behavior. A role is not a workflow by itself. It is a
bounded responsibility used inside a workflow.

Core roles:

- `planner`
- `explorer`
- `gap-analyzer`
- `plan-reviewer`
- `executor`
- `tester`
- `reviewer`

### Role Structure

Use this structure:

```markdown
---
name: role-name
description: One-sentence role purpose
role: role-name
---

# Role Name

## Mission

Define the role's primary responsibility.

## Inputs

- Required input 1.
- Required input 2.

## Responsibilities

- Concrete responsibility.
- Concrete responsibility.

## Constraints

- What this role must not do.
- What this role must defer to another role.

## Process

1. Step.
2. Step.
3. Step.

## Output Format

Define the exact output structure.

## Failure Conditions

Define when this role must stop, escalate, or request clarification.
```

### Role Writing Rules

- Keep roles narrow.
- A role should not secretly perform another role's job.
- The `planner` does not execute.
- The `explorer` does not modify files.
- The `gap-analyzer` does not write the final plan.
- The `plan-reviewer` approves or rejects plans; it does not rewrite them
  silently.
- The `executor` follows an approved plan and executor context.
- The `tester` verifies behavior and records results.
- The `reviewer` checks quality, scope, and residual risk.

### Role Output Requirements

Every role should define an output shape.

Example:

```markdown
## Output Format

Return:

- `summary`: 2-4 sentences.
- `evidence`: file paths, lines, commands, or artifacts used.
- `findings`: ordered list of issues or observations.
- `open_questions`: blocking and non-blocking questions.
- `next_step`: recommended next workflow step.
```

## Skills

Skills package a reusable procedure or domain expertise. Use skills for tasks
that need more than a role definition.

Examples:

- security review
- frontend implementation guidance
- migration procedure
- benchmark authoring
- plugin creation
- PR review
- test strategy

### Skill Structure

Use this structure:

```markdown
---
name: skill-name
description: Trigger conditions and purpose
version: 0.1.0
---

# Skill Name

## When To Use

Define trigger conditions.

## When Not To Use

Define exclusions.

## Required Inputs

- Input.
- Input.

## Procedure

### Phase 0: Orient

Actions:

Evidence:

Output:

### Phase 1: Analyze

...

## Required Output

Define the artifact or response.

## Quality Bar

Define what must be true for completion.

## Failure Handling

Define stop, retry, or escalation rules.
```

### Skill Writing Rules

- A skill must have clear trigger conditions.
- A skill must state when not to use it.
- A skill must define required inputs.
- A skill must define output artifacts.
- A skill must include verification or quality criteria.
- If a skill uses optional tools, it must define fallback behavior.
- If a skill writes files, it must name the file paths or path pattern.

## Rules

Rules define policy. They should be stable, small, and reusable.

Examples:

- mode selection
- low fast path
- override policy
- retry policy
- context handoff
- verification

### Rule Structure

Use this structure:

```markdown
# Rule Name

## Purpose

What decision this rule controls.

## Applies To

- Workflow stage.
- Role.
- Target.

## Policy

- Concrete rule.
- Concrete rule.

## Allow

- Allowed case.

## Block

- Blocked case.

## Record

- Fields that must be logged.

## Examples

Short examples of allowed and blocked decisions.
```

### Rule Writing Rules

- Rules should be enforceable.
- Avoid rules that cannot be observed or logged.
- Include what to record when the rule applies.
- Include allow/block examples for risky rules.
- Do not bury policy only inside role prompts.

## Prompts

Prompt files are reusable fragments. They should be composable.

Prompt files should not:

- define full workflows
- duplicate command files
- include target-specific install details
- contain project-specific secrets

Use prompts for:

- role tone
- evidence requirements
- output style
- target-specific instruction wrappers
- common warnings

### Prompt Structure

```markdown
# Prompt Fragment Name

## Purpose

Short purpose.

## Instruction

The reusable prompt text.

## Variables

- `{task_request}`
- `{mode}`
- `{executor_context}`
```

## Target Files

Target files adapt core Logos assets to a specific CLI host.

Targets currently include:

- `targets/gemini-cli`
- `targets/codex-cli`

### Target Command Files

Target command files should:

- describe how the command appears in that host
- reference core commands, roles, rules, and workflows
- include host-specific limitations
- avoid redefining core policy

### Target Prompt Files

Target prompt files should:

- wrap core prompt fragments in host-compatible wording
- compensate for known target behavior
- name unsupported features clearly

### Target README Files

Target README files should explain:

- what the target is
- whether it is primary, baseline, or compatibility
- what files are installed
- what is not supported yet
- how target-specific commands map to Logos concepts

## Plugin Files

Plugins extend Logos without changing core assets.

Plugin Markdown should follow the same file-type rules:

- plugin `commands` follow command rules
- plugin `roles` follow role rules
- plugin `skills` follow skill rules
- plugin `guards` follow rule/guard rules
- plugin `prompts` follow prompt rules

Plugin files must not silently override core behavior unless the manifest or
README clearly states the override.

Plugin README files must include:

- purpose
- provided assets
- required permissions
- installation status
- compatibility with targets
- known limitations

## Human Documentation

Human-facing docs live under `docs/` and README files.

Human docs may explain:

- concepts
- architecture
- examples
- rationale
- migration
- troubleshooting

Human docs should not be used as agent instructions unless explicitly referenced
by a command, skill, role, or prompt.

### Human Doc Structure

Use this structure when possible:

```markdown
# Title

## Purpose

## Concepts

## Usage

## Examples

## Notes
```

## Output Formats

Agent-facing files must specify output when the task produces an artifact or
decision.

Use structured output names where possible.

Common output sections:

- `Summary`
- `Evidence`
- `Decisions`
- `Open Questions`
- `Risks`
- `Excluded Scope`
- `Verification`
- `Next Step`

For review-style outputs, use severity:

- `Critical`
- `High`
- `Medium`
- `Low`

For workflow decisions, record:

- selected mode
- final mode
- override status
- risk signals
- blocking questions
- retry count
- verification result

## Evidence Requirements

When a file claims something about the codebase, it should require evidence.

Acceptable evidence:

- file paths
- line numbers when available
- git diff summary
- command output summary
- test result
- schema validation result
- artifact path

Avoid:

- "seems like"
- "probably"
- "should be fine"
- "I think"

If evidence is unavailable, say so explicitly and mark the claim as an
assumption.

## User Approval Gates

Agent-facing commands must stop for approval when:

- implementation is about to start after planning
- destructive file operations are proposed
- mode override is requested
- high-risk domains are involved
- scope is ambiguous
- tests cannot be run
- verification is incomplete

Use direct language:

```markdown
Stop and ask the user to approve the selected approach before implementation.
```

Do not use vague language:

```markdown
Consider checking with the user.
```

## Failure Handling

Commands and skills must define failure handling.

Minimum failure rules:

- If required input is missing, ask a blocking question.
- If code evidence is insufficient, return to exploration.
- If success criteria are unclear, return to clarification.
- If task plan is rejected, return to planning.
- If execution fails, classify the failure before retrying.
- If retry budget is exceeded, stop and report.

## Naming Rules

Use kebab-case for files that are not Python modules:

```text
low-fast-path.md
context-handoff.md
high-risk-override.yaml
plugin-manifest.schema.json
```

Use snake_case only for Python package/module directories:

```text
gap_analyzer
plan_reviewer
test_runner
```

Use target names exactly:

```text
gemini-cli
codex-cli
```

Use role names consistently:

```text
planner
explorer
gap-analyzer
plan-reviewer
executor
tester
reviewer
```

## Markdown Style

- Use `#` for the title.
- Use `##` for main sections.
- Use `###` only when needed.
- Prefer short lists over long paragraphs.
- Use fenced code blocks for examples.
- Use tables only for compact reference data.
- Keep headings stable so tools can parse them later.
- Do not use decorative formatting.

## Review Checklist

Before adding or changing an agent-facing Markdown file, check:

- Is the audience agent-facing or human-facing?
- Is the file in the correct directory?
- Does it have frontmatter if needed?
- Does it define purpose?
- Does it define inputs?
- Does it define constraints?
- Does it define process?
- Does it define output format?
- Does it define failure handling?
- Does it avoid duplicating policy from another file?
- Does it avoid target-specific details unless under `targets/`?
- Does it avoid plugin-specific behavior unless under `plugins/`?

## Minimal Templates

### Command Template

```markdown
---
description: <short action description>
argument-hint: "<input>"
---

# <Command Name>

## Purpose

<What the agent must accomplish.>

## Input

- `$ARGUMENTS`: <meaning>

## Workflow

### Phase 1: <Name>

Goal:

Actions:

Output:

## User Approval Gates

- <approval gate>

## Output

- <artifact or response format>

## Failure Handling

- <failure rule>
```

### Role Template

```markdown
---
name: <role-name>
description: <role purpose>
role: <role-name>
---

# <Role Name>

## Mission

## Inputs

## Responsibilities

## Constraints

## Process

## Output Format

## Failure Conditions
```

### Skill Template

```markdown
---
name: <skill-name>
description: <when and why to use this skill>
version: 0.1.0
---

# <Skill Name>

## When To Use

## When Not To Use

## Required Inputs

## Procedure

## Required Output

## Quality Bar

## Failure Handling
```

### Rule Template

```markdown
# <Rule Name>

## Purpose

## Applies To

## Policy

## Allow

## Block

## Record

## Examples
```
