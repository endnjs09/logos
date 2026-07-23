---
id: logos.guard.approval-gate
kind: guard
name: approval-gate
description: Classify Codex permission requests that require user approval.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
enforcement: hard
enforcement_status: implemented
decision: allow_block_ask
risk_level: high
severity: 3
depends_on: []
---

# Approval Gate

Block `danger-full-access` permission requests for the default Codex target.

Ask before network access, workspace-boundary writes, MCP side-effect tools, or
unknown permission requests.

This guard relies on Codex `approval_policy = "on-request"` remaining available.
