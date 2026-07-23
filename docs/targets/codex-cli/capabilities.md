# Codex CLI Capabilities

This document records the Codex CLI surfaces that Logos may rely on for the
Codex target.

## Purpose

V7 fixes the difference between desired Logos behavior and confirmed Codex host
behavior. A Logos guard may claim runtime enforcement only when it is mapped to
a confirmed, emulated, or explicitly experimental Codex surface and backed by
Logos implementation code.

## Status Values

| Status | Meaning |
|---|---|
| `confirmed` | Codex officially supports the surface |
| `emulated` | Logos provides the behavior through installed files, scripts, or workflow routing |
| `experimental` | Codex officially documents the surface, but marks it as subject to change |
| `reported` | Non-official source reports the surface, but Logos has not verified it |
| `assumed` | Logos design expects the surface, but it is not verified |
| `unknown` | Verification has not been attempted or was inconclusive |
| `unsupported` | Codex does not support the surface and Logos cannot emulate it safely |
| `not_used` | The surface may exist, but Logos does not use it for this target |

## Confirmed Surfaces

| Surface | Status | Logos Use |
|---|---|---|
| `AGENTS.md` | `confirmed` | Durable repo-level routing into Logos Nous workflow |
| `.codex/config.toml` | `confirmed` | Project-scoped Codex settings for trusted repositories |
| `approval_policy` | `confirmed` | Default approval behavior for sandbox escalation and permission prompts |
| `sandbox_mode` | `confirmed` | Filesystem and command execution sandbox boundary |
| `sandbox_workspace_write.network_access` | `confirmed` | Default network-deny posture for workspace-write sessions |
| `hooks` | `confirmed` | Lifecycle entrypoint for Logos guard scripts |
| `PreToolUse` | `confirmed` | Inspect local tool calls before execution |
| `PostToolUse` | `confirmed` | Inspect local tool results and record evidence after execution |
| `PermissionRequest` | `confirmed` | Review approval requests before a permission boundary is crossed |
| `UserPromptSubmit` | `confirmed` | Inspect submitted user prompts for sensitive data or mode context |
| `Stop` | `confirmed` | Run final validation or continuation checks when a turn stops |
| `MCP` | `confirmed` | Attach external tools and context servers through Codex config |
| `MCP tool approval` | `confirmed` | Control MCP tool prompting, allow lists, and deny lists |
| `skills` | `confirmed` | Install the Nous skill as the only auto-discoverable Logos skill |
| `subagents` | `confirmed` | Future role delegation path for specialized Logos work |
| `plugin-bundled hooks` | `confirmed` | Future distribution path for Logos as a Codex plugin |
| `execpolicy rules` | `experimental` | Optional command prefix allow, prompt, or forbidden policy; not installed by default in V8 |
| `PreToolUse hard deny output` | `reported` | OMO-observed `permissionDecision = "deny"` shape; Logos probe exists but runtime result is not confirmed |
| `procedures` | `emulated` | Logos step documents routed through `nous/SKILL.md` |
| `session_state` | `emulated` | Logos mode and run state stored under `.logos/session/` |
| project-local commands | `not_used` | Codex target uses `AGENTS.md`, skills, and hooks instead |

## Procedure Kind Scope

`procedure` is a global Logos document kind, not a Codex-only kind.

Codex makes the pattern especially useful because Logos installs only
`.agents/skills/nous/SKILL.md` as an auto-discoverable Codex skill. Step-level
documents live under `.agents/logos/procedures/` so Codex routes through the
Nous director first instead of treating every step as an independent skill.

Other targets may install multiple native skills when that host benefits from
that shape. They are not required to use the Codex procedure pattern unless it
improves routing, context hygiene, or host compatibility.

## Important Limits

- Project-local `.codex/config.toml`, hooks, and rules load only when the Codex
  project layer is trusted.
- Non-managed command hooks must be reviewed and trusted before Codex runs them.
- `PreToolUse` and `PostToolUse` cover local tool paths such as shell commands,
  `apply_patch`, MCP tools, and most local function tools. Hosted tools such as
  WebSearch do not use the same local hook path.
- `PreToolUse` is a useful guardrail but not a complete enforcement boundary.
  Logos must not claim complete hard enforcement from hook presence alone.
- V8 project hooks currently use concise `systemMessage` output for warnings
  and approval notes. Hard denial requires a separately verified Codex
  `PreToolUse` deny output or native `execpolicy` rule.
- The hard-deny probe is documented in
  `docs/targets/codex-cli/hard-deny-probe.md`.
- `execpolicy rules` are documented as experimental, so they may support
  command guard work but should not be the only enforcement path.
- The V8 execpolicy position is documented in
  `docs/targets/codex-cli/execpolicy.md`.

## Hook Trust Model

Project-local Logos hooks are not automatically trusted just because the Logos
installer writes them. Codex requires non-managed command hooks to be reviewed
and trusted before they run, and trust is tied to the current hook definition.

Implications for Logos:

- V8 hook installation must document the user trust step.
- A changed hook script or hook definition may require trust review again.
- Logos must not treat an installed hook file as active enforcement until Codex
  has loaded and trusted that hook.
- Managed hooks or plugin-bundled hooks may have different trust paths, but they
  still need explicit target documentation before Logos claims enforcement.

## V8 Implication

The Codex target should combine:

```text
Codex config and sandbox
Codex hooks
PermissionRequest
optional execpolicy rules
Logos guard scripts
Logos doctor and evidence checks
```

This gives Logos a practical enforcement path without pretending that prompt
instructions alone are hard guards.

For guard-by-guard implementation mapping, see
`docs/targets/codex-cli/guard-mapping.md`.
