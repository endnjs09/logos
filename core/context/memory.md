---
id: logos.context.memory
kind: context
name: memory
description: Compact policy for reading and writing Logos work memory.
status: active
version: 0.1.0
outputs:
  - memory-policy
depends_on: []
related_workflows:
  - logos.workflow.recovery
---

# Memory Context

Use Logos memory only when active work context is missing, compacted, or unclear.
Do not read `.logos/runs/` or `.logos/evidence/` at the start of normal work.

## Read Order

1. `.logos/memory/resume-snapshot.md`
2. `.logos/memory/active-work.json`
3. `.logos/memory/run-index.json`
4. The specific `.logos/plans/<plan_id>/plan-state.json` named by memory.
5. The specific plan or run artifact needed to continue.
6. Raw evidence only when verification or debugging requires it.

## Store

- Store official memory in English.
- Store compact decisions, current stage, plan id, run id, target files,
  changed files, verification summary, open items, and remaining risk.
- Do not store concrete secret values, full transcripts, large raw outputs, or
  unrelated file listings as memory.

## Details

Read `core/context/references/memory-details.md` only when memory recovery,
compaction, or stale state handling cannot be resolved from this card.
