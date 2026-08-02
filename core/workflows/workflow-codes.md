# Workflow Codes

This file defines stable names used by workflow assets, Runner state, procedure
files, and installed role prompts.

## Modes

| Code | Meaning |
| --- | --- |
| `low` | Small, clear, local, low-risk work. |
| `middle` | Default ordinary development work. |
| `high` | Broad, risky, cross-cutting, or hard-to-reverse work. |

## Planning Stages

| Stage | Role | Primary Output |
| --- | --- | --- |
| `scan` | `exp` | `scan-result.json` |
| `intake` | `intk` | `intake-result.json` |
| `spec` | `sp` | `spec.json` |
| `plan` | `pln` | `task-plan.json`, `context-handoff.json` |
| `review_lite` | `rv` | `review-lite.json` |

## Execution Stages

| Stage | Role | Primary Output |
| --- | --- | --- |
| `execute` | `exe` plus specialist roles | `execution-result.json` |
| `verify` | `vf` | `verification-result.json` |

## Terminal Outputs

| Output | Owner | Meaning |
| --- | --- | --- |
| `final_response` | `orch` | User-facing completion response after verification. This is not a Runner stage. |

## Specialist Role Codes

| Code | Meaning |
| --- | --- |
| `bd` | Default application behavior implementation. |
| `fd` | Frontend and browser-facing implementation. |
| `db` | Persistence, schema, migration, and query behavior. |
| `sys` | Build, runtime configuration, tooling, and operations. |
| `test` | Tests, fixtures, and verification support. |
| `sec` | Security and sensitive behavior review. |
| `rv` | Pre-execution plan review. |
| `vf` | Final evidence-based verification. |
| `mem` | Resume and compact memory recovery. |

## Transition Results

| Result | Meaning |
| --- | --- |
| `success` | Stage completed and may advance. |
| `pass` | Review or verification gate passed. |
| `fail` | Gate failed and must return to a prior stage. |
| `ask_user` | User input is required before safe progress. |
| `blocked` | Work cannot safely continue without external change. |
| `retry` | Repeat a stage within retry budget. |
| `rollback` | Recommend reverting or repairing partial changes. |

## Gate Names

| Gate | Blocks |
| --- | --- |
| `intake_to_spec` | Spec creation when essential information is missing. |
| `spec_to_plan` | Planning when success criteria or scope is unclear. |
| `plan_to_review_lite` | Review when target files or verification are absent. |
| `review_lite_to_execute` | Execution when plan review fails. |
| `execute_to_verify` | Verification when execution result is incomplete. |
| `verify_to_final` | Final response when evidence is missing or criteria fail. |

## Complexity Profiles

Complexity profiles are internal agent judgments. The user does not select
`low`, `middle`, or `high` directly.

| Profile | Default Use |
| --- | --- |
| `low` | Tiny, local, clear, reversible work. |
| `middle` | Default ordinary development work. |
| `high` | Broad, risky, cross-surface, or hard-to-reverse work. |
