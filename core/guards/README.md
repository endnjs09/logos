---
id: logos.reference.guards-overview
kind: reference
name: guards-overview
description: Overview of Logos guard policy assets and their runtime relationship.
status: active
version: 0.1.0
---

# Guard Policy Assets

`core/guards/` is the source of truth for runtime safety policy. Guard assets are
not long prompt instructions. They define the behavior that Codex hooks, Logos
Runner, generated manifests, and native Codex approval surfaces must implement
or report honestly.

Use guard YAML files for machine-readable policy:

- `enforcement_status: policy-only` means the policy is defined but not wired.
- `enforcement_status: implemented` means a hook, Runner path, or Codex target
  surface exists.
- `enforcement_status: verified` means implementation evidence proves that the
  guard fires as intended.

Installed projects receive generated guard manifests and Codex hook scripts.
They do not receive the entire guard policy library as agent context.
