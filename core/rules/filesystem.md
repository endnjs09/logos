---
id: logos.rule.filesystem
kind: rule
name: filesystem
description: Applies when reading, creating, editing, moving, or deleting project files.
status: active
version: 0.2.0
enforcement: soft
always_apply: false
stages: [scan, plan, execute, verify]
globs:
  - "**/*"
related_guards:
  - logos.guard.file-write-boundary
detail_reference: .agents/logos/rules/references/filesystem-details.md
---

# Filesystem

## Rule
Read before editing and keep file changes inside the approved task scope.

## Must
- Inspect nearby code before changing behavior.
- Keep edits limited to target files or justified adjacent files.
- Record unexpected file changes as deviations.

## Must Not
- Rewrite unrelated files, metadata, generated output, or user work.
- Use file changes to bypass planning or guard decisions.

## Details
See `.agents/logos/rules/references/filesystem-details.md`.
