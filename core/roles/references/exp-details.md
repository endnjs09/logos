---
id: logos.reference.exp-details
kind: reference
name: exp-details
description: Detailed feature scan, evidence, and question candidate guidance for Explorer.
status: active
version: 0.1.0
applies_to:
  - logos.role.exp
---

# Explorer Details

## Purpose

Define how read-only scan evidence should be collected without turning scan into
implementation.

## Read Only When

- The target domain is hard to locate.
- Question candidates are too broad or too few.
- Likely target files are uncertain.

## Detailed Guidance

- Start from observable project structure, then search by domain terms.
- Check shared/common/config/middleware only shallowly unless evidence points
  there.
- Question candidates should identify user-policy choices, not code facts.
- Complexity signals include multiple surfaces, auth/data changes, external
  effects, unclear ownership, and cross-role implementation.

## Failure Handling

If evidence is insufficient, return the gap and recommended next read. Do not
guess the implementation surface.
