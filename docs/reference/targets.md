# Targets Reference

Targets are CLI hosts that Logos can mount onto.

Targets are not implemented by Logos. Logos adapts core assets and plugins into
target-specific commands, prompts, hooks, tools, templates, and installation
steps.

## Supported Targets

Current targets:

- `codex-cli`: primary implementation target.
- `gemini-cli`: fallback and experimental target.

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
| `experimental` | Target host documents the surface, but marks it as subject to change |
| `reported` | A non-official source reports the surface, but Logos has not verified it |
| `assumed` | Designed but not verified against the target host |
| `unknown` | Verification has not been attempted or was inconclusive |
| `unsupported` | Target host cannot support or emulate the surface |
| `not_used` | Logos intentionally does not use the surface for this target |

Runtime guarantees may rely only on `confirmed` or `emulated` surfaces.
`experimental` surfaces may be used only with warning and explicit fallback
planning. `reported`, `assumed`, and `unknown` surfaces are not runtime
guarantees and must be recorded in benchmark metadata if included.
`unsupported` surfaces must not be included in active target assembly.

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
The main implementation target. Currently `codex-cli`.

`baseline`  
A comparison target used to measure performance gaps.

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
- using Codex's confirmed config, sandbox, approval, hook, skill, MCP, and
  subagent surfaces
- routing durable behavior through `AGENTS.md`, `nous/SKILL.md`, and
  `.agents/logos/procedures/`
- mapping Logos guards to Codex hooks and approval boundaries before claiming
  hard enforcement

Codex is the current primary implementation target. Gemini CLI remains a
fallback and experimental target.

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
