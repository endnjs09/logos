# Codex CLI Guard Mapping

This document maps Logos guard concepts to Codex CLI surfaces for V8 guardrail
implementation.

## Mapping Rules

- Use Codex native safety surfaces before adding a separate Logos mechanism.
- Treat prompt rules as advisory only.
- Treat a guard as `implemented` only when a Logos script or Codex config path is
  wired into the target.
- Treat a guard as `verified` only after tests or recorded evidence show that
  the guard fires as intended.
- Prefer Codex native sandbox and approval behavior for execution safety.
- Use `PermissionRequest` to add concise Logos approval notes, `PreToolUse` for
  preflight warnings, and `PostToolUse` or `Stop` for evidence and final
  validation.
- Claim hard blocking only after the target output schema is verified to stop
  execution in Codex.
- Track the hard-deny schema probe separately from default installed hooks. See
  `docs/targets/codex-cli/hard-deny-probe.md`.
- Treat execpolicy as optional and experimental in V8. See
  `docs/targets/codex-cli/execpolicy.md`.

## Guard Matrix

| Logos Guard | Primary Codex Surface | Logos Code Needed | Current Enforcement | V8 Priority |
|---|---|---|---|---|
| `dangerous-command-denylist` | `PreToolUse` for `Bash`, `PermissionRequest`, optional `execpolicy` | command parser and warning mapper | advisory-implemented | V8-A |
| `protected-branch-guard` | `PreToolUse` for `Bash` git commands, `PostToolUse` git status check | branch detector and protected branch policy | advisory-implemented | V8-B |
| `approval-gate` | `PermissionRequest`, `approval_policy = "on-request"` | request classifier and approval-note mapper | advisory-implemented | V8-C |
| `secret-scan` | `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop` | deterministic secret pattern scanner | advisory-implemented | V8-D |
| `working-tree-checkpoint` | `SessionStart` or first `PreToolUse` | git HEAD/status recorder and checkpoint manifest | advisory-implemented | V8-E |
| `file-write-boundary` | `PreToolUse` for `apply_patch`, `Edit`, or `Write` | target file allow-list from task plan/context handoff | policy-only | after task-plan runtime |
| `dependency-install-guard` | `PreToolUse` for package manager commands | package manager classifier and approval rule | partial via command action classifier | after V8 |
| `high-risk-override-block` | `PermissionRequest`, `PreToolUse`, `Stop` | high-risk override classifier | policy-only | after risk taxonomy |
| `excluded-scope` | `PreToolUse`, `PostToolUse`, `Stop` | scope matcher using task plan excluded scope | policy-only | after V10 |
| `context-budget` | `UserPromptSubmit`, `Stop` | context size estimator and warning path | policy-only | after V10 |
| `required-fields` | `Stop` | output/schema validator | policy-only | after V10 |

The `advisory-implemented` rows are the V8 guardrail MVP. Policy-only rows are
real Logos guard assets, but they depend on later task-plan, risk taxonomy,
measurement, or output-schema runtime work and are not V8 completion blockers.

## Guard Details

### Dangerous Command Denylist

Use for commands that can delete data, rewrite git history, install remote code,
or alter production-like state.

Codex surfaces:

- `PreToolUse` checks `Bash` command arguments before execution.
- `PermissionRequest` checks escalations before approval.
- `execpolicy` can provide an experimental prefix-level block or prompt layer.
  Logos does not install execpolicy rules by default in V8.

Limit:

- Shell wrappers and complex shell syntax may reduce static command precision.
  Treat the denylist as a guardrail plus approval boundary, not a complete
  parser for all shells.
- The installed PreToolUse hook emits concise warning or approval-note context.
  Codex-runtime blocking behavior still requires target-runtime verification
  before the guard is marked `verified`.
- The denylist is not the primary safety model. Codex sandbox and approval
  remain the execution boundary; Logos adds risk explanation and workflow
  pointers.
- V8-2-A adds a standalone hard-deny probe for the OMO-observed
  `permissionDecision = "deny"` output. It is not enabled by default.

