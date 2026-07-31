---
id: logos.prompt.evidence-contract
kind: prompt
name: evidence-contract
description: Evidence recording rules for files, commands, tests, and stage claims.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
outputs:
  - evidence-backed-stage-result
depends_on: []
---

# Evidence Contract

Separate observed facts from assumptions.

For codebase claims, cite files that were read or changed. For command claims,
record the command and result. For tests, record the test command, pass/fail
status, and any skipped reason.

Do not claim that tests, hooks, guards, approvals, or runtime enforcement ran
unless there is concrete evidence from this task.

Use `.logos/plans/<plan_id>/stages/<stage>/raw.md` for worker raw output and
the official stage result JSON for normalized evidence. Runner may copy
selected evidence into `.logos/runs/`, `.logos/evidence/`, and `.logos/memory/`
without asking the worker to re-read those logs.
