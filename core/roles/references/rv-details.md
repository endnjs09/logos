---
id: logos.reference.rv-details
kind: reference
name: rv-details
description: Detailed plan review checklist, rejection, and severity guidance.
status: active
version: 0.1.0
applies_to:
  - logos.role.rv
---

# Plan Reviewer Details

## Purpose

Define detailed pre-execution plan review criteria.

## Read Only When

- It is unclear whether a plan should pass, warn, or block.
- Severity or routing recommendation is disputed.

## Detailed Guidance

- Block when target files are missing, broad, or unjustified.
- Block when verification or rollback is absent.
- Block when unresolved questions affect implementation correctness.
- Warn for non-blocking risk that can be verified later.

## Failure Handling

Return the exact plan field that must be repaired and the stage that should
repair it.
