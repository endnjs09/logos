---
id: logos.procedure.review
kind: procedure
name: review
description: Step procedure for reviewing implemented work for quality, risk, and security before final response.
status: active
version: 0.1.0
outputs:
  - review-summary
depends_on:
  - logos.procedure.execution
  - logos.role.rv
  - logos.role.sec
related_rules:
  - logos.rule.security
  - logos.rule.user-approval
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.1.0 -->

# Review

## Purpose

Check completed work for quality, regression, scope, and security risk.

## Use When

- Files were changed.
- Risk-sensitive areas such as auth, secrets, data, billing, or deployment were touched.

## Procedure

1. Compare the diff against the user request and task plan.
2. Check for scope creep, broken assumptions, and missing tests.
3. Use `sec` for security-sensitive changes.
4. Use `rv` for general code review and regression concerns.
5. Return concrete blockers or approval.

## Outputs

- `review-summary`

## Output Contract

Return reviewed files, findings, severity, required fixes, and residual risk.

## Failure Handling

If review evidence is insufficient, send the work back to execution or verification.
