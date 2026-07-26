# ADR 001: Project Structure

## Status

Accepted.

## Decision

Logos uses a complete final structure with incremental implementation.

Runtime code lives under `packages/`, split by package responsibility:
`logos-core`, `logos-installer`, `logos-runner`, and `logos-eval`. Core
instruction assets live under `core/`. Target installation assets live under
`targets/`. Schemas live under `schemas/`. Benchmark inputs live under
`benchmarks/`. Run artifacts live under `runs/`, and comparison reports live
under `reports/`.

## Rationale

The project goal is not to replace Codex CLI. The goal is to mount a structured
orchestration layer onto Codex projects: planning, exploration, gap analysis,
plan review, context handoff, execution, verification, retry policy, run memory,
and evidence capture.
