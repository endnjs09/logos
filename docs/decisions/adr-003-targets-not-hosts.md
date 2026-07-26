# ADR 003: Targets, Not Hosts

## Status

Accepted.

## Decision

Logos uses `targets/` instead of `hosts/` for Codex CLI integration assets.

## Rationale

Codex CLI is not implemented by Logos. It is an installation target. Logos
mounts prompts, hooks, tools, templates, skills, procedures, and runner shims
onto an existing Codex CLI project.
