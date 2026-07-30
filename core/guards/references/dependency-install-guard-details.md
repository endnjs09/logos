---
id: logos.reference.dependency-install-guard-details
kind: reference
name: dependency-install-guard-details
description: Detailed implementation notes for dependency installation policy.
status: active
version: 0.1.0
applies_to:
  - logos.guard.dependency-install-guard
---

# Dependency Install Details

Dependency changes are risky because they alter the trusted code base, lockfile,
build behavior, and transitive supply chain. Avoid relying only on package
manager command names. Cross-check command intent, manifest diffs, lockfile
diffs, and task-plan authorization.
