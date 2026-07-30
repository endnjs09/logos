---
id: logos.reference.command-execution-details
kind: reference
name: command-execution-details
description: Detailed guidance for command execution soft policy.
status: active
version: 0.1.0
applies_to:
  - logos.rule.command-execution
---

# Command Execution Details

Prefer commands that answer one question. Avoid broad command chains when a
smaller inspection or verification command would do. If command output is large,
record the useful evidence and avoid flooding the model context.
