---
id: logos.reference.mem-details
kind: reference
name: mem-details
description: Detailed memory recovery and context budget guidance.
status: active
version: 0.1.0
applies_to:
  - logos.role.mem
---

# Memory Keeper Details

## Purpose

Define compact recovery from Logos work-state records.

## Read Only When

- Compact memory is missing or stale.
- The active plan or current stage cannot be identified.
- A raw log may be needed to resolve a blocker.

## Detailed Guidance

- Prefer `resume-snapshot.md`, `active-work.json`, `open-items.json`, and
  `run-index.json`.
- Then read the active plan state and current stage result.
- Read raw prompts or raw transcripts only when structured results are missing
  or invalid.
- Resolved questions must not remain open.

## Failure Handling

If memory conflicts, mark the resume context stale and name the conflicting
files.
