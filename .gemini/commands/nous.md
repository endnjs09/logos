---
id: logos.command.nous
kind: command
name: nous
description: Activate Logos Nous Mode for the current Gemini CLI project session.
status: active
version: 0.1.0
target: gemini-cli
argument_hint: ""
loads:
  - logos.skill.nous
approval_required: false
---

# Nous Activation

## Purpose

Activate Logos Nous Mode for the current project session.

## Input

No command arguments are required.

## Preconditions

- Logos is installed in the current project.
- `.logos/session/` is writable.

## Command Instruction

Set the Logos session state to active. Subsequent user requests should follow
the Logos Nous workflow.

## Loaded Assets

- `.agents/AGENTS.md`
- `.agents/skills/nous/SKILL.md`

## Output

Confirm that Logos Nous Mode is active.

## Failure Handling

If the session state cannot be updated, report the failure and ask the user to
run `logos nous on` from the project root.

