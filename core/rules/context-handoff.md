---
id: logos.rule.context-handoff
kind: rule
name: context-handoff
description: Keep implementation context scoped and sufficient.
status: active
version: 0.1.0
targets:
  - codex-cli
  - codex-cli
profiles:
  - codex
  - codex
applies_to:
  - nous
depends_on: []
---

# Context Handoff Rule

Execution should receive the smallest sufficient context, not the full planning
history. Preserve the user goal, target files, constraints, excluded scope,
known risks, and verification plan.
