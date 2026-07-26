# Run Log Format

Run logs record what Logos did, which plan it followed, what changed, and how
execution and verification ended.

Run logs are part of the product. If the run cannot be audited or resumed,
Logos cannot keep long Codex work reliable.

## Run Directory

Each installed project writes run records to:

```text
.logos/runs/<run_id>/
```

Example:

```text
.logos/runs/run-20260726T083710Z0000/
```

## Current Run Artifacts

```text
.logos/runs/<run_id>/
+-- run.json
+-- commands.jsonl
+-- files.jsonl
+-- guards.jsonl
+-- tests.jsonl
```

`run.json` is the compact run summary. JSONL files are append-only event
records. Official stage contracts live under `.logos/plans/<plan_id>/`.

## Plan Linkage

`run.json.artifact_paths` links the run to the important plan artifacts:

- `plan-state.json`
- `request.json`
- `scan-result.json`
- `intake-result.json`
- `spec.json`
- `task-plan.json`
- `context-handoff.json`
- `review-lite.json`
- `execution-result.json`
- `verification-result.json`

The run summary copies only high-signal summaries from those artifacts. It does
not duplicate full stage JSON.

## Commands

`commands.jsonl` records normalized command observations:

- tool name
- command
- cwd
- exit code
- summary

Do not store secrets in tool logs.

## Files

`files.jsonl` records changed file observations. `run.json.touched_files` is the
deduplicated high-level list.

## Guards

`guards.jsonl` records structured guard decisions when Runner or hooks can
associate the decision with the current run.

## Tests

`tests.jsonl` records test results declared by execution or verification stage
artifacts. Hooks must not infer whether a command is a test from command text.

The semantic source is:

- `execution-result.json.tests_run`
- `verification-result.json.tests_run`

Runner copies those structured records into `tests.jsonl` and updates:

- `run.json.test_summary`
- `run.json.test_count`
- `run.json.failed_test_count`

## Run Summary

`run.json` should summarize:

- run id
- plan id
- selected mode
- status
- user request
- execution summary
- verification summary
- test summary
- modified files
- failure reason
- artifact paths

## Failure Reasons

Use stable failure reason names.

Recommended values:

- `missing_requirements`
- `clarification_blocked`
- `plan_rejected`
- `execution_failed`
- `test_failed`
- `verification_failed`
- `scope_violation`
- `retry_budget_exceeded`
- `tool_error`
- `target_error`
- `unknown`

## Redaction Rules

Logs must not contain:

- API keys
- access tokens
- passwords
- private SSH keys
- personal local paths when avoidable
- full proprietary data dumps

If redaction occurs, log the redaction marker and reason.

## Reproducibility Requirements

A run should record enough information to answer:

- Which config was loaded?
- Which target was used?
- Which plugins were active?
- Which benchmark task ran?
- Which mode was selected?
- Which mode was finalized?
- What context was passed to execution?
- Which tools were run?
- What failed or succeeded?
- Which plan artifacts explain the work?
- What should Codex read first after context loss?

## Resume Memory

Agents should not scan raw `.logos/runs/` or `.logos/evidence/` at the start of
normal work. When context is unclear, read:

```text
.logos/memory/resume-snapshot.md
```

Then, only if needed, follow the plan/run links named in the snapshot.

## Report Command

`logos-runner report <plan_id>` prints the compact human-facing summary for a
plan and its linked run.
