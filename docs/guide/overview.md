# Overview

Logos is a Codex CLI-mounted orchestration harness for AI coding work.

Its primary goal is to make Codex-driven coding work more structured,
auditable, and recoverable through planning, role routing, context control,
tool discipline, verification, and run memory. Logos does not replace Codex CLI.
It installs instructions, hooks, procedures, and runner shims onto Codex
projects.

## What Logos Is

Logos is:

- a package of prompts, roles, rules, guards, workflows, hooks, and runner tools
- an installer for the supported Codex CLI target
- a runner-assisted workflow for intake, scan, spec, plan, execution, and
  verification
- a plugin-ready structure for future calibration packs

Logos is not:

- a standalone IDE
- a web app
- a new model runtime
- a replacement for Codex CLI

## Main Concepts

`core`  
Built-in Logos assets shared by generated instructions and runner prompts.

`targets`  
Installation surfaces for Codex CLI.

`plugins`  
Optional calibration packs that extend core behavior.

`schemas`  
Contracts for configuration, targets, plugins, benchmarks, runs, and reports.

`benchmarks`  
Repeatable tasks used to measure behavior.

`.logos/plans`  
Per-task planning artifacts, stage prompts, raw worker output, and normalized
stage results.

`.logos/runs`  
Run-level evidence and execution state.

`.logos/memory`  
Compact resume summaries for long or interrupted tasks.

## Expected Flow

```text
install Logos onto a Codex project
-> run a coding task through Nous
-> create or resume a Logos plan
-> route Codex through scan, intake, spec, plan, execution, and verification
-> execute tools under Codex sandbox and approval controls
-> write plan, run, memory, and evidence artifacts
```

## Calibration Strategy

Logos improves behavior by adding structure around Codex:

- separate planning from execution
- require code evidence
- ask clarifying questions before risky or under-specified implementation
- generate task plans and specs
- pass compressed context to executor roles
- verify results against success criteria
- classify failures before retrying
- record durable memory and evidence for resume and review

## Reading Order

For maintainers:

1. `README.md`
2. `docs/reference/markdown-authoring.md`
3. `docs/reference/frontmatter-reference.md`
4. `docs/reference/document-types.md`
5. `docs/reference/instruction-authoring.md`
6. `docs/reference/targets.md`
7. `docs/reference/plugins.md`
8. `docs/reference/benchmark-format.md`
9. `docs/reference/run-log-format.md`
10. `docs/decisions/*.md`
