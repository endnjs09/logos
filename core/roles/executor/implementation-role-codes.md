# Implementation Role Codes

These codes split executor work by implementation domain. They should be used in
task plans, role routing, run logs, and installed Codex role cards.

| Code | Domain | Purpose |
|---|---|---|
| `bd` | Backend | API, services, auth flow, server-side business logic |
| `fd` | Frontend | UI, client state, forms, accessibility, browser behavior |
| `db` | Database | schema, migrations, persistence, query behavior |
| `sys` | System | build, runtime config, infrastructure, deployment surfaces |
| `test` | Test | automated tests, fixtures, verification support |

Use more than one implementation role when a task crosses domains. Keep the role
codes short, but keep their output evidence explicit.
