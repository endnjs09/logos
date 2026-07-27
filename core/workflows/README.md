# Logos Workflows

`core/workflows/` defines the canonical lifecycle for Logos work. These files
are source assets for the harness. They are not meant to be eagerly loaded by
Codex during normal task execution.

## Responsibility

- `core/roles/` defines who performs a responsibility.
- `core/workflows/` defines how work moves from one state to the next.
- `targets/codex-cli/templates/agents/logos/procedures/` defines the installed
  Codex-facing procedure text for each stage.
- `packages/logos-runner/` materializes workflow decisions into plan state,
  stage prompts, gates, and result files.

## Files

| File | Purpose |
| --- | --- |
| `low.yaml` | Minimal flow for small, clear, low-risk work. |
| `middle.yaml` | Default flow for ordinary development work. |
| `high.yaml` | Structured flow for broad, risky, or hard-to-reverse work. |
| `planning.yaml` | State transitions from request to execution gate. |
| `execution.yaml` | Preconditions and routing for implementation work. |
| `review.yaml` | Pre-execution, security, and verification review policy. |
| `recovery.yaml` | Retry, rollback, blocked, and resume transitions. |
| `context-handoff.yaml` | Compact context passing and write-boundary policy. |
| `workflow-codes.md` | Shared names for modes, stages, transitions, and gates. |

## Installation Policy

Workflow assets are normally not copied verbatim into target projects. Their
rules are reflected in installed procedures, role cards, Runner gates, and
generated manifests. If a future target needs local workflow inspection, install
a manifest or selected workflow summary instead of loading every workflow file as
default context.

## Authoring Rules

- Keep workflow files structured and state-oriented.
- Prefer explicit states, gates, transitions, and outputs over prose.
- Do not duplicate role responsibilities here.
- Do not put Codex-specific hook mechanics here; target-specific mechanics
  belong under `targets/codex-cli/`.
- If a workflow can block, define the return state.
- If a workflow can resume, define the source of truth for resume.
