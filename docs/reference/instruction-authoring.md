# Instruction Authoring

This document defines how to write Logos instructions so they remain reliable
when assembled into host prompts.

## Instruction Hierarchy

Logos instruction assets should be layered from stable to specific:

```text
core/prompts/base-system
  -> core/rules
  -> core/workflows
  -> core/roles
  -> .agents/skills
  -> targets/<target>
  -> runtime context
```

Lower layers may specialize upper layers, but they should not silently contradict
them. If a target needs an exception, document the exception in the target asset.

## Write For Execution

Agent-facing instructions should be written as procedures.

Good:

```text
Inspect the task plan before editing files. If `target_files` is missing, stop
and request a plan update.
```

Bad:

```text
The agent should ideally be mindful of file scope.
```

## Use Contract Language

Use these keywords consistently:

- `MUST` for mandatory behavior
- `MUST NOT` for prohibited behavior
- `SHOULD` for preferred behavior
- `MAY` for optional behavior
- `STOP` when the agent must halt and ask or wait

Do not overuse `MUST`. If everything is mandatory, nothing is prioritized.

## Make Inputs Explicit

Every instruction that depends on runtime data must name the input.

Examples:

- `user_request`
- `task_plan.target_files`
- `context_handoff.allowed_write_paths`
- `run_state.retry_count`
- `approval.status`
- `guard_result.decision`

Avoid phrases like "the relevant files" unless a previous step defines how to
find them.

## Make Outputs Explicit

Every process must produce named outputs.

Examples:

- `intake`
- `spec`
- `task-plan`
- `context-handoff`
- `guard-result`
- `evidence`
- `measurement-log`
- `final-response`

When possible, reference the schema that validates the output.

## Avoid Hidden Global Policy

Do not bury global policy inside a narrow file.

Examples:

- File write boundaries belong in `core/guards/file-write-boundary/`.
- Test discipline belongs in `core/rules/` or `core/evaluation/`.
- Gemini-specific command behavior belongs in `targets/gemini-cli/`.
- Nous activation belongs in `.gemini/commands/nous.md` and the Gemini target.

## Clarifying Questions

Questions must be bounded.

Each questioning workflow must define:

- when questions are required
- maximum question count
- what counts as a blocking ambiguity
- when the agent may proceed with assumptions
- how assumptions are recorded

Avoid question lists that shift planning responsibility back to the user.

## Examples

Examples should show behavior, not decorate the file.

Good examples include:

- trigger examples
- allowed and blocked cases
- expected output shape
- failure cases

Avoid examples that duplicate the full policy.

## Failure Instructions

Every agent-facing document should say what to do when it cannot proceed.

Common failure behaviors:

- `stop_and_ask`
- `block_tool_call`
- `request_approval`
- `record_failure`
- `fallback_to_baseline`
- `retry_with_budget`
- `return_partial_with_risk`

## Anti-Patterns

Avoid:

- long motivational roleplay
- duplicated rules across multiple files
- ambiguous safety language
- hidden target-specific behavior in core assets
- command files that contain full workflows
- skill files that load every reference eagerly
- guard files that cannot be tested
- outputs that have no name or schema
