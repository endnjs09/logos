---
id: logos.reference.vf-details
kind: reference
name: vf-details
description: Detailed verification, evidence, skipped check, and final status guidance.
status: active
version: 0.1.0
applies_to:
  - logos.role.vf
---

# Verifier Details

## Purpose

Define detailed final verification criteria.

## Read Only When

- Evidence is partial or contradictory.
- A skipped check must be classified.
- Final success, partial, blocked, or failed status is unclear.

## Detailed Guidance

- Verify each success criterion separately.
- Compare changed files against approved target files.
- Copy test summary from structured test or execution results when possible.
- Skipped checks require reason and residual risk.

## Failure Handling

If evidence is missing, mark the result partial, failed, or blocked. Do not
claim success without proof.
