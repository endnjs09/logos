# Codex CLI Target

This target contains Logos assets intended to be installed onto Codex CLI.

Codex CLI is a primary compatibility target for Logos research. It lets Logos
compare target behavior while reusing the same core assets, prompt assembly,
session state, manifests, and doctor checks.

Nous Mode is the default after install for Codex projects. State is stored in
`.logos/session/nous-state.json` with `nous_mode: true`, while durable behavior
is carried by `AGENTS.md`, the single repo skill `.agents/skills/nous/SKILL.md`,
and step procedures under `.agents/logos/procedures/`.

Codex target behavior is routed through Nous first. Use uninstall as the
off-ramp when a project should no longer use Logos behavior.
