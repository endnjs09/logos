# Run Log Format

Run logs record what Logos did, why it did it, and whether it improved the
result compared with a baseline.

Run logs are part of the product. If the run cannot be audited, Logos cannot
prove calibration improvement.

## Run Directory

Each run should write to:

```text
runs/<timestamp>-<task-id>-<condition>/
```

Example:

```text
runs/2026-07-11T101530Z-movie-tracker-gemini-logos/
```

## Recommended Run Artifacts

```text
run/
+-- request.json
+-- config.json
+-- target.json
+-- plugins.json
+-- snapshot.json
+-- interview-draft.json
+-- spec.json
+-- task-plan.json
+-- executor-context.json
+-- tool-results.jsonl
+-- verification.json
+-- run-result.json
+-- measurement.jsonl
+-- diff.patch
```

Not every mode needs every artifact. Low Fast Path may skip interview draft and
structured spec.

## Measurement Log

`measurement.jsonl` is append-only.

Each line should be one JSON object.

Required fields:

- `task_id`
- `condition`
- `target`
- `host`
- `initial_mode`
- `final_mode`
- `final_success`

Recommended fields:

- `mode_changed`
- `low_fast_path_applied`
- `context_handoff_applied`
- `plugins`
- `llm_call_count`
- `tool_call_count`
- `retry_count`
- `token_input`
- `token_output`
- `executor_context_tokens`
- `estimated_full_context_tokens`
- `test_result`
- `verification_result`
- `failure_reason`

## Tool Results

`tool-results.jsonl` should record normalized tool calls.

Each entry should include:

- tool name
- command or operation
- cwd
- start time
- end time
- exit code
- summary
- redaction status

Do not store secrets in tool logs.

## Verification Result

`verification.json` should record:

- tests passed
- success criteria status
- quality gate status
- excluded scope status
- blocking questions
- reviewer decision if applicable

Verification should distinguish:

- machine-verified
- model-reviewed
- human-reviewed
- not verified

## Run Result

`run-result.json` should summarize:

- task id
- condition
- target
- modified files
- diff path
- final status
- failure reason
- retry count
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

## Report Linkage

Comparison reports in `reports/comp/` should reference run directories rather
than duplicating all run content.
