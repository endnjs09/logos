---
id: logos.guard.secret-scan
kind: guard
name: secret-scan
description: Detect secret-like values with deterministic patterns before they are exposed, stored, or finalized.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
enforcement: hard
enforcement_status: implemented
risk_level: high
severity: 3
decision: ask
depends_on: []
---

# Secret Scan

Detect credential-like values with deterministic matching. Do not treat file
names such as `.env` as automatically forbidden; classify the value being
introduced or exposed.

Placeholder names are allowed when they do not contain a real credential value.
Examples include `REDIS_URL`, `OAUTH_CLIENT_SECRET`, `YOUR_API_KEY`,
`${SERVICE_TOKEN}`, and `<token>`.

When a real secret-like value is detected, pause through the Codex approval
path, warn that the value may be sensitive, and prefer placeholder text plus
user-owned secret entry outside the agent response.
