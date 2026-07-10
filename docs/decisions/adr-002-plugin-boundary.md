# ADR 002: Plugin Boundary

## Status

Accepted.

## Decision

Logos will support plugins as external harness packs. The initial structure
includes `plugins/`, `src/logos/plugins/`, and
`schemas/plugin-manifest.schema.json`, but runtime plugin loading is deferred.

## Rationale

Logos needs to improve Gemini through replaceable calibration assets: commands,
roles, skills, hooks, guards, prompts, workflows, benchmarks, schemas, and
evaluators. Keeping these as plugins allows new calibration strategies without
modifying the core runtime.
