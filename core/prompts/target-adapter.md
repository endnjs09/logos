---
id: logos.template.target-adapter
kind: template
name: target-adapter
description: Target adaptation material for assembled host instructions.
status: active
version: 0.1.0
targets:
  - gemini-cli
  - codex-cli
profiles:
  - gemini
  - codex
outputs:
  - target-adapter-context
depends_on: []
---

# Target Adapter Prompt

Apply Logos through the installed host target and active profile. Logos should
compensate for weak planning, scope drift, premature implementation, and
overconfident verification by making workflow steps and evidence requirements
explicit.
