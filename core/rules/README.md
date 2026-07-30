---
id: logos.reference.rules-overview
kind: reference
name: rules-overview
description: Overview of Logos soft rule assets and conditional rule use.
status: active
version: 0.1.0
---

# Rule Assets

`core/rules/` contains soft model policy. Rules guide agent behavior, but they do
not guarantee runtime enforcement. Hard enforcement belongs in `core/guards/`
and target hook or Runner code.

Rules should be compact enough to inject or read on demand. Do not assemble all
rule bodies into `AGENTS.md` or the Nous skill by default. Use frontmatter such
as `always_apply`, `stages`, `globs`, and `related_guards` to decide when a rule
is relevant.

Use `references/` for detailed examples and edge cases. A compact rule card must
remain useful without reading its reference.
