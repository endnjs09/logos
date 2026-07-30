---
id: logos.rule.verification
kind: rule
name: verification
description: Applies when checking implementation results, tests, success criteria, and final response claims.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [planning, execute, verify, review]
globs: []
related_guards: []
detail_reference: core/rules/references/verification-details.md
---

# Verification

## Rule
Final claims must be backed by recorded evidence.

## Must
- Compare implementation results against success criteria and excluded scope.
- Record commands, changed files, test results, and remaining risks.
- Say what was not verified when evidence is incomplete.

## Must Not
- Present planned work as completed work.
- Hide known failures, skipped checks, or environmental blockers.

## Details
See `core/rules/references/verification-details.md`.
