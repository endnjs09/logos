---
id: logos.reference.prompt-assembly-details
kind: reference
name: prompt-assembly-details
description: Detailed guidance for maintaining Logos Runner prompt assembly.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
applies_to:
  - runner-prompt-assembly
depends_on:
  - logos.prompt.worker-envelope
  - logos.prompt.json-result-contract
  - logos.prompt.evidence-contract
  - logos.prompt.user-response-contract
---

# Prompt Assembly Details

Runner stage prompts should be assembled in this order:

1. Worker envelope contract.
2. Stage metadata and output targets.
3. Required JSON result contract.
4. Evidence contract.
5. User request and available previous artifacts.
6. Required input artifacts.
7. Relevant soft rule pointers.
8. Compact role directive.
9. Stage procedure.

Do not embed the full role reference library or full rule library by default.
Add references as paths and let the worker read them only when the compact
directive is insufficient for the active decision.

Executor and verification prompts may add stage-specific summaries from
`task-plan.json`, `context-handoff.json`, `execution-result.json`, and
`spec.json`. They should still preserve the common contracts.

Prompt assembly changes should be validated by installing into a sample project,
preparing at least one planning stage prompt and one execution or verification
prompt, and checking that the prompt is compact, JSON-bound, and evidence-bound.
