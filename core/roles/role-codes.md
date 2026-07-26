# Logos Role Codes

This file defines the short role codes used by installed Codex target assets.
The codes are stable routing labels, not user-facing commands.

## Orchestration Roles

| Code | Role | Core Source | Installed Path | Purpose |
|---|---|---|---|---|
| `orch` | Orchestrator | `core/roles/orch.md` | `.agents/logos/roles/orch.md` | Routes the overall Logos workflow. |
| `exp` | Explorer | `core/roles/exp.md` | `.agents/logos/roles/exp.md` | Performs read-only scan and evidence collection. |
| `intk` | Intake | `core/roles/intk.md` | `.agents/logos/roles/intk.md` | Handles essential clarification and sufficiency. |
| `sp` | Spec Writer | `core/roles/sp.md` | `.agents/logos/roles/sp.md` | Defines what should be built. |
| `pln` | Planner | `core/roles/pln.md` | `.agents/logos/roles/pln.md` | Defines how work should be implemented. |
| `exe` | Executor | `core/roles/exe.md` | `.agents/logos/roles/exe.md` | Routes and coordinates implementation. |
| `rv` | Plan Reviewer | `core/roles/review/rv.md` | `.agents/logos/roles/rv.md` | Reviews the plan before execution. |
| `sec` | Security Reviewer | `core/roles/review/sec.md` | `.agents/logos/roles/sec.md` | Reviews security and sensitive behavior. |
| `vf` | Verifier | `core/roles/review/vf.md` | `.agents/logos/roles/vf.md` | Verifies completed work with evidence. |
| `mem` | Memory Keeper | `core/roles/mem.md` | `.agents/logos/roles/mem.md` | Recovers active work after context loss. |

## Implementation Roles

Implementation role codes are selected by `exe`.

| Code | Role | Core Source | Installed Path | Purpose |
|---|---|---|---|---|
| `bd` | Application Behavior | `core/roles/implementation/bd.md` | `.agents/logos/roles/bd.md` | Default application behavior implementation. |
| `fd` | Frontend | `core/roles/implementation/fd.md` | `.agents/logos/roles/fd.md` | UI, client state, forms, accessibility, browser behavior. |
| `db` | Persistence | `core/roles/implementation/db.md` | `.agents/logos/roles/db.md` | Schema, migrations, persistence, constraints, and query behavior. |
| `sys` | System | `core/roles/implementation/sys.md` | `.agents/logos/roles/sys.md` | Build, runtime config, infrastructure, tooling, and deployment surfaces. |
| `test` | Test | `core/roles/implementation/test.md` | `.agents/logos/roles/test.md` | Tests, fixtures, and verification support. |

## Detail References

Each role may point to:

```text
.agents/logos/roles/references/<role-code>-details.md
```

Details are optional. Read them only when the compact role card is not enough to
make a safe routing, implementation, review, verification, or memory decision.
