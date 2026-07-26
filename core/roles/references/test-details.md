---
id: logos.reference.test-details
kind: reference
name: test-details
description: Detailed test design, fixture, command, and evidence guidance.
status: active
version: 0.1.0
applies_to:
  - logos.implementation-role.test
---

# Test Details

## Purpose

Define detailed test and verification support guidance.

## Read Only When

- Test scope, fixture shape, command choice, or skipped-check handling is
  unclear.

## Detailed Guidance

- Test observable behavior and success criteria.
- Keep fixtures minimal and deterministic.
- Record commands exactly as run and classify results honestly.
- A skipped or unavailable test is not a pass.

## Failure Handling

If tests cannot run, record the concrete environment blocker and expected
command.
