---
id: logos.reference.file-write-boundary-details
kind: reference
name: file-write-boundary-details
description: Detailed implementation notes for task-plan write boundaries.
status: active
version: 0.1.0
applies_to:
  - logos.guard.file-write-boundary
---

# File Write Boundary Details

Write boundaries are dynamic. The allow list comes from the approved task plan,
context handoff, and role routing for the current work. A new helper file may be
acceptable when adjacent to an approved target and explicitly justified. Writes
outside workspace, excluded scope, or approved plan boundaries should return to
planning or review.
