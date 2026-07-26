---
id: logos.reference.sec-details
kind: reference
name: sec-details
description: Detailed security, privacy, secret, and external-effect review guidance.
status: active
version: 0.1.0
applies_to:
  - logos.role.sec
---

# Security Reviewer Details

## Purpose

Define detailed security review criteria.

## Read Only When

- Auth, permissions, secrets, sensitive data, billing, deployment, deletion, or
  external systems are involved.

## Detailed Guidance

- Check actor identity and authorization boundaries.
- Check that secret values are placeholders unless the user explicitly supplies
  real values.
- Check sensitive data exposure in responses, logs, tests, and fixtures.
- Treat prompt policy as advisory unless a guard is implemented and verified.

## Failure Handling

For high-risk unresolved issues, block completion and name the missing evidence
or approval.
