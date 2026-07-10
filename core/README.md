# Harness Assets

This directory contains the assets that shape host-agent behavior.

These files are intentionally outside runtime code so that role prompts, rules,
guards, and host profiles can evolve without changing Python implementation.

## Directories

- `roles`: role definitions for planner, explorer, gap analyzer, plan reviewer, executor, tester, and reviewer.
- `rules`: written policy rules for mode selection, override, verification, context handoff, and retry.
- `workflows`: Low, Middle, and High workflow definitions.
- `prompts`: markdown prompt bodies used by role prompt assembly.
- `guards`: machine-readable guard definitions.
- `host_profiles`: host-specific behavior and limitation profiles.
