# Targets

Targets are supported AI coding CLI hosts that Logos can install onto.

Logos does not replace these hosts. It mounts core assets, plugins, commands,
prompts, hooks, tools, and evaluation helpers onto them.

## Supported Targets

- `gemini-cli`: primary calibration target.
- `codex-cli`: compatibility and baseline target.

## Target Shape

```text
target-name/
├─ .logos-target/
│  └─ target.toml
├─ commands/
├─ prompts/
├─ hooks/
├─ tools/
├─ templates/
├─ install/
└─ README.md
```
