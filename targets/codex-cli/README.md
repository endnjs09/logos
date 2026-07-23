# Codex CLI Target

This target contains Logos assets intended to be installed onto Codex CLI.

Codex CLI is the primary implementation target for current Logos research. It
lets Logos reuse the same core assets, prompt assembly, session state,
manifests, and doctor checks while relying on Codex's native project
instructions, config, sandbox, approvals, hooks, skills, MCP, and subagent
surfaces.

Nous Mode is the default after install for Codex projects. State is stored in
`.logos/session/nous-state.json` with `nous_mode: true`, while durable behavior
is carried by `AGENTS.md`, the single repo skill `.agents/skills/nous/SKILL.md`,
and step procedures under `.agents/logos/procedures/`.

Codex target behavior is routed through Nous first. Use uninstall as the
off-ramp when a project should no longer use Logos behavior.

See:

- `docs/targets/codex-cli/capabilities.md`
- `docs/targets/codex-cli/guard-mapping.md`
