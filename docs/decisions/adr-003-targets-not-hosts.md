# ADR 003: Targets, Not Hosts

## Status

Accepted.

## Decision

Logos uses `targets/` instead of `hosts/` for Gemini CLI and Codex CLI
integration assets.

## Rationale

Gemini CLI and Codex CLI are not implemented by Logos. They are installation
targets. Logos mounts commands, prompts, hooks, tools, and templates onto those
existing CLI hosts.
