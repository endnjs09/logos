---
id: logos.prompt.worker-envelope
kind: prompt
name: worker-envelope
description: Common wrapper applied to every Runner-managed Codex worker prompt.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
outputs:
  - stage-prompt
depends_on: []
---

# Worker Envelope Contract

Every Runner-managed worker prompt must identify the active stage, role,
project root, plan id, stage output target, and official output file.

The worker must perform only the assigned stage. It must not proceed to later
stages, bypass Runner gates, or directly edit official Logos result files.
Official result files are materialized by Runner after the worker returns a
valid result.

The worker should read compact role and procedure directives first. Detail
references are optional and should be read only when the compact directive or
the active stage requires them.

If required information is missing, the worker records the blocker in the
result instead of guessing or silently expanding scope.
