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
runtime code      -> src/logos
core assets       -> core
plugin assets     -> plugins
schemas/contracts -> schemas
benchmark inputs  -> benchmarks
run artifacts     -> runs
comparison output -> reports
design rationale  -> docs
```

## Runtime Package

`src/logos` is a single Python package with clear internal boundaries:

- `core`: shared primitives, ids, errors, and common domain types.
- `config`: configuration loading and validation.
- `hosts`: Gemini, Codex, Claude Code, and fake host adapters.
- `orchestration`: role-specific intelligence layers that compensate for Gemini.
- `workflow`: v12 Low/Middle/High stage execution.
- `policies`: mode fit, override, retry, quality, and scope policies.
- `context`: context handoff, compression, and token budget control.
- `project_scan`: code evidence, git state, file scan, hash diff, project intent.
- `prompts`: role prompt assembly from harness assets.
- `artifacts`: interview draft, spec, task plan, run result, measurement log.
- `eval`: baseline comparison and benchmark reporting.
- `telemetry`: calls, tokens, retries, failures, and quality measurements.
- `cli`: command surface for run, compare, validate, and inspect.
- `utils`: low-level helpers.

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

## Implementation Strategy

Structure is complete from the start. Implementation is incremental:

1. v1: schemas, fake host, workflow skeleton, measurement logs.
2. v2: Gemini baseline and Gemini + Logos execution comparison.
3. v3: planner, explorer, and context handoff.
4. v4: gap analyzer, plan reviewer, and high-mode review.
5. v5: retry policy, evaluator, benchmark suite hardening.
6. v6: Codex and Claude Code baseline automation.
