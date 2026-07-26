---
id: logos.reference.exe-details
kind: reference
name: exe-details
description: Detailed execution, role routing, deviation, and recovery guidance.
status: active
version: 0.1.0
applies_to:
  - logos.role.exe
---

# Executor Details

## Purpose

Define how execution stays inside approved plan boundaries.

## Read Only When

- A step touches multiple implementation surfaces.
- A needed file is outside approved target files.
- A deviation or blocker appears during implementation.

## Detailed Guidance

- Use `bd` as the default application-behavior role when the surface is not
  clearly `fd`, `db`, `sys`, or `test`.
- Stop before editing unapproved files and route back to planning.
- Record all changed files, commands, role results, blockers, and verification
  inputs.
- Use recovery only to repair execution state, not to bypass planning.

## Failure Handling

Return a blocked or partial execution result with deviations and recommended
next stage.
