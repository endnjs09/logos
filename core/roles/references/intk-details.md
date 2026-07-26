---
id: logos.reference.intk-details
kind: reference
name: intk-details
description: Detailed sufficiency and clarification guidance for Intake.
status: active
version: 0.1.0
applies_to:
  - logos.role.intk
---

# Intake Details

## Purpose

Define when a question is blocking and how resolved decisions are recorded.

## Read Only When

- It is unclear whether to ask the user.
- Product policy, security policy, or behavior semantics are missing.
- `open_questions` conflicts with sufficient status.

## Detailed Guidance

- Ask about policy choices such as permissions, retention, payment behavior,
  irreversible actions, public/private visibility, and accepted failure modes.
- Do not ask about facts the codebase can answer.
- Do not ask about small visual details unless they affect implementation
  correctness.
- `essential_information_status: sufficient` requires no blocking questions and
  no unresolved open questions.

## Failure Handling

If blocking information is missing, stop before Spec and return the exact
questions.
