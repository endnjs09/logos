# Logos Plugins

Logos plugins are external harness packs that add Gemini calibration capability
without changing the core runtime.

They are inspired by Claude Code plugins, but are scoped to Logos' purpose:
lifting Gemini Pro High behavior through better instructions, roles, guards,
workflows, tools, and evaluation assets.

## Structure

```text
plugin-name/
├─ .logos-plugin/
│  └─ plugin.toml
├─ commands/
├─ roles/
├─ skills/
├─ hooks/
├─ guards/
├─ prompts/
├─ workflows/
├─ benchmarks/
├─ schemas/
└─ README.md
```

All directories except `.logos-plugin/` are optional.

## Directories

- `builtin`: first-party plugins maintained with Logos.
- `external`: locally installed or third-party plugins.
- `examples`: example plugin layouts for plugin authors.

## Initial Policy

Plugin loading is not implemented in v0. The directory and manifest schema exist
to keep the extension boundary stable before runtime support is added.