### Protected Branch Guard

Use for direct mutation of protected branches such as `main` or `master`.

Codex surfaces:

- `PreToolUse` checks git commands before they run.
- `PostToolUse` can record the branch and changed git state after a command.

Limit:

- The guard needs repository context and must handle detached HEAD and worktree
  states.

### Approval Gate

Use for actions that should pause before crossing a safety boundary.

Codex surfaces:

- `approval_policy = "on-request"` keeps approval prompts available.
- `PermissionRequest` lets Logos inspect permission requests and add concise
  approval notes.
- Granular approval policy can later fail closed for selected categories.

Limit:

- `approval_policy = "never"` removes the interactive approval path and is
  invalid for the default Logos Codex target.
- V6 doctor already rejects `approval_policy = "never"` for Codex installs; V8
  should keep that check and add runtime request classification.
- Unknown permission requests stay silent. Codex's own approval prompt remains
  the user-facing control unless Logos can add a meaningful risk note.

### Secret Scan

Use for API keys, private keys, tokens, credentials, `.env` leakage, and
generated files that may contain sensitive values.

Codex surfaces:

- `UserPromptSubmit` can catch pasted secrets before work starts.
- `PreToolUse` can inspect writes or shell commands that may expose secrets.
- `PostToolUse` and `Stop` can scan diffs and final outputs before completion.

Limit:

- Deterministic scanning is required. LLM judgment alone is not a secret guard.
- V8 starts with PreToolUse payload scanning and approval notes. Diff/final
  output scanning belongs to later PostToolUse or Stop expansion.

### Working Tree Checkpoint

Use before risky operations to record recovery metadata.

Codex surfaces:

- `PreToolUse` can record current git `HEAD`, branch, and
  `git status --short` before a risky command proceeds through Codex approval.

Limit:

- V8 records metadata only. It does not automatically reset, stash, or discard
  user work.
- Non-git directories still get a checkpoint file with missing git fields.

### File Write Boundary

Use to keep file edits inside the planned task scope.

Codex surfaces:

- `PreToolUse` can observe `apply_patch`, `Edit`, and `Write`-like calls.

Limit:

- The guard depends on `task_plan.target_files` or context handoff allow lists.
  It should be implemented after task plan schema work is available.

### Dependency Install Guard

Use for package installation, package manager lockfile updates, toolchain
installation, and commands that can download or execute third-party code.

Codex surfaces:

- `PreToolUse` checks package manager commands such as `npm install`,
  `pnpm add`, `pip install`, `poetry add`, `cargo add`, `go get`, and similar
  commands before execution.
- `PermissionRequest` can route network, dependency, or sandbox escalation
  requests through approval.

Limit:

- Package manager command semantics differ by ecosystem. The first
  implementation should classify common high-risk patterns and ask when unsure
  instead of silently allowing ambiguous dependency changes.
- V8 classifies common package manager install/add/remove/update actions inside
  the command guard. A standalone dependency-install guard remains a follow-up.
- Package test/build script commands such as `npm test` are not dependency
  changes and should stay silent unless another guard applies.

### Compound Shell Segments

Use when a shell command contains multiple operations in one line.

Codex surfaces:

- `PreToolUse` receives the shell command payload and can inspect command
  segments before Codex approval or execution.

Limit:

- V8 splits common separators such as `;`, `&&`, `||`, and `|`. It is not a
  complete shell parser.
- Each segment is classified independently, and the most restrictive result is
  used for the Logos warning or approval note.

### High Risk Override Block

Use when a user or model tries to override safeguards around production data,
payments, authentication, authorization, data deletion, database migration,
secret exposure, or protected branch mutation.

Codex surfaces:

- `PermissionRequest` can inspect approval requests before the boundary is
  crossed.
- `PreToolUse` can catch commands or writes that attempt the override.
- `Stop` can fail the turn when the final result claims an unsafe override was
  performed or bypassed.

Limit:

- This guard needs a deterministic high-risk taxonomy plus user-authorization
  rules. It should block or require explicit approval; it must never be
  represented as `record_only`.
