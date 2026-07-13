---
id: logos.rule.filesystem
kind: rule
name: filesystem
description: Keep file reads and edits scoped to the user request.
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

# Filesystem Rule

Read files needed to understand the task before editing. Keep changes scoped to
the requested behavior and avoid unrelated rewrites or metadata churn.
