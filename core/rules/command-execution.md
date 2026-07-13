---
id: logos.rule.command-execution
kind: rule
name: command-execution
description: Run shell commands deliberately and report relevant results.
status: active
version: 0.1.0
targets:
  - gemini-cli
profiles:
  - gemini
applies_to:
  - nous
depends_on:
  - logos.rule.user-approval
---

# Command Execution Rule

Use commands to inspect, build, test, and verify. Prefer narrow commands with a
clear purpose. For destructive, network, credential, or production-affecting
commands, follow the user approval rule instead of deciding approval locally.
