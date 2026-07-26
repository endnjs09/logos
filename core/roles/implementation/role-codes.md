# Implementation Role Codes

These codes split executor work by implementation domain. They should be used in
task plans, role routing, run logs, and installed Codex role cards.

| Code | Domain | Core Source | Purpose |
|---|---|---|---|
| `bd` | Application Behavior | `core/roles/implementation/bd.md` | Default application behavior that is not clearly frontend, database, system, or test work |
| `fd` | Frontend | `core/roles/implementation/fd.md` | User-facing UI, client state, forms, accessibility, browser behavior |
| `db` | Persistence | `core/roles/implementation/db.md` | Persistence shape, schema, migrations, constraints, and query behavior |
| `sys` | System | `core/roles/implementation/sys.md` | Build, runtime config, infrastructure, tooling, and deployment surfaces |
| `test` | Test | `core/roles/implementation/test.md` | Automated tests, fixtures, verification support |

Route by changed surface, not by feature label. When a task does not clearly
belong to `fd`, `db`, `sys`, or `test`, use `bd` as the default application
behavior role. Use more than one implementation role when a task crosses
surfaces. Keep the role codes short, but keep their output evidence explicit.

Each implementation role may point to a details file under
`core/roles/references/`. Details are not default context.
