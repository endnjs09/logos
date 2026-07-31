---
id: logos.prompt.json-result-contract
kind: prompt
name: json-result-contract
description: JSON-only final response rules for Runner-managed Codex workers.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
outputs:
  - stage-result-json
depends_on: []
---

# JSON Result Contract

The worker final response must be one JSON object only.

Do not wrap the JSON in Markdown fences. Do not add prose before or after the
JSON. Escape JSON strings correctly; invalid JSON blocks the stage gate.

Include every required field listed in the active stage prompt. Use explicit
empty arrays, empty strings, `false`, or `null` only when the field contract
allows that value.

Persisted Logos artifacts are English-only. Translate or summarize
user-provided text into English before writing official JSON fields. Preserve
original user wording only in raw user-answer records, not in official stage
result JSON.

A result that declares sufficient information must not keep unresolved blocking
questions in the same official JSON object.
