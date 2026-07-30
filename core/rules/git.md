---
id: logos.rule.git
kind: rule
name: git
description: Applies when using git state, diffs, branches, commits, or remote operations.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [exploration, execute, verify]
globs:
  - ".git/**"
  - "**/.gitignore"
  - "**/.gitattributes"
related_guards:
  - logos.guard.protected-branch-guard
  - logos.guard.working-tree-checkpoint
  - logos.guard.dangerous-command-denylist
detail_reference: core/rules/references/git-details.md
---

# Git

## Rule
Treat git as evidence and preserve user work.

## Must
- Use status and diffs to understand impact.
- Distinguish existing user changes from Logos changes.
- Ask before branch, remote, or history-affecting operations.

## Must Not
- Reset, discard, force-push, or rewrite history as a routine fix.
- Revert unrelated changes unless the user explicitly asks.

## Details
See `core/rules/references/git-details.md`.
