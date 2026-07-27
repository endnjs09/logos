# Logos Context

`core/context/` defines how Logos keeps, reduces, and transfers task context.
These assets are source policy for Runner, procedures, and memory behavior. They
are not default Codex context.

## Responsibility

- `memory.md` defines when previous work state should be read and what memory
  files mean.
- `handoff.md` defines what compact context is passed between roles and stages.
- `references/` contains details that are read only when the compact context
  policy is insufficient.

## Boundaries

Context is not a transcript. Logos context should preserve decisions, target
files, constraints, verification expectations, changed files, and remaining
risk. It should not preserve raw conversation, large command output, unrelated
file listings, or concrete secret values as official context.

## Installation Policy

Context source assets are not copied verbatim into target projects by default.
Their rules are reflected in installed procedures, role cards, Runner memory
files, `context-handoff.json`, and generated manifests.
