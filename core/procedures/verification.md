---
id: logos.procedure.verification
kind: procedure
name: verification
description: Step procedure for verifying completed or proposed changes with tests, builds, lint, diff review, doctor checks, and skipped-check reporting.
status: active
version: 0.2.0
outputs:
  - verification-summary
depends_on:
  - logos.procedure.execution
  - logos.role.vf
related_rules:
  - logos.rule.command-execution
  - logos.rule.git
  - logos.rule.secrets
  - logos.rule.verification
---

<!-- logos-managed: true -->
<!-- logos-target: codex-cli -->
<!-- logos-version: {{logos_version}} -->
<!-- logos-asset-version: 0.2.0 -->

# Verification

## Purpose

Check whether work is complete, scoped, and supported by evidence.

## Use When

- A change has been made.
- A plan needs quality review.
- The final response needs pass, fail, skipped, or unavailable verification status.

## Procedure

1. Identify relevant checks.
2. Run available tests, builds, linters, or doctor checks when appropriate.
3. Inspect diffs when tests are unavailable or insufficient.
4. Record pass, fail, skipped, or unavailable status.
5. Include verification status in the final response.

## Outputs

- `verification-summary`

## Output Contract

Return checks run, results, skipped checks, and remaining risk.

## Failure Handling

Report unavailable checks and remaining risk.
