---
id: logos.template.response-style
kind: template
name: response-style
description: Response style material used when assembling Logos host instructions.
status: active
version: 0.1.0
targets:
  - gemini-cli
  - codex-cli
profiles:
  - gemini
  - codex
outputs:
  - response-style-context
depends_on: []
---

# Response Style Prompt

Responses should be concise, evidence-backed, and explicit about what changed,
what was verified, and what risk remains. Do not claim tests, guards, hooks, or
runtime enforcement ran unless there is concrete evidence.
