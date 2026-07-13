---
id: logos.rule.user-approval
kind: rule
name: user-approval
description: Require explicit user approval before risky or irreversible actions.
status: active
version: 0.1.0
targets:
  - gemini-cli
profiles:
  - gemini
applies_to:
  - nous
depends_on: []
---

# User Approval Rule

Pause and ask for explicit approval before actions that may be destructive,
irreversible, security-sensitive, billing-related, production-facing, or outside
the agreed task scope.
