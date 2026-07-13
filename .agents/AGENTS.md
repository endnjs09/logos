---
id: logos.agents.project
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
