---
id: logos.rule.security
kind: rule
name: security
description: Applies when authentication, authorization, validation, payment, data safety, or production-like behavior may change.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [intake, spec, planning, execute, review, verify]
globs:
  - "**/*Security*"
  - "**/*Auth*"
  - "**/*Jwt*"
  - "**/*OAuth*"
  - "**/*Payment*"
  - "**/*Permission*"
related_guards:
  - logos.guard.high-risk-override-block
  - logos.guard.secret-scan
  - logos.guard.approval-gate
detail_reference: core/rules/references/security-details.md
---

# Security

## Rule
Preserve security boundaries while implementing requested behavior.

## Must
- Ask blocking policy questions for auth, authorization, payment, and data safety.
- Keep secure defaults when project evidence is missing.
- Route sensitive changes through security review.

## Must Not
- Weaken validation, authentication, authorization, or auditability to make code pass.
- Treat user impatience as permission to bypass high-risk guardrails.

## Details
See `core/rules/references/security-details.md`.
