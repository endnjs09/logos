# Logos Role Codes

This file defines the short role codes used by installed Codex target assets.
The codes are stable routing labels, not user-facing commands.

| Code | Role | Current Core Counterpart | Purpose |
|---|---|---|---|
| `orch` | Orchestrator | new coordinator layer | Routes the overall Logos workflow |
| `intk` | Intake | planner | Clarifies ambiguous or underspecified requests |
| `pln` | Planner | planner | Produces scoped task plans |
| `exp` | Explorer | explorer | Inspects codebase structure and existing patterns |
| `sp` | Spec Writer | planner | Defines what should be built before task planning |
| `exe` | Executor | executor | Coordinates implementation work |
| `sec` | Security Reviewer | reviewer | Reviews security-sensitive behavior |
| `rv` | Reviewer | reviewer, plan-reviewer | Reviews scope, maintainability, and quality |
| `vf` | Verifier | tester | Verifies completed work with evidence |
| `mem` | Memory Keeper | gap-analyzer, recovery docs | Recovers active work after context loss |

Implementation role codes are selected by `exe` and are defined in
`core/roles/executor/implementation-role-codes.md`.
