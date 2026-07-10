# Plugin Reference

Logos plugins are harness extension packs.

They may provide commands, roles, skills, hooks, guards, prompts, workflows,
benchmarks, schemas, or evaluator assets. A plugin is recognized by its manifest:

```text
.logos-plugin/plugin.toml
```

Plugin loading is disabled in v0. The manifest contract and directory structure
exist first so the extension boundary remains stable.
