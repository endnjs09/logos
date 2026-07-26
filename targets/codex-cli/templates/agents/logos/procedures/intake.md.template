---
id: logos.procedure.intake
kind: procedure
name: intake
description: Step procedure for deciding whether essential information is sufficient before Spec.
status: active
version: 0.2.0
outputs:
  - intake-result
schemas:
  - schemas/intake-result.schema.json
depends_on:
  - logos.role.intk
related_rules:
  - logos.rule.context-handoff
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.2.0 -->

# Intake

## Purpose

Decide whether the agent has enough essential information to write the Spec.
This procedure is the first gate before planning or editing.

## Use When

- A new coding, debugging, refactoring, testing, review, or repository-maintenance request starts.
- A previous answer supplies clarification and the agent must decide whether Spec can now begin.

## Snapshot Check

If the request appears to continue earlier Logos work, read
`.logos/memory/resume-snapshot.md` before asking questions. Use
`.logos/memory/active-work.json` or `.logos/memory/open-items.json` only when the
snapshot is insufficient. Do not scan `.logos/runs/` or `.logos/evidence/` by
default during intake.

## Core Rule

Ask only for information that is required before Spec or planning can start
safely. Do not ask for information that the scan result already resolves.
Code structure can resolve implementation patterns, but it cannot decide product
or security policy by itself. When a request affects policy, authorization,
data integrity, external integration, irreversible behavior, or user-visible
contract semantics, ask the smallest useful set of policy questions before Spec.

Complexity is an internal agent judgment. The default is `middle`; change it to
`low` or `high` only when there is a concrete reason.

## Complexity Guidance

- `low`: The request is small, clear, local, and low-risk.
- `middle`: Default for ordinary development work that needs a Spec before a plan.
- `high`: The request appears broad, cross-cutting, structurally complex, risky, or hard to reverse.

Use `high` when the request may involve sensitive behavior such as auth,
permissions, billing, data deletion, schema migration, deployment, production
state, secrets, or external systems. Use `low` only when the work looks clearly
bounded and safe.

## Ask Criteria

Ask when missing information would block safe progress before Spec:

- The requested outcome has multiple materially different meanings.
- The completion criteria are unclear enough that implementation could be wrong.
- A required external choice is missing, such as provider, platform, integration, or policy.
- The request may touch sensitive data, permissions, security, billing, irreversible changes, or production-like state.
- Exploration cannot identify the missing information from repository files.

Ask policy questions when the request requires decisions such as:

- Authentication or identity policy, including sign-up, login, password reset, session, token, or account lifecycle behavior.
- Authorization policy, including who may view, create, update, delete, approve, publish, export, or administer data.
- Uniqueness and duplicate handling, including account, phone, email, username, slug, payment request, order, or idempotency keys.
- Password, credential, secret, token, verification-code, or sensitive-response handling.
- Billing, payment, points, refunds, settlement, quotas, external calls, or irreversible state transitions.
- Database schema, migration, retention, deletion, audit, or recovery policy.
- API contract choices that users or clients observe, including status codes, error semantics, response shape, and public/private fields.

For these areas, do not silently turn an inferred default into a confirmed
decision unless repository evidence already proves that exact policy. If a
reasonable default exists but still changes service policy, ask a concise
required question or state the default as an optional question that can be
accepted by silence only when safe.

## Do Not Ask Criteria

Do not ask when the information can be discovered or safely deferred:

- Existing code, configuration, tests, or documentation can answer it.
- A reversible, conventional default is safe until planning refines it.
- The question is stylistic, preferential, or not needed to start exploration.
- The question would be more precise during planning.
- The question only asks about naming, internal class layout, UI copy, color,
  formatting style, or other implementation taste that the repository pattern
  can decide.

## Question Budget

Ask as many blocking questions as needed, but no more than 10 at once. If more
than 10 blocking unknowns exist, ask the highest-priority questions first and
defer the rest to planning after Spec.

## Procedure

1. Restate the actionable request in one sentence.
2. Decide whether essential information is `sufficient` or `missing`.
3. Set internal complexity to `middle` unless there is evidence for `low` or `high`.
4. List only unknowns that block safe progress before Spec.
5. Split questions into `required_questions` and `optional_questions`.
6. If essential information is missing, ask the required questions and set `next_step` to `ask_user`.
7. If essential information is sufficient, record safe assumptions and set `next_step` to `spec`.
8. Start or update the Interview Draft with the raw request, known facts,
   blocking unknowns, questions, confirmed decisions, open questions, and
   excluded scope.
9. After the user answers blocking questions, re-run this procedure, update the
   Interview Draft, and proceed to Spec once the missing essentials are
   resolved.

## Outputs

- `intake-result`

## Output Contract

Return this structure:

```yaml
schema_version: 1
intake_summary: "<one-sentence actionable restatement>"
essential_information_status: sufficient | missing
complexity: low | middle | high
complexity_basis:
  - "<why this complexity was chosen>"
blocking_unknowns:
  - "<unknown that blocks safe progress before Spec>"
questions:
  - "<all required questions for backward compatibility; mirror required_questions>"
required_questions:
  - "<question that must be answered before Spec>"
optional_questions:
  - "<question that would improve the task but can safely default or defer>"
known_constraints:
  - "<confirmed constraint from the user request or prior answers>"
assumptions_allowed:
  - "<safe assumption that does not need a question before Spec>"
risk_notes:
  - "<risk hint for planning or review>"
interview_draft_update:
  raw_request: "<original or latest user request>"
  known_facts:
    - "<fact established by request, snapshot, or user answer>"
  confirmed_decisions:
    - "<decision confirmed by the user or safe project evidence>"
  open_questions:
    - "<non-blocking question to carry into planning>"
  excluded_scope:
    - "<scope that should not be implemented unless later confirmed>"
next_step: ask_user | spec
```

When `essential_information_status` is `sufficient`, `questions` should be
empty, `required_questions` must be empty, and `next_step` must be `spec`.
When it is `missing`, `questions` must mirror `required_questions`, required
questions must target the blocking unknowns, and `next_step` must be `ask_user`.
Optional questions must not block Spec by themselves.

## Failure Handling

If the request is impossible to scope, pause and ask the blocking questions that
would make Spec safe to begin. If uncertainty can be resolved from scan evidence,
move to Spec instead of questioning the user.
