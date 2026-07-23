# Codex Execpolicy Position

This document records the V8-2-B decision for Codex `execpolicy`.

## Decision

Logos does not install project execpolicy rules by default in V8.

Codex documents execpolicy as an experimental command policy surface. It can
classify command prefixes as:

- `allow`
- `prompt`
- `forbidden`

Codex applies the most restrictive matching rule and provides
`codex execpolicy check` to test rule files. This makes execpolicy promising for
native command gating, but it should not be the only V8 enforcement path until
Logos has a stable target contract and end-to-end evidence.

## Logos Use

Default V8 behavior:

- Keep `approval_policy = "on-request"`.
- Keep `sandbox_mode = "workspace-write"`.
- Use Logos hooks for concise warnings, approval notes, pointers, and evidence.
- Do not grow a broad Logos shell-command denylist as the primary safety model.

Optional future behavior:

- Add an opt-in execpolicy rules file for narrow command classes.
- Use `prompt` for commands that should go through Codex native approval.
- Use `forbidden` only for tightly scoped, well-tested categories.
- Validate every rule with `codex execpolicy check` before installation.

## Why Not Default

- The surface is documented as experimental.
- Shell wrappers and compound commands still need careful testing.
- Logos already relies on Codex sandbox and approval as the primary execution
  safety boundary.
- V8 is focused on guardrails that are cheap, narrow, and easy to reason about.

## Status

```text
execpolicy rules = experimental / optional
default Logos install = not enabled
```
