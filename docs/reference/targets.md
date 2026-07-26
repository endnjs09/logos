# Targets Reference

Targets are CLI hosts that Logos can mount onto.

Targets are not implemented by Logos. Logos adapts core assets and plugins into
target-specific prompts, hooks, tools, templates, runner shims, and installation
steps.

## Supported Targets

Current target:

- `codex-cli`: primary and only active implementation target.

## Target Manifest

Each target has:

```text
targets/<target>/.logos-target/target.toml
```

The manifest should define:

- target name
- target kind
- description
- target support status for commands, skills, hooks, approvals, sandbox,
  subagents, MCP, and other host-dependent surfaces
- provided asset directories

## Target Support Reality Check

Target manifests must distinguish desired Logos behavior from confirmed target
host behavior.

Use `target_support` for every host-dependent surface:

```toml
[target_support.hooks]
status = "confirmed"
notes = "Codex can run configured hook commands."

[target_support.approval]
status = "confirmed"
notes = "Codex owns final approval prompts."

[target_support.runner]
status = "emulated"
notes = "Logos installs runner shims under .logos/bin."
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
guarantees. `unsupported` surfaces must not be included in active target
assembly.

## Target Directory Shape

```text
targets/codex-cli/
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

## Codex CLI Target

The Codex CLI target should emphasize:

- preserving Codex's native coding strengths
- using Codex's confirmed config, sandbox, approval, hook, skill, MCP, and
  subagent surfaces
- routing durable behavior through `AGENTS.md`, `nous/SKILL.md`, and
  `.agents/logos/`
- using Logos Runner artifacts under `.logos/plans`, `.logos/runs`,
  `.logos/memory`, and `.logos/evidence`
- mapping Logos guards to Codex hooks and approval boundaries before claiming
  hard enforcement

## Target Assets

`commands/`  
Target-specific command surfaces when supported.

`prompts/`  
Target-specific prompt wrappers and runner prompt fragments.

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

Before adding or changing target assets:

- Is this an installation target, not a new runtime engine?
- Is the manifest valid?
- Are target-specific files isolated under `targets/codex-cli`?
- Are core policies left in `core/`?
- Are target limitations documented?
- Are `target_support` statuses explicit for skills, hooks, approvals,
  sandbox, subagents, tools, and context injection?
- Are assumed surfaces excluded from runtime guarantees?
- Can the installer and doctor verify the generated project shape?
