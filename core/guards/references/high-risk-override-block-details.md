---
id: logos.reference.high-risk-override-block-details
kind: reference
name: high-risk-override-block-details
description: Detailed implementation notes for high-risk override blocking.
status: active
version: 0.1.0
applies_to:
  - logos.guard.high-risk-override-block
---

# High-Risk Override Details

User intent is important, but it cannot convert a critical safety violation into
a normal implementation choice. Overrides that weaken auth, authorization,
payment correctness, secret handling, destructive data operations, migrations,
or production controls must go back through clarification, plan review, or a
separate explicit safety procedure.
