# Plugin Reference

Logos plugins are harness extension packs.

They add calibration capability without changing Logos core runtime. A plugin
may provide commands, roles, skills, hooks, guards, prompts, workflows,
benchmarks, schemas, or evaluator assets.

## Plugin Identity

A plugin is recognized by:

```text
.logos-plugin/plugin.toml
```

The manifest must define at least:

- plugin name
- version
- description
- kind
- provided asset directories

## Plugin Kinds

Recommended plugin kinds:

- `harness-pack`: roles, prompts, guards, workflows.
- `tool-pack`: tool wrappers or MCP/LSP integrations.
- `benchmark-pack`: tasks, fixtures, suites, expected results.
- `evaluator-pack`: metrics, rubrics, report templates.
- `mixed-pack`: multiple categories.

## Plugin Directory Shape

```text
plugin-name/
+-- .logos-plugin/
|   +-- plugin.toml
+-- commands/
+-- roles/
+-- skills/
+-- hooks/
+-- guards/
+-- prompts/
+-- workflows/
+-- benchmarks/
+-- schemas/
+-- README.md
```

Only `.logos-plugin/plugin.toml` is mandatory. All other directories are
optional.

## Plugin Principles

Plugins must be:

- explicit about what they provide
- safe by default
- target-aware when target behavior differs
- auditable in run logs
- removable without breaking core Logos

Plugins must not:

- silently override core behavior
- require secrets in committed files
- assume network access unless declared
- bypass safety guards
- write outside allowed project paths

## Load Order

Initial planned order:

1. Core assets
2. Built-in plugins
3. External plugins
4. CLI overrides

When a plugin overrides or extends an asset, the run log must record it.

## Permissions

Plugins may eventually request permissions:

- tools
- hooks
- filesystem paths
- network
- target-specific install access

Permission requests must be declared in the manifest before runtime support is
implemented.

## Hooks

Plugin hooks should attach to named lifecycle events.

Possible future events:

- `before_config_validate`
- `after_config_validate`
- `before_plan`
- `after_explore`
- `before_execute`
- `after_tool_use`
- `before_verify`
- `on_failure`
- `after_run`

Hooks must be deterministic where possible and must record their effects.

## Plugin README Requirements

Each plugin README should include:

- purpose
- provided assets
- target compatibility
- permissions
- install status
- example usage
- known limitations

## Review Checklist

Before accepting a plugin:

- Does it have a valid manifest?
- Are provided directories declared?
- Is target compatibility clear?
- Are permissions clear?
- Does it avoid silent overrides?
- Are commands/roles/skills written according to `markdown-authoring.md`?
- Can it be disabled without breaking core behavior?
