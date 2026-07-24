---
id: logos.procedure.exploration
kind: procedure
name: exploration
description: Step procedure for inspecting repository structure, existing patterns, and likely target files.
status: active
version: 0.2.0
outputs:
  - exploration-result
schemas:
  - schemas/exploration-result.schema.json
depends_on:
  - logos.role.exp
related_rules:
  - logos.rule.context-handoff
  - logos.rule.filesystem
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.2.0 -->

# Exploration

## Purpose

Gather project evidence for Spec and Task Plan creation before any editing.
Exploration reduces unnecessary questions by checking what the repository can
already answer.

## Use When

- The correct target files are not obvious.
- Existing project conventions should guide the change.
- Intake has enough essential information to begin reading the project.

## Read-Only Boundary

Do not modify files during exploration. Search, inspect, and summarize only.
Record likely target files, but leave write decisions to planning.

## Snapshot Check

If the task continues earlier Logos work, read `.logos/memory/resume-snapshot.md`
first. Use `.logos/memory/active-work.json`, `.logos/memory/open-items.json`, or
`.logos/memory/run-index.json` only when needed to resolve a concrete continuity
question. Do not scan raw `.logos/runs/` or `.logos/evidence/` by default.

## Feature Scan

Inspect only enough structure to support planning:

- Relevant domain code for the requested change.
- Nearby tests or examples for the same behavior.
- Shared, common, config, routing, middleware, build, or framework surfaces that
  may constrain the change.

Keep shared/common/config/middleware checks shallow unless evidence shows they
are directly involved.

## Evidence Rules

- Separate evidence from inference.
- Record file paths and why each file was read.
- Prefer existing project patterns over generic assumptions.
- Keep `likely_target_files` separate from `read_only_context`.
- Keep question candidates only when code and snapshot cannot answer them.

## Procedure

1. Inspect repository structure.
2. Run a focused feature scan for relevant domain code and shallow shared/config surfaces.
3. Read likely entry points, adjacent implementations, tests, and project docs or config that reveal project intent.
4. Capture code evidence with paths and reasons.
5. Identify likely target files and read-only context files separately.
6. Note hash diff or working-tree state only if available and relevant.
7. Remove questions that repository evidence answers.
8. Carry remaining question candidates and blocking unknowns into Interview Draft updates.
9. Reassess complexity with evidence and choose `next_step`.

## Outputs

- `exploration-result`

## Output Contract

Return this structure:

```yaml
schema_version: 1
exploration_summary: "<what was inspected and why>"
snapshot_used: false
snapshot_sources:
  - "<snapshot or memory file read, if any>"
files_read:
  - path: "<file path>"
    reason: "<why it was read>"
feature_scan:
  - area: "<domain/shared/common/config/middleware/build/test>"
    finding: "<brief finding>"
code_evidence:
  - source: "<file path or command>"
    evidence: "<fact supported by the source>"
project_intent:
  - source: "<README/config/docs/file>"
    intent: "<project convention, goal, or constraint>"
hash_diff:
  - source: "<git/status/hash source>"
    finding: "<state difference or no relevant diff>"
likely_target_files:
  - path: "<file likely to change later>"
    reason: "<why>"
read_only_context:
  - path: "<file needed for context but not likely to change>"
    reason: "<why>"
existing_patterns:
  - "<pattern found in existing code>"
constraints_discovered:
  - "<constraint discovered during exploration>"
question_candidates:
  - question: "<question that code cannot answer>"
    reason: "<why it matters>"
blocking_unknowns:
  - "<unknown that blocks spec or task plan>"
interview_draft_update:
  known_facts:
    - "<fact discovered from code or snapshot>"
  confirmed_decisions:
    - "<decision supported by user answer or project evidence>"
  open_questions:
    - "<question to carry forward>"
  excluded_scope:
    - "<scope not supported by evidence or not requested>"
complexity_reassessment:
  previous_complexity: low | middle | high
  recommended_complexity: low | middle | high
  basis:
    - "<reason>"
next_step: clarification | intake
```

Use `next_step: clarification` only when exploration finds blocking unknowns
that repository evidence cannot resolve. Otherwise use `next_step: intake`.

## Failure Handling

Report inaccessible files, missing project context, or ownership uncertainty
instead of guessing silently. If a required decision cannot be made from code or
snapshot evidence, return `next_step: clarification`.
