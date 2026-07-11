# Benchmark Format

Benchmarks define repeatable tasks used to measure whether Logos improves Gemini
Pro High behavior.

A benchmark is not just a prompt. It is a controlled experiment input with
success criteria, constraints, expected evidence, and comparison conditions.

## Benchmark Directory Layout

```text
benchmarks/
+-- tasks/
+-- suites/
+-- fixtures/
+-- expected/
```

## Task Files

Task files live in:

```text
benchmarks/tasks/
```

Each task should define:

- `task_id`
- request
- initial mode
- success criteria
- excluded scope
- fixture path if needed
- expected outcome
- verification method
- allowed conditions
- limits

## Task Authoring Principles

Benchmark tasks must be:

- repeatable
- scoped
- measurable
- independent from local machine state
- clear enough that multiple hosts can attempt the same work

Avoid tasks that rely on:

- private credentials
- current web content
- hidden local files
- vague quality preferences
- manual interpretation only

## Success Criteria

Success criteria must be concrete.

Good:

```yaml
success_criteria:
  - "The app stores watched movies by calendar year."
  - "The year summary view displays total watched count."
  - "Tests or verification steps cover empty, single-year, and multi-year states."
```

Bad:

```yaml
success_criteria:
  - "The app should be good."
  - "Make it clean."
```

## Excluded Scope

Every non-trivial benchmark should define excluded scope.

Examples:

```yaml
excluded_scope:
  - "Do not add authentication."
  - "Do not introduce a database service."
  - "Do not change unrelated UI routes."
```

Excluded scope is important because one of Logos' goals is reducing scope drift.

## Fixtures

Fixtures live in:

```text
benchmarks/fixtures/
```

Use fixtures for:

- sample projects
- input files
- mock API data
- expected project state

Fixtures should be small enough to copy per run.

## Expected Results

Expected result assets live in:

```text
benchmarks/expected/
```

They may include:

- expected JSON output
- expected file list
- expected UI behavior descriptions
- expected test commands
- expected diff constraints

Expected results do not need to describe one exact implementation if multiple
valid implementations exist.

## Suites

Suites live in:

```text
benchmarks/suites/
```

A suite groups tasks for repeatable comparison.

Suite files should define:

- suite id
- task list
- allowed conditions
- default limits
- reporting label

## Conditions

Standard conditions:

- `gemini-baseline`
- `gemini-logos`
- `codex-baseline`

Future conditions may include:

- `gemini-logos-with-plugin`
- `codex-logos`
- `claude-code-reference`

Condition names must be stable because reports use them for comparison.

## Limits

Tasks may define limits:

- max retries
- max tool calls
- max model calls
- time budget
- token budget
- allowed file write scope

Limits make benchmark results comparable.

## Verification

Each benchmark should define how success is verified.

Verification may include:

- test command
- build command
- static check
- file existence
- schema validation
- manual review rubric

When verification is manual, the task should say exactly what the reviewer must
check.

## Benchmark Review Checklist

Before adding a benchmark:

- Does it have a stable task id?
- Is the request clear?
- Is the initial mode justified?
- Are success criteria measurable?
- Is excluded scope explicit?
- Can the task run without private data?
- Is verification defined?
- Are limits defined?
- Can Gemini baseline and Gemini + Logos both attempt it?
