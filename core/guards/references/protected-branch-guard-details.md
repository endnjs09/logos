---
id: logos.reference.protected-branch-guard-details
kind: reference
name: protected-branch-guard-details
description: Detailed implementation notes for protected branch mutation checks.
status: active
version: 0.1.0
applies_to:
  - logos.guard.protected-branch-guard
---

# Protected Branch Details

Protected branch detection should handle `main`, `master`, release branches, and
configured project patterns. Read-only git commands are allowed. Commands that
rewrite or delete protected history must not be treated as ordinary approvals.
