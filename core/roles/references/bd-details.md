---
id: logos.reference.bd-details
kind: reference
name: bd-details
description: Detailed application behavior implementation guidance.
status: active
version: 0.1.0
applies_to:
  - logos.implementation-role.bd
---

# Application Behavior Details

## Purpose

Define detailed guidance for application behavior implementation.

## Read Only When

- Domain behavior boundaries are unclear.
- Auth, validation, API, service, or business logic interacts with another role.
- Compatibility with existing behavior is uncertain.

## Detailed Guidance

- Preserve established request/response and error conventions.
- Derive actor identity from verified context, not user-submitted fields.
- Keep placeholders for secrets or external keys; do not invent real values.
- Coordinate with `db` for persistence changes and `test` for behavior proof.

## Failure Handling

If required behavior depends on missing policy, route back to intake or planning.
