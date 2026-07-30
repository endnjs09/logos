---
id: logos.reference.dangerous-command-denylist-details
kind: reference
name: dangerous-command-denylist-details
description: Detailed implementation notes for dangerous command classification.
status: active
version: 0.1.0
applies_to:
  - logos.guard.dangerous-command-denylist
---

# Dangerous Command Details

The command guard should classify command intent, not only exact strings.
Segment compound shell commands first, evaluate each segment independently, and
use the most restrictive decision. Read-only discovery and verification should
stay quiet. Destructive discard, broad recursive deletion, forceful git history
mutation, and remote script execution require the strongest response available
on the target.
