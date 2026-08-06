# Logos

Logos is a Codex CLI orchestration harness for structured coding-agent work.

The project is intentionally structured for the final architecture first, while
implementation is expected to arrive through staged versions. Logos is an
orchestration harness with planning,
gap analysis, plan review, context handoff, execution, verification, retry
policy, telemetry, and benchmark comparison.

## Structure Rule

```text
core assets         -> core
runtime packages    -> packages
target assets       -> targets
plugin assets       -> plugins
schemas/contracts   -> schemas
benchmark inputs    -> benchmarks
run artifacts       -> runs
comparison output   -> reports
design rationale    -> docs
```

## Runtime Packages

Logos runtime code is split by package boundary:

- `packages/logos-core`: asset scanning, frontmatter validation, manifests,
  prompt assembly, workflow primitives, guard models, context models, and shared
  configuration.
- `packages/logos-installer`: `logos install`, `uninstall`, `doctor`,
  `status`, and Nous session-state commands.
- `packages/logos-runner`: Codex Runner orchestration, stage prompts, gates,
  work-state records, and native subagent handoff.
- `packages/logos-eval`: baseline comparison, benchmark runs, measurement
  logs, scoring, reports, and reproducibility records.

## Core Assets

`core/` contains built-in code-adjacent assets, not runtime implementation:

- `roles`: planner, explorer, gap analyzer, plan reviewer, executor, tester, reviewer.
- `rules`: mode, override, verification, context, and retry rules.
- `workflows`: Low, Middle, and High workflow definitions.
- `prompts`: markdown prompts used by role prompt assembly.
- `guards`: high-risk override, excluded scope, required fields, context budget.
- `host_profiles`: Codex host behavior profiles.

## Plugins

`plugins/` is reserved for external harness packs. A Logos plugin can add or
override commands, roles, skills, hooks, guards, prompts, workflows, benchmark
tasks, schemas, or evaluator rubrics without changing Logos core runtime.

Plugin loading is intentionally disabled at scaffold time. The structure and
manifest contract exist now so later calibration packs can be added without
redesigning the project.

## Targets

`targets/` contains host-mounted packaging assets for supported CLI hosts.

- `targets/codex-cli`: primary and only active target.

Targets are not model implementations. They are installation surfaces that map
Logos core assets into each CLI host's command, prompt, hook, tool, and template
format.

