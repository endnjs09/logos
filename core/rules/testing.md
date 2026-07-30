---
id: logos.rule.testing
kind: rule
name: testing
description: Applies when creating, modifying, running, or interpreting tests and verification commands.
status: active
version: 0.1.0
enforcement: soft
always_apply: false
stages: [planning, execute, verify]
globs:
  - "**/*Test.*"
  - "**/*Tests.*"
  - "**/test/**"
  - "**/tests/**"
  - "**/__tests__/**"
related_guards: []
detail_reference: core/rules/references/testing-details.md
---

# Testing

## Rule
Tests should prove the changed behavior, not merely exercise files.

## Must
- Prefer focused tests for the requested behavior.
- Record test commands and pass/fail results.
- Separate code failures from environment failures.

## Must Not
- Claim verification without direct evidence.
- Hide failing tests or skip relevant tests to make the task look complete.

## Details
See `core/rules/references/testing-details.md`.
