---
id: logos.reference.working-tree-checkpoint-details
kind: reference
name: working-tree-checkpoint-details
description: Detailed implementation notes for working tree checkpoints.
status: active
version: 0.1.0
applies_to:
  - logos.guard.working-tree-checkpoint
---

# Working Tree Checkpoint Details

Checkpoints are evidence, not automatic destructive rollback. Record the current
HEAD, dirty state, and run id before risky mutation. If the project is not a git
repository, record that limitation and avoid pretending rollback is guaranteed.
