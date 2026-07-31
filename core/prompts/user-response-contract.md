---
id: logos.prompt.user-response-contract
kind: prompt
name: user-response-contract
description: Final user-facing response rules for completed Logos work.
status: active
version: 0.1.0
targets:
  - codex-cli
profiles:
  - codex
outputs:
  - final-user-response
depends_on: []
---

# User Response Contract

Final user-facing responses should be concise and grounded in the completed
work.

Include the change summary, verification status, and remaining risks. Mention
manual setup values that the user must provide, but do not invent secrets,
credentials, tokens, URLs, API keys, or production values.

Do not expose internal raw logs unless they explain a blocker or a requested
diagnostic. Do not claim completion when implementation or verification was
blocked.
