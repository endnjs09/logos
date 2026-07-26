---
id: logos.reference.db-details
kind: reference
name: db-details
description: Detailed persistence, migration, and data integrity guidance.
status: active
version: 0.1.0
applies_to:
  - logos.implementation-role.db
---

# Persistence Details

## Purpose

Define detailed data-layer implementation guidance.

## Read Only When

- Schema or migration safety is unclear.
- Data integrity rules are part of the behavior.
- Query or persistence conventions are uncertain.

## Detailed Guidance

- Prefer additive compatible schema changes unless the plan explicitly approves
  destructive behavior.
- Record uniqueness, ownership, transaction, and locking assumptions.
- Do not hide migration risks.
- Keep seed or fixture data free of real secrets.

## Failure Handling

If a destructive migration or production data change is required, stop for
approval and planning review.
