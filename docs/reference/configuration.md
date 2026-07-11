# Configuration Reference

This document defines the principles for Logos configuration files.

Logos configuration must be boring, explicit, and auditable. Configuration should
describe where assets live, which targets are supported, which policies are
enabled, and where run artifacts are written. It should not hide workflow logic
that belongs in `core/workflows`, `core/rules`, or plugins.

## Configuration Sources

Logos configuration is expected to come from these sources:

| Source | Purpose |
|---|---|
| `logos.toml` | Project-level Logos configuration and path registry. |
| `.env` | Local secrets and machine-specific values. Not committed. |
| `.env.example` | Documented environment variable names. No secrets. |
| `core/**/*.yaml` | Built-in roles, guards, workflows, and profiles. |
| `targets/*/.logos-target/target.toml` | Target metadata for Gemini CLI and Codex CLI. |
| `plugins/*/.logos-plugin/plugin.toml` | Plugin metadata and provided assets. |
| `schemas/*.schema.json` | Contract definitions for validation. |

## Configuration Layering

Configuration should be layered in this order:

1. Built-in defaults in code.
2. `logos.toml`.
3. Target manifests.
4. Plugin manifests.
5. Environment variables.
6. Explicit CLI arguments.

Later layers may override earlier layers only when the override is intentional
and visible in logs.

## `logos.toml`

`logos.toml` is the top-level project configuration.

It should define:

- project identity
- architecture mode
- path registry
- supported targets
- supported benchmark conditions
- mode defaults
- logging defaults
- safety defaults
- plugin discovery policy

It should not define:

- full prompts
- role behavior
- workflow stage internals
- benchmark task details
- target-specific installation templates
- secrets

## Path Rules

All configured paths should be relative to the repository root unless explicitly
documented otherwise.

Good:

```toml
[paths]
core_assets = "core"
targets = "targets"
plugins = "plugins"
runs = "runs"
reports = "reports"
```

Avoid:

```toml
[paths]
core_assets = "C:/Users/someone/private/path"
```

Absolute paths make experiments harder to reproduce.

## Target Configuration

Targets represent installation destinations, not model implementations.

Supported targets:

- `gemini-cli`
- `codex-cli`

Target-specific information belongs in:

```text
targets/<target>/.logos-target/target.toml
targets/<target>/commands/
targets/<target>/prompts/
targets/<target>/hooks/
targets/<target>/tools/
targets/<target>/templates/
targets/<target>/install/
```

Do not put Gemini CLI-specific prompt behavior in `core/`. Put it under
`targets/gemini-cli`.

## Plugin Configuration

Plugin loading is disabled in the scaffold stage.

When enabled later, plugin loading must:

- validate plugin manifests
- record plugin load order
- reject malformed manifests
- reject unknown asset directories unless explicitly allowed
- record every plugin that contributes assets to a run
- distinguish built-in plugins from external plugins

Plugin configuration belongs in:

```text
plugins/<plugin>/.logos-plugin/plugin.toml
```

## Environment Variables

`.env.example` documents variable names. `.env` contains local values and must
not be committed.

Environment variables should be used for:

- API keys
- local target paths
- local runtime flags
- optional debug behavior

Environment variables should not define workflow policy. Policy belongs in core
rules, target assets, or plugin assets.

## Safety Configuration

Safety configuration should default to conservative behavior.

High-risk domains include:

- auth
- authorization
- billing
- payments
- data deletion
- database migration
- secrets
- production deployment

If a user asks for override in a high-risk domain, the override should be
blocked or escalated according to `core/rules/override-policy.md` and
`core/guards/high-risk-override.yaml`.

## Validation Rules

Configuration validation should check:

- required sections exist
- configured paths exist or can be created
- supported targets are known
- default target is supported
- benchmark conditions are known
- mode values are one of `low`, `middle`, `high`
- plugin manifests are valid when plugin loading is enabled
- target manifests are valid
- run/report directories are writable

## Logging Requirements

Every run should record:

- loaded config file path
- target
- condition
- enabled plugins
- selected mode
- final mode
- safety overrides
- resolved paths

Configuration decisions must be reproducible from the run artifacts.

## Change Rules

When changing configuration format:

- update the relevant schema
- update this document
- update examples
- update validation tests
- add an ADR if the change affects architecture

