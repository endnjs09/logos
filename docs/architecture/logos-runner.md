# Logos Runner

## Scope

Logos Runner is a Codex CLI target runtime. It coordinates Logos stages and calls
Codex CLI workers for role-specific work.

## Inputs

- User request
- Project root
- Installed Logos files
- Current Logos plan state

## Worker Model

- Worker command: `codex exec`
- Target directory: project root
- Read-only stages use Codex read-only sandbox
- Execution stages use Codex workspace-write sandbox
- Each worker receives one stage prompt and returns one structured result

## Stages

- `scan`: shallow feature and project scan
- `intake`: required-question and complexity intake
- `spec`: request specification
- `plan`: task plan and context handoff
- `review_lite`: pre-execution plan review
- `execute`: implementation
- `verify`: verification

## State Layout

```text
.logos/
|- plans/
|  `- <plan_id>/
|     |- request.json
|     |- scan-result.json
|     |- intake-result.json
|     |- interview-draft.json
|     |- spec.json
|     |- task-plan.json
|     |- context-handoff.json
|     |- review-lite.json
|     |- execution-result.json
|     |- verification-result.json
|     `- plan-state.json
|- runs/
|  `- <run_id>/
`- memory/
```

## CLI Surface

- `logos-runner doctor`
- `logos-runner start`
- `logos-runner run`
- `logos-runner answer`
- `logos-runner continue`
- `logos-runner execute`
- `logos-runner verify`
- `logos-runner status`

## Installed Codex Flow

```text
logos install --target codex-cli --root <project>
logos-runner doctor --root <project>
logos-runner start --root <project> "<request>"
logos-runner run --root <project> <plan_id>
logos-runner execute --root <project> <plan_id>
logos-runner verify --root <project> <plan_id>
```
