---
id: logos.reference.fd-details
kind: reference
name: fd-details
description: Detailed frontend, accessibility, and client state guidance.
status: active
version: 0.1.0
applies_to:
  - logos.implementation-role.fd
---

# Frontend Details

## Purpose

Define detailed UI and client behavior guidance.

## Read Only When

- UI state, accessibility, form behavior, or responsive layout is uncertain.
- Existing design conventions are not obvious.

## Detailed Guidance

- Match existing component patterns before introducing new abstractions.
- Include loading, error, empty, disabled, and success states when behavior needs
  them.
- Keep labels and controls accessible.
- Avoid unrelated visual redesign.

## Failure Handling

If API behavior is missing or ambiguous, route to `bd` or planning instead of
inventing the contract.
