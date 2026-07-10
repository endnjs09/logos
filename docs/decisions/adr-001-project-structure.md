# ADR 001: Project Structure

## Status

Accepted.

## Decision

Logos uses a complete final structure with incremental implementation.

Runtime code lives under `src/logos`. Harness assets live under `harness`.
Schemas live under `schemas`. Benchmark inputs live under `benchmarks`. Run
artifacts live under `runs`, and comparison reports live under `reports`.

## Rationale

The project goal is not to wrap Gemini. The goal is to compensate for Gemini's
coding-agent weaknesses through orchestration: planning, exploration, gap
analysis, plan review, context handoff, execution, verification, retry policy,
and measurement.
