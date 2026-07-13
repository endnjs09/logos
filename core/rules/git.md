---
id: logos.rule.git
kind: rule
name: git
description: Preserve user work and use git information as evidence.
status: active
version: 0.1.0
targets:
  - gemini-cli
profiles:
  - gemini
applies_to:
  - nous
depends_on: []
---

# Git Rule

Treat existing uncommitted changes as user work unless proven otherwise. Use
git status and diffs to understand impact, but do not revert unrelated changes.
