---
id: logos.rule.security
kind: rule
name: security
description: Preserve security boundaries while performing coding tasks.
status: active
version: 0.1.0
targets:
  - gemini-cli
  - codex-cli
profiles:
  - gemini
  - codex
applies_to:
  - nous
depends_on:
  - logos.rule.secrets
  - logos.rule.user-approval
---

# Security Rule

Do not weaken authentication, authorization, validation, audit logging, or data
protection to make an implementation easier. Escalate security-sensitive
ambiguity to the user instead of guessing.
