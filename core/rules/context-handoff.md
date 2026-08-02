---
id: logos.rule.context-handoff
kind: rule
name: context-handoff
description: Applies when passing compact task context between Logos stages or roles.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [plan, execute, resume]
globs:
  - ".logos/plans/**/context-handoff.json"
  - ".logos/memory/**"
related_context:
  - logos.context.handoff
detail_reference: .agents/logos/rules/references/context-handoff-details.md
---

# Context Handoff

## Rule
Pass the smallest sufficient context to the next stage or role.

## Must
- Include goal, success criteria, target files, excluded scope, risks, and verification plan.
- Preserve confirmed decisions separately from unresolved questions.

## Must Not
- Copy full transcripts or unrelated evidence into handoff payloads.
- Hide blocking unknowns as assumptions.

## Details
See `.agents/logos/rules/references/context-handoff-details.md`.
