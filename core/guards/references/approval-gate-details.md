---
id: logos.reference.approval-gate-details
kind: reference
name: approval-gate-details
description: Detailed implementation notes for Codex permission request integration.
status: active
version: 0.1.0
applies_to:
  - logos.guard.approval-gate
---

# Approval Gate Details

Codex native approval remains authoritative for command execution. Logos should
add a note only when it can explain project-specific risk. Unknown permission
requests should stay silent so the user sees the normal Codex approval prompt
without extra noise.
