# Logos Roles

`core/roles/` is the source role model for installed Codex target assets.

Role cards are compact runtime instructions. Details live under
`core/roles/references/` and are read only when a role card explicitly says the
extra guidance is needed.

## Runtime Shape

Installed Codex assets use this shape:

```text
.agents/logos/roles/<role-code>.md
.agents/logos/roles/references/<role-code>-details.md
```

Core source mirrors that shape:

```text
core/roles/<role-code>.md
core/roles/implementation/<role-code>.md
core/roles/review/<role-code>.md
core/roles/references/<role-code>-details.md
```

## Role Cards

| Source | Installed Path | Role Code | Purpose |
|---|---|---|---|
| `orch.md` | `.agents/logos/roles/orch.md` | `orch` | Route the overall workflow and decide the next stage. |
| `exp.md` | `.agents/logos/roles/exp.md` | `exp` | Inspect relevant code and project patterns without editing. |
| `intk.md` | `.agents/logos/roles/intk.md` | `intk` | Decide whether essential information is sufficient. |
| `sp.md` | `.agents/logos/roles/sp.md` | `sp` | Convert confirmed requirements into a buildable Spec. |
| `pln.md` | `.agents/logos/roles/pln.md` | `pln` | Produce Task Plan, Context Handoff, and execution gate. |
| `exe.md` | `.agents/logos/roles/exe.md` | `exe` | Route implementation work to specialist roles. |
| `implementation/bd.md` | `.agents/logos/roles/bd.md` | `bd` | Application behavior implementation. |
| `implementation/fd.md` | `.agents/logos/roles/fd.md` | `fd` | Frontend and browser-facing implementation. |
| `implementation/db.md` | `.agents/logos/roles/db.md` | `db` | Persistence, schema, migration, and query work. |
| `implementation/sys.md` | `.agents/logos/roles/sys.md` | `sys` | Build, runtime, tooling, and configuration work. |
| `implementation/test.md` | `.agents/logos/roles/test.md` | `test` | Tests, fixtures, and verification support. |
| `review/rv.md` | `.agents/logos/roles/rv.md` | `rv` | Pre-execution plan review. |
| `review/sec.md` | `.agents/logos/roles/sec.md` | `sec` | Security and sensitive behavior review. |
| `review/vf.md` | `.agents/logos/roles/vf.md` | `vf` | Evidence-based final verification. |
| `mem.md` | `.agents/logos/roles/mem.md` | `mem` | Resume and compact memory recovery. |

## Details

Details are optional references, not default context.

Read a details file only when:

- the compact role card is insufficient;
- role boundary or routing is ambiguous;
- a safety, verification, or recovery decision needs stricter criteria;
- another Logos role explicitly asks for it.

Do not duplicate essential operating instructions only in details. A role card
must remain useful on its own.
