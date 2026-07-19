---
id: logos.rule.secrets
kind: rule
name: secrets
description: Avoid exposing or committing secrets.
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
depends_on: []
---

# Secrets Rule

Do not print, persist, or commit secrets. Treat `.env`, private keys, tokens,
credentials, and production connection strings as sensitive unless the user
explicitly provides a safe testing context.
