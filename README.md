# Logos

Logos is a performance calibration harness for lifting Gemini Pro High 3.1
toward Codex and Claude Code level coding-agent behavior.

The project is intentionally structured for the final architecture first, while
implementation is expected to arrive through staged versions. The goal is not a
small wrapper around Gemini. Logos is an orchestration harness with planning,
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
compatibility shim  -> src/logos/cli
```

## Runtime Packages

Logos runtime code is split by package boundary:

- `packages/logos-core`: asset scanning, frontmatter validation, manifests,
  prompt assembly, workflow primitives, guard models, context models, and shared
  configuration.
- `packages/logos-installer`: `logos install`, `uninstall`, `doctor`,
  `status`, and Nous session-state commands.
- `packages/logos-gemini`: Gemini CLI adapter, mode activation, injection,
  hooks, runtime state, evidence, approvals, checkpoints, and target guards.
- `packages/logos-eval`: baseline comparison, benchmark runs, measurement
  logs, scoring, reports, and reproducibility records.

`src/logos/cli` is kept only as a compatibility shim for older
`python -m logos.cli.main` entrypoints. New runtime code should be added under
`packages/`.

## Core Assets

`core/` contains built-in code-adjacent assets, not runtime implementation:

- `roles`: planner, explorer, gap analyzer, plan reviewer, executor, tester, reviewer.
- `rules`: mode, override, verification, context, and retry rules.
- `workflows`: Low, Middle, and High workflow definitions.
- `prompts`: markdown prompts used by role prompt assembly.
- `guards`: high-risk override, excluded scope, required fields, context budget.
- `host_profiles`: Gemini, Codex, and Claude Code host behavior profiles.

## Plugins

`plugins/` is reserved for external harness packs. A Logos plugin can add or
override commands, roles, skills, hooks, guards, prompts, workflows, benchmark
tasks, schemas, or evaluator rubrics without changing Logos core runtime.

Plugin loading is intentionally disabled at scaffold time. The structure and
manifest contract exist now so later calibration packs can be added without
redesigning the project.

## Targets

`targets/` contains host-mounted packaging assets for supported CLI hosts.

- `targets/gemini-cli`: primary target for Gemini Pro High calibration.
- `targets/codex-cli`: compatibility and baseline reference target.

Targets are not model implementations. They are installation surfaces that map
Logos core assets into each CLI host's command, prompt, hook, tool, and template
format.

## Implementation Strategy

Structure is complete from the start. Implementation is incremental:

1. v1: installer, doctor, target templates, Nous session state, and asset
   validation.
2. v2: core asset scanning, prompt assembly, manifests, and Gemini adapter
   reality checks.
3. v3: guard runtime, approvals, checkpoints, evidence, and hook emulation.
4. v4: workflow orchestration, role routing, context handoff, and retry policy.
5. v5: evaluator, measurement logs, benchmark suite, and reproducibility.
6. v6: Codex and Claude Code baseline automation.
