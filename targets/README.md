# Targets

Targets are supported AI coding CLI hosts that Logos can install onto.

Logos does not replace the host. It mounts core assets, commands, prompts,
hooks, tools, and runtime helpers onto the host's project surface.

## Supported Targets

- `codex-cli`: primary and only active target.

## Target Shape

```text
target-name/
|- .logos-target/
|  `- target.toml
|- commands/
|- prompts/
|- hooks/
|- tools/
|- templates/
|- install/
`- README.md
```
