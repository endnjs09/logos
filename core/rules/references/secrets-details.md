---
id: logos.reference.secrets-details
kind: reference
name: secrets-details
description: Detailed guidance for secret handling soft policy.
status: active
version: 0.1.0
applies_to:
  - logos.rule.secrets
---

# Secrets Details

Use placeholders and environment variable names. If the user gives an actual
secret value, avoid repeating it. Store only redacted evidence and tell the user
where to configure the value outside Logos artifacts.
