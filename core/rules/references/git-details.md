---
id: logos.reference.git-details
kind: reference
name: git-details
description: Detailed guidance for git soft policy.
status: active
version: 0.1.0
applies_to:
  - logos.rule.git
---

# Git Details

Git evidence helps separate user changes from Logos changes. Destructive git
commands are never routine cleanup. If rollback is needed, report the exact
state and ask for explicit user direction.
