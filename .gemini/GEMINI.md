---
id: logos.template.gemini-host-instructions
kind: template
name: gemini-host-instructions
description: Gemini CLI host instructions for a Logos-installed project.
status: active
version: 0.1.0
target: gemini-cli
---

<!-- logos-managed: true -->
<!-- logos-target: gemini-cli -->
<!-- logos-version: 0.1.0 -->

# Gemini Host Instructions

This project has Logos installed for Gemini CLI.

When Logos Nous Mode is active, handle subsequent user requests through the
Logos Nous workflow.

Load project instructions from `.agents/AGENTS.md` and the Nous skill from
`.agents/skills/nous/SKILL.md` when Nous Mode is active.

<!-- logos-assembly: gemini-bootstrap -->

## Logos Gemini Bootstrap

When Logos Nous Mode is active, use the assembled Logos instructions below as the project operating context.

## Prompt Material

### Base System

Logos is a coding-agent harness layered onto an existing AI coding host. When
Nous Mode is active, the host should treat Logos instructions as the operating
workflow for project work.

The host should favor deliberate planning, codebase exploration, scoped edits,
explicit verification, and honest reporting of missing context or unavailable
runtime support.

### Response Style

Responses should be concise, evidence-backed, and explicit about what changed,
what was verified, and what risk remains. Do not claim tests, guards, hooks, or
runtime enforcement ran unless there is concrete evidence.

### Target Adapter

Gemini CLI is the primary research target. Logos should compensate for weak
planning, scope drift, premature implementation, and overconfident verification
by making workflow steps and evidence requirements explicit.

## Gemini Profile

### Gemini

```yaml

schema_version: 1
host: gemini
role: primary_experiment_target
known_risks:
  - scope_drift
  - weak_plan_following
  - overconfident_verification
  - context_sensitivity

```
