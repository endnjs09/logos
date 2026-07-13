---
id: logos.template.project-agents
kind: template
name: project-agents
description: Project-level Logos agent and skill loading instructions.
status: active
version: 0.1.0
---

# Logos Agent Instructions

Use these instructions when Logos Nous Mode is active.

- Read `.agents/skills/nous/SKILL.md` for the Nous workflow.
- Prefer scoped planning, implementation, verification, and evidence.
- Do not claim hard guard enforcement unless the guard is implemented and verified.
- Report missing context instead of inventing unavailable runtime behavior.

<!-- logos-assembly: agents-operating-rules -->

## Logos Operating Rules

Apply these rules when Logos Nous Mode is active.

## Rules

### Command Execution

Use commands to inspect, build, test, and verify. Prefer narrow commands with a
clear purpose. For destructive, network, credential, or production-affecting
commands, follow the user approval rule instead of deciding approval locally.

### Context Handoff

Execution should receive the smallest sufficient context, not the full planning
history. Preserve the user goal, target files, constraints, excluded scope,
known risks, and verification plan.

### Filesystem

Read files needed to understand the task before editing. Keep changes scoped to
the requested behavior and avoid unrelated rewrites or metadata churn.

### Git

Treat existing uncommitted changes as user work unless proven otherwise. Use
git status and diffs to understand impact, but do not revert unrelated changes.

### Secrets

Do not print, persist, or commit secrets. Treat `.env`, private keys, tokens,
credentials, and production connection strings as sensitive unless the user
explicitly provides a safe testing context.

### Security

Do not weaken authentication, authorization, validation, audit logging, or data
protection to make an implementation easier. Escalate security-sensitive
ambiguity to the user instead of guessing.

### User Approval

Pause and ask for explicit approval before actions that may be destructive,
irreversible, security-sensitive, billing-related, production-facing, or outside
the agreed task scope.

### Verification

Before final response, identify what was checked and what was not checked.
Prefer direct evidence such as tests, command output, static inspection, diff
review, or clear reasoning from source files. If verification is incomplete,
state the remaining uncertainty plainly.
