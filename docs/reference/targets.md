# Targets Reference

Targets are CLI hosts that Logos can mount onto.

Targets are not implemented by Logos. Logos adapts core assets and plugins into
target-specific commands, prompts, hooks, tools, templates, and installation
steps.

## Supported Targets

Current targets:

- `gemini-cli`: primary calibration target.
- `codex-cli`: compatibility and baseline target.

## Target Manifest

Each target has:

```text
targets/<target>/.logos-target/target.toml
```

The manifest should define:

- target name
- target kind
- description
- target support status for commands, plugin loading, lifecycle hooks, and other
  host-dependent surfaces
- provided asset directories

## Target Support Reality Check

Target manifests must distinguish desired Logos behavior from confirmed target
host behavior.

Use `target_support` for every host-dependent surface:

```toml
[target_support.commands]
status = "confirmed"
notes = "Target supports project commands."

[target_support.plugin]
status = "assumed"
notes = "Plugin loading behavior still needs verification."

[target_support.before_tool]
status = "emulated"
notes = "Logos adapter intercepts tool requests before forwarding."

[target_support.after_tool]
status = "assumed"
notes = "Native lifecycle support is not confirmed."
```

Allowed status values:

| Status | Meaning |
|---|---|
| `confirmed` | Target host natively supports the surface |
| `emulated` | Logos can implement the surface through a wrapper, adapter, or command |
| `assumed` | Designed but not verified against the target host |
| `unsupported` | Target host cannot support or emulate the surface |

Runtime guarantees may rely only on `confirmed` or `emulated` surfaces.
`assumed` surfaces are design assumptions and must be recorded in benchmark
metadata if included. `unsupported` surfaces must not be included in active
target assembly.

## Target Directory Shape

```text
targets/<target>/
+-- .logos-target/
|   +-- target.toml
+-- commands/
+-- prompts/
+-- hooks/
+-- tools/
+-- templates/
+-- install/
+-- README.md
```

## Target Kinds

`primary`  
The main calibration target. Currently `gemini-cli`.

`baseline`  
A comparison target used to measure performance gaps. Currently `codex-cli`.

`compatibility`  
A target supported to prove portability, but not the primary focus.

## Gemini CLI Target

The Gemini CLI target should emphasize:

- strict planning before execution
- code evidence collection
- mode fit checks
- context handoff
- explicit verification
- retry discipline
- measurement logging

Gemini-specific prompts should compensate for:

- scope drift
- weak plan following
- overconfident verification
- context sensitivity

## Codex CLI Target

The Codex CLI target should emphasize:

- preserving Codex's native coding strengths
- consistent benchmark comparison
- minimal unnecessary prompt interference
- compatibility with Logos artifacts

Codex is a baseline and compatibility target, not the main calibration subject.

## Target Assets

`commands/`  
Target-specific command surfaces.

`prompts/`  
Target-specific prompt wrappers.

`hooks/`  
Target lifecycle integrations.

`tools/`  
Target-specific tool shims or bridge configuration.

`templates/`  
Files rendered by the installer.

`install/`  
Install/uninstall scripts or installation plans.

## Installation Rules

Target installers should:

- inspect target availability
- resolve target config paths
- render templates
- avoid overwriting user files without backup
- report planned changes before writing
- support uninstall where practical
- record installation metadata

## Target Review Checklist

Before adding or changing a target:

- Is this an installation target, not a new runtime engine?
- Is the manifest valid?
- Are target-specific files isolated under `targets/<target>`?
- Are core policies left in `core/`?
- Are target limitations documented?
- Are `target_support` statuses explicit for commands, plugin loading, hooks,
  tools, and context injection?
- Are assumed surfaces excluded from runtime guarantees?
- Can the installer dry-run the changes?
