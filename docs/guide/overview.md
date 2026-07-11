# Overview

Logos is a host-mounted calibration harness for AI coding CLIs.

Its primary goal is to improve Gemini Pro High behavior through structured
planning, context control, tool discipline, verification, and measurement. Logos
does not replace Gemini CLI or Codex CLI. It mounts a harness onto them.

## What Logos Is

Logos is:

- a package of commands, prompts, roles, rules, guards, workflows, and tools
- an installer for supported CLI targets
- a measurement harness for comparing Gemini baseline with Gemini + Logos
- a plugin-ready structure for future calibration packs

Logos is not:

- a standalone IDE
- a web app
- a new model runtime
- a replacement for Gemini CLI
- a replacement for Codex CLI

## Main Concepts

`core`  
Built-in Logos assets shared across targets.

`targets`  
Installation surfaces for Gemini CLI and Codex CLI.

`plugins`  
Optional calibration packs that extend core behavior.

`schemas`  
Contracts for configuration, targets, plugins, benchmarks, runs, and reports.

`benchmarks`  
Repeatable tasks used to measure behavior.

`runs`  
Per-run artifacts and logs.

`reports`  
Comparison output across benchmark conditions.

## Expected Flow

```text
install Logos onto a target
→ run a task or benchmark
→ assemble core and plugin assets
→ guide the host through a workflow
→ execute tools under control
→ verify the result
→ write run artifacts
→ compare conditions
```

## Calibration Strategy

Logos improves behavior by adding structure around the host:

- separate planning from execution
- require code evidence
- ask clarifying questions before risky implementation
- generate task plans and specs
- pass compressed context to executor roles
- verify results against success criteria
- classify failures before retrying
- record measurements for comparison

## Reading Order

For maintainers:

1. `README.md`
2. `docs/reference/markdown-authoring.md`
3. `docs/reference/targets.md`
4. `docs/reference/plugins.md`
5. `docs/reference/benchmark-format.md`
6. `docs/reference/run-log-format.md`
7. `docs/decisions/*.md`

