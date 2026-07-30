---
id: logos.reference.secret-scan-details
kind: reference
name: secret-scan-details
description: Detailed implementation notes for secret scanning and sanitization.
status: active
version: 0.1.0
applies_to:
  - logos.guard.secret-scan
---

# Secret Scan Details

Secret policy distinguishes names from values. Environment variable names,
placeholder tokens, and instructions telling the user where to put a value are
allowed. Concrete credential values should not be written to logs, evidence,
commits, final summaries, or generated documentation. Runtime code should
sanitize before recording evidence.
