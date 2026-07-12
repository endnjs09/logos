# ADR 001: Project Structure

## Status

Accepted.

## Decision

Logos uses a complete final structure with incremental implementation.

Runtime code lives under `packages/`, split by package responsibility:
`logos-core`, `logos-installer`, `logos-gemini`, and `logos-eval`. Core
instruction assets live under `core/`. Target installation assets live under
`targets/`. Schemas live under `schemas/`. Benchmark inputs live under
`benchmarks/`. Run artifacts live under `runs/`, and comparison reports live
under `reports/`.

`src/logos/cli` is retained only as a compatibility shim for older module
entrypoints. New runtime implementation belongs in `packages/`.

## Rationale

The project goal is not to wrap Gemini. The goal is to compensate for Gemini's
coding-agent weaknesses through orchestration: planning, exploration, gap
analysis, plan review, context handoff, execution, verification, retry policy,
and measurement.
