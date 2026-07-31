---
id: logos.reference.procedures-overview
kind: reference
name: procedures-overview
description: Defines the source layout and authoring boundaries for Logos procedure assets.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
applies_to:
  - procedures
---

# Logos Procedures

`core/procedures/` contains the source procedure documents for Logos stages.
These files are installed into target projects under `.agents/logos/procedures/`.

Procedures define what a stage does. They do not define who performs the work,
which belongs in `core/roles/`, and they do not define lifecycle transitions,
which belong in `core/workflows/`.

## Files

| File | Purpose |
| --- | --- |
| `exploration.md` | Read-only feature scan and project evidence gathering. |
| `intake.md` | Missing-information detection, bounded clarification, and interview draft updates. |
| `spec.md` | Mini or structured specification writing after intake is sufficient. |
| `planning.md` | Task plan and context handoff preparation before execution. |
| `review.md` | Review-lite gate before execution and risk procedure source. |
| `execution.md` | Executor entry conditions and implementation boundaries. |
| `verification.md` | Verification comparison against spec, plan, and execution result. |
| `resume.md` | Context recovery when the active work state is unclear. |

## Installation Policy

Installers copy active procedure assets from this directory into the target
project. Target templates should not duplicate procedure bodies. Target-specific
templates may reference installed procedure paths, but the procedure source of
truth stays here.

## Authoring Rules

- Keep procedure files stage-specific.
- Do not embed implementation-role details unless the stage cannot route without
  them.
- Do not duplicate rules; reference `.agents/logos/rules/` when rule detail is
  needed.
- Do not add host-specific hook mechanics here.
- Do not make procedures auto-discoverable skills.
