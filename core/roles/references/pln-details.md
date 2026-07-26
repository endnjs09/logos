---
id: logos.reference.pln-details
kind: reference
name: pln-details
description: Detailed task planning, target file, role routing, and context handoff guidance.
status: active
version: 0.1.0
applies_to:
  - logos.role.pln
---

# Planner Details

## Purpose

Define how Task Plan, role routing, Context Handoff, and review-lite should be
formed.

## Read Only When

- Target file scope is disputed.
- Role routing is ambiguous.
- Context Handoff decision is unclear.
- Review-lite detects a plan risk.

## Detailed Guidance

- Target files must be justified by Spec or Exploration.
- Route by changed surface, not feature label.
- Use Context Handoff for high complexity, multiple roles, meaningful risk, or
  context loss risk.
- Review-lite must block missing verification, broad target files, unresolved
  blocking questions, and unbounded scope.

## Failure Handling

Return blockers and the stage that must repair them. Do not pass execution with
missing target files or verification plan.
