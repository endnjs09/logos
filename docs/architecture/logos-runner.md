# Logos Runner

## Scope

Logos Runner is a Codex CLI target runtime. It coordinates Logos stages,
prepares role-specific prompts, records structured results, and applies stage
gates.

## Inputs

- User request
- Project root
- Installed Logos files
- Current Logos plan state

## Worker Model

- Worker execution uses Codex native subagents in the active Codex session.
- Logos Runner does not start nested `codex exec` processes.
- Runner prepares one stage prompt at a time.
- The parent Codex session spawns the stage worker with Codex native
  multi-agent tools.
- The worker returns one structured JSON result.
- Runner records that result, validates required fields, and applies the next
  gate.

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
|     |- plan-state.json
|     |- interview-draft.json
|     |- spec.json
|     |- task-plan.json
|     |- context-handoff.json
|     |- review-lite.json
|     |- execution-result.json
|     |- verification-result.json
|     |- user-answers.jsonl
|     |- stages/
|     |  |- scan/
|     |  |  |- prompt.md
|     |  |  |- raw.md
|     |  |  `- result.json
|     |  |- intake/
|     |  |- spec/
|     |  |- plan/
|     |  |- review-lite/
|     |  |- execute/
|     |  `- verify/
|     `- errors/
|        `- <stage>-parse-error.json
|- runs/
|  `- <run_id>/
|     |- run.json
|     |- commands.jsonl
|     |- files.jsonl
|     |- guards.jsonl
|     `- tests.jsonl
`- memory/
   |- active-work.json
   |- run-index.json
   |- open-items.json
   `- resume-snapshot.md
```

The plan root contains official work contracts and final stage outputs that are
useful to humans and later stages. The `stages/` directory contains per-stage
process records:

- `prompt.md`: prompt prepared by Runner for that stage worker
- `raw.md`: raw worker response captured by the parent Codex session
- `result.json`: parsed and validated stage result

The `errors/` directory contains parse or validation failure records. Runner
keeps backward-compatible readers for older flat plan directories, but new
plans should use the grouped layout.

The `runs/` directory contains work execution records. It stores compact run
summaries and append-only command, file, guard, and test records. Test records
come from structured stage artifacts such as `verification-result.json`, not
from command-name guessing in hooks.

The `memory/` directory is the first resume surface. Agents should read
`resume-snapshot.md` before raw run or evidence logs when context is unclear.

## CLI Surface

Installed Codex projects should call the project-local shim:

- `.logos/bin/logos-runner.cmd doctor`
- `.logos/bin/logos-runner.cmd start`
- `.logos/bin/logos-runner.cmd run`
- `.logos/bin/logos-runner.cmd run-stage`
- `.logos/bin/logos-runner.cmd record-stage`
- `.logos/bin/logos-runner.cmd gate`
- `.logos/bin/logos-runner.cmd answer`
- `.logos/bin/logos-runner.cmd continue`
- `.logos/bin/logos-runner.cmd execute`
- `.logos/bin/logos-runner.cmd verify`
- `.logos/bin/logos-runner.cmd status`
- `.logos/bin/logos-runner.cmd report`

The PowerShell shim `.logos/bin/logos-runner.ps1` is also installed, but the
`.cmd` shim is the default on Windows because it avoids PowerShell execution
policy blockers.

## Installed Codex Flow

```text
logos install --target codex-cli --root <project>
.\.logos\bin\logos-runner.cmd doctor --root .
.\.logos\bin\logos-runner.cmd start --root . "<request>"
.\.logos\bin\logos-runner.cmd next --root . <plan_id>
Codex native subagent executes the prepared stage prompt
.\.logos\bin\logos-runner.cmd record-stage --root . <plan_id> <stage> --file <json_file>
.\.logos\bin\logos-runner.cmd gate --root . <plan_id> <stage> --apply
```
