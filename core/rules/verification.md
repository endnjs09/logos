---
id: logos.rule.verification
kind: rule
name: verification
description: Require evidence-backed verification before final responses.
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

# Verification Rule

Before final response, identify what was checked and what was not checked.
Prefer direct evidence such as tests, command output, static inspection, diff
review, or clear reasoning from source files. If verification is incomplete,
state the remaining uncertainty plainly.
