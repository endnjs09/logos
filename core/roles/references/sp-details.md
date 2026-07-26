---
id: logos.reference.sp-details
kind: reference
name: sp-details
description: Detailed specification guidance for Spec Writer.
status: active
version: 0.1.0
applies_to:
  - logos.role.sp
---

# Spec Writer Details

## Purpose

Define how to write the lightest adequate Spec for a task.

## Read Only When

- Complexity level is unclear.
- Success criteria are vague.
- Excluded scope or quality gates are hard to state.

## Detailed Guidance

- Low work may use a one-line plan when behavior is obvious and low risk.
- Middle work needs a Mini Spec with goal, success criteria, key edge cases, and
  excluded scope.
- High work needs confirmed requirements, constraints, quality gates, edge
  cases, excluded scope, and open questions.
- Success criteria must be observable; avoid vague criteria such as "works
  well".

## Failure Handling

If blocking questions remain, return them instead of producing an executable
Spec.
