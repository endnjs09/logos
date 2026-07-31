---
id: logos.reference.prompts-overview
kind: reference
name: prompts-overview
description: Explains the purpose and boundaries of Logos prompt contract assets.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
applies_to:
  - runner-prompt-assembly
depends_on: []
---

# Logos Prompt Contracts

`core/prompts/` contains shared prompt contracts used by Logos Runner when it
builds stage prompts for Codex workers.

These files are not role definitions, workflow steps, rules, or hard guards.
Those assets live in their own `core/` directories. Prompt contracts define the
common wrapper, result shape, evidence style, and user-facing response
expectations that every assembled worker prompt should preserve.

Runner should copy these assets into `.agents/logos/prompts/` during install and
read the installed copies when preparing `.logos/plans/<plan_id>/stages/<stage>/prompt.md`.

Default assembly rules:

- Include only compact prompt contracts required by the active stage.
- Keep role behavior in `.agents/logos/roles/`.
- Keep stage behavior in `.agents/logos/procedures/`.
- Keep policy pointers in `.agents/logos/rules/`.
- Read prompt detail references only when changing prompt assembly behavior.
