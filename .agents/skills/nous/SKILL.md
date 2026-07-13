---
id: logos.skill.nous
kind: skill
name: nous
description: Use when Logos Nous Mode is active for Gemini CLI coding tasks.
status: active
version: 0.1.0
triggers:
  - nous mode active
  - Gemini CLI coding task
do_not_trigger_when:
  - nous mode inactive
outputs:
  - final-response
depends_on: []
---

# Nous

## Purpose

Guide Gemini CLI through Logos Nous Mode after the project session is activated.

## Use When

- Logos Nous Mode is active.
- The user enters a coding, debugging, testing, review, or documentation request.

## Do Not Use When

- Logos Nous Mode is inactive.
- The user asks only for a conceptual explanation and no project work is needed.

## Required Context

- `.gemini/GEMINI.md`
- `.agents/AGENTS.md`
- `.logos/session/nous-state.json`

## Procedure

1. Read the user request.
2. Identify whether the task requires clarification, codebase exploration, planning, implementation, or verification.
3. Ask concise blocking questions only when required.
4. Prefer scoped edits and explicit verification.
5. Report limitations when V1 runtime guards, hooks, or evidence capture are not yet available.

<!-- logos-assembly: nous-skill-directive -->

## Assembled Nous Directive

Use this directive after Logos Nous Mode has been activated for the project session.

### Required Operating Loop

- Clarify only when required information is missing.
- Inspect the codebase before making non-trivial edits.
- Plan the smallest sufficient change.
- Implement within the requested scope.
- Verify with concrete evidence before final response.

## Workflow Material

### workflows/execution.yaml

```yaml

# Execution workflow.

```

### workflows/planning.yaml

```yaml

# Planning workflow.

```

### workflows/review.yaml

```yaml

# Review workflow.

```

## Rule Material

### rules/command-execution.md

# Command Execution Rule

Use commands to inspect, build, test, and verify. Prefer narrow commands with a
clear purpose. Avoid destructive, network, credential, or production-affecting
commands unless the user has approved the risk.

### rules/context-handoff.md

# Context Handoff Rule

Execution should receive the smallest sufficient context, not the full planning
history. Preserve the user goal, target files, constraints, excluded scope,
known risks, and verification plan.

### rules/filesystem.md

# Filesystem Rule

Read files needed to understand the task before editing. Keep changes scoped to
the requested behavior and avoid unrelated rewrites or metadata churn.

### rules/git.md

# Git Rule

Treat existing uncommitted changes as user work unless proven otherwise. Use
git status and diffs to understand impact, but do not revert unrelated changes.

### rules/secrets.md

# Secrets Rule

Do not print, persist, or commit secrets. Treat `.env`, private keys, tokens,
credentials, and production connection strings as sensitive unless the user
explicitly provides a safe testing context.

### rules/security.md

# Security Rule

Do not weaken authentication, authorization, validation, audit logging, or data
protection to make an implementation easier. Escalate security-sensitive
ambiguity to the user instead of guessing.

### rules/user-approval.md

# User Approval Rule

Pause and ask for explicit approval before actions that may be destructive,
irreversible, security-sensitive, billing-related, production-facing, or outside
the agreed task scope.

### rules/verification.md

# Verification Rule

Before final response, identify what was checked and what was not checked.
Prefer direct evidence such as tests, command output, static inspection, diff
review, or clear reasoning from source files. If verification is incomplete,
state the remaining uncertainty plainly.

## Target Profile

### profiles/gemini.yaml

```yaml

schema_version: 1
host: gemini
role: primary_experiment_target
known_risks:
  - scope_drift
  - weak_plan_following
  - overconfident_verification
  - context_sensitivity

```

## Outputs

- A clear response to the user.
- Any required plan, summary, or verification note for the task.

## Failure Handling

Stop and report missing installation, missing session state, or unavailable target behavior.

## References

- `docs/reference/markdown-authoring.md`
- `docs/reference/frontmatter-reference.md`
