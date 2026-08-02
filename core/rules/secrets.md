---
id: logos.rule.secrets
kind: rule
name: secrets
description: Applies when credentials, tokens, private keys, cookies, or environment values may be read, written, logged, or summarized.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [intake, plan, execute, review_lite, verify]
globs:
  - "**/.env*"
  - "**/*secret*"
  - "**/*credential*"
  - "**/*private*key*"
related_guards:
  - logos.guard.secret-scan
detail_reference: .agents/logos/rules/references/secrets-details.md
---

# Secrets

## Rule
Use names and placeholders for secrets; do not expose concrete secret values.

## Must
- Refer to required values by name, such as `JWT_SECRET` or `OAUTH_CLIENT_ID`.
- Tell the user to provide real values through their normal secret-management path.
- Redact concrete secret-like values from reports and evidence.

## Must Not
- Generate, print, persist, commit, or summarize real credentials.
- Copy user-provided secret values into examples, tests, or final responses.

## Details
See `.agents/logos/rules/references/secrets-details.md`.
