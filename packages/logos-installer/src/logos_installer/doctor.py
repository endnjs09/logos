"""Doctor checks for a Logos Gemini installation."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path

from logos_core.assets.scanner import scan_core_assets
from logos_core.assets.validate import load_asset, validate_paths
from logos_core.session.state import validate_session_state_payload
from logos_core.work_state.jsonl import validate_jsonl


GEMINI_REQUIRED_PATHS = [
    ".gemini/GEMINI.md",
    ".gemini/commands/nous.toml",
    ".gemini/settings.json",
    ".agents/AGENTS.md",
    ".agents/skills/nous/SKILL.md",
    ".agents/skills/codebase-exploration/SKILL.md",
    ".agents/skills/implementation-planning/SKILL.md",
    ".agents/skills/risk-review/SKILL.md",
    ".agents/skills/verification/SKILL.md",
    ".logos/config.toml",
    ".logos/target.toml",
    ".logos/active-profile.toml",
    ".logos/session/nous-state.json",
    ".logos/generated/install-manifest.json",
    ".logos/generated/asset-manifest.json",
    ".logos/generated/asset-hashes.json",
    ".logos/generated/guards-manifest.json",
    ".logos/generated/prompt-assembly-manifest.json",
]

CODEX_REQUIRED_PATHS = [
    "AGENTS.md",
    ".agents/skills/nous/SKILL.md",
    ".agents/logos/procedures/intake.md",
    ".agents/logos/procedures/exploration.md",
    ".agents/logos/procedures/spec.md",
    ".agents/logos/procedures/planning.md",
    ".agents/logos/procedures/execution.md",
    ".agents/logos/procedures/verification.md",
    ".agents/logos/procedures/review.md",
    ".agents/logos/procedures/resume.md",
    ".agents/logos/roles/orch.md",
    ".agents/logos/roles/intk.md",
    ".agents/logos/roles/exp.md",
    ".agents/logos/roles/sp.md",
    ".agents/logos/roles/pln.md",
    ".agents/logos/roles/exe.md",
    ".agents/logos/roles/bd.md",
    ".agents/logos/roles/fd.md",
    ".agents/logos/roles/db.md",
    ".agents/logos/roles/sys.md",
    ".agents/logos/roles/test.md",
    ".agents/logos/roles/sec.md",
    ".agents/logos/roles/rv.md",
    ".agents/logos/roles/vf.md",
    ".agents/logos/roles/mem.md",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/pre_tool_use.py",
    ".codex/hooks/permission_request.py",
    ".codex/hooks/post_tool_use.py",
    ".codex/hooks/post_compact.py",
    ".logos/config.toml",
    ".logos/target.toml",
    ".logos/active-profile.toml",
    ".logos/session/nous-state.json",
    ".logos/generated/install-manifest.json",
    ".logos/generated/asset-manifest.json",
    ".logos/generated/asset-hashes.json",
    ".logos/generated/guards-manifest.json",
    ".logos/generated/prompt-assembly-manifest.json",
]

CODEX_MANIFEST_TRACKED_REQUIRED_PATHS = [
    relative for relative in CODEX_REQUIRED_PATHS if not relative.startswith(".logos/generated/")
]

CODEX_OBSOLETE_PATHS = [
    ".agents/skills/codebase-exploration/SKILL.md",
    ".agents/skills/implementation-planning/SKILL.md",
    ".agents/skills/risk-review/SKILL.md",
    ".agents/skills/verification/SKILL.md",
    ".agents/logos/procedures/codebase-exploration.md",
    ".agents/logos/procedures/implementation-planning.md",
    ".agents/logos/procedures/risk-review.md",
]

CODEX_PROCEDURE_PATHS = [
    ".agents/logos/procedures/intake.md",
    ".agents/logos/procedures/exploration.md",
    ".agents/logos/procedures/spec.md",
    ".agents/logos/procedures/planning.md",
    ".agents/logos/procedures/execution.md",
    ".agents/logos/procedures/verification.md",
    ".agents/logos/procedures/review.md",
    ".agents/logos/procedures/resume.md",
]

CODEX_PROCEDURE_IDS = {
    ".agents/logos/procedures/intake.md": "logos.procedure.intake",
    ".agents/logos/procedures/exploration.md": "logos.procedure.exploration",
    ".agents/logos/procedures/spec.md": "logos.procedure.spec",
    ".agents/logos/procedures/planning.md": "logos.procedure.planning",
    ".agents/logos/procedures/execution.md": "logos.procedure.execution",
    ".agents/logos/procedures/verification.md": "logos.procedure.verification",
    ".agents/logos/procedures/review.md": "logos.procedure.review",
    ".agents/logos/procedures/resume.md": "logos.procedure.resume",
}

CODEX_ROLE_PATHS = [
    ".agents/logos/roles/orch.md",
    ".agents/logos/roles/intk.md",
    ".agents/logos/roles/exp.md",
    ".agents/logos/roles/sp.md",
    ".agents/logos/roles/pln.md",
    ".agents/logos/roles/exe.md",
    ".agents/logos/roles/bd.md",
    ".agents/logos/roles/fd.md",
    ".agents/logos/roles/db.md",
    ".agents/logos/roles/sys.md",
    ".agents/logos/roles/test.md",
    ".agents/logos/roles/sec.md",
    ".agents/logos/roles/rv.md",
    ".agents/logos/roles/vf.md",
    ".agents/logos/roles/mem.md",
]

CODEX_ROLE_IDS = {
    ".agents/logos/roles/orch.md": "logos.role.orch",
    ".agents/logos/roles/intk.md": "logos.role.intk",
    ".agents/logos/roles/exp.md": "logos.role.exp",
    ".agents/logos/roles/sp.md": "logos.role.sp",
    ".agents/logos/roles/pln.md": "logos.role.pln",
    ".agents/logos/roles/exe.md": "logos.role.exe",
    ".agents/logos/roles/bd.md": "logos.implementation-role.bd",
    ".agents/logos/roles/fd.md": "logos.implementation-role.fd",
    ".agents/logos/roles/db.md": "logos.implementation-role.db",
    ".agents/logos/roles/sys.md": "logos.implementation-role.sys",
    ".agents/logos/roles/test.md": "logos.implementation-role.test",
    ".agents/logos/roles/sec.md": "logos.role.sec",
    ".agents/logos/roles/rv.md": "logos.role.rv",
    ".agents/logos/roles/vf.md": "logos.role.vf",
    ".agents/logos/roles/mem.md": "logos.role.mem",
}

CODEX_RUNTIME_REQUIRED_DIRS = [
    ".logos/session",
    ".logos/evidence",
    ".logos/evidence/artifacts",
    ".logos/memory",
    ".logos/plans",
    ".logos/checkpoints",
    ".logos/runs",
]

CODEX_MEMORY_REQUIRED_PATHS = [
    ".logos/memory/active-work.json",
    ".logos/memory/run-index.json",
    ".logos/memory/open-items.json",
    ".logos/memory/resume-snapshot.md",
]


@dataclass(frozen=True)
class DoctorReport:
    ok: list[str]
    warnings: list[str]
    errors: list[str]

    @property
    def passed(self) -> bool:
        return not self.errors


def doctor_gemini(root: Path, *, source_root: Path | None = None) -> DoctorReport:
    return doctor_target(
        root,
        target="gemini-cli",
        required_paths=GEMINI_REQUIRED_PATHS,
        marker_checks={
            ".gemini/GEMINI.md": "logos-assembly: gemini-bootstrap",
            ".agents/AGENTS.md": "logos-assembly: agents-operating-rules",
            ".agents/skills/nous/SKILL.md": "logos-assembly: nous-skill-directive",
        },
        source_root=source_root,
    )


def doctor_codex(root: Path, *, source_root: Path | None = None) -> DoctorReport:
    return doctor_target(
        root,
        target="codex-cli",
        required_paths=CODEX_REQUIRED_PATHS,
        marker_checks={
            "AGENTS.md": "logos-assembly: codex-operating-context",
            ".agents/skills/nous/SKILL.md": "logos-assembly: codex-nous-skill",
        },
        source_root=source_root,
    )


def doctor_target(
    root: Path,
    *,
    target: str,
    required_paths: list[str],
    marker_checks: dict[str, str],
    source_root: Path | None = None,
) -> DoctorReport:
    source = (source_root or Path.cwd()).resolve()
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    for relative in required_paths:
        if (root / relative).exists():
            ok.append(relative)
        else:
            errors.append(f"Missing required path: {relative}")

    target_toml = root / ".logos/target.toml"
    if target_toml.exists():
        text = target_toml.read_text(encoding="utf-8")
        if 'status = "assumed"' in text:
            warnings.append("Target support contains assumed surfaces.")
        if 'status = "reported"' in text:
            warnings.append("Target support contains reported surfaces.")
        if 'status = "experimental"' in text:
            warnings.append("Target support contains experimental surfaces.")
        if 'status = "unknown"' in text:
            warnings.append("Target support contains unknown surfaces.")
        if 'status = "unsupported"' in text:
            errors.append("Target support contains unsupported active surfaces.")

    if target == "codex-cli":
        validate_target_provides(root, target, ok, errors)
        validate_codex_config(root, ok, warnings, errors)
        validate_codex_hooks(root, ok, warnings, errors)
        validate_codex_install_shape(root, ok, errors)
        validate_codex_links(root, ok, errors)
        validate_codex_procedures(root, ok, errors)
        validate_codex_roles(root, ok, errors)
        validate_codex_target_profile(root, ok, errors)
        validate_codex_runtime_dirs(root, ok, errors)
        validate_codex_work_state(root, ok, errors)

    validate_session_state(root, ok, errors)
    install_manifest = validate_manifest(root, ok, errors)
    validate_core_manifests(root, source, ok, warnings, errors)
    validate_prompt_assembly(root, marker_checks, ok, errors)
    if target == "codex-cli":
        validate_codex_manifest_files(root, install_manifest, ok, errors)

    markdown_paths = collect_markdown_assets(root, required_paths)
    for issue in validate_paths([path for path in markdown_paths if path.exists()]):
        errors.append(f"{issue.path}: {issue.message}")

    return DoctorReport(ok=ok, warnings=warnings, errors=errors)


def validate_target_provides(
    root: Path,
    target: str,
    ok: list[str],
    errors: list[str],
) -> None:
    path = root / ".logos/target.toml"
    if not path.exists():
        return

    try:
        loaded = tomllib.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"Invalid target TOML: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append("Target metadata must be a TOML table.")
        return

    if target == "codex-cli":
        validate_expected_provides(
            loaded.get("provides"),
            {
                "instructions": "AGENTS.md",
                "skills": ".agents/skills",
                "procedures": ".agents/logos/procedures",
                "roles": ".agents/logos/roles",
                "config": ".codex/config.toml",
                "hooks": ".codex/hooks.json",
            },
            ok,
            errors,
        )


def validate_expected_provides(
    provides: object,
    expected: dict[str, str],
    ok: list[str],
    errors: list[str],
) -> None:
    if not isinstance(provides, dict):
        errors.append("Target metadata requires provides table.")
        return

    for key, value in expected.items():
        actual = provides.get(key)
        if actual == value:
            ok.append(f"target provides {key if key != 'config' else 'codex config'}")
            continue
        errors.append(f"Target provides.{key} must be {value}.")


def validate_codex_config(
    root: Path,
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    path = root / ".codex/config.toml"
    if not path.exists():
        return

    try:
        loaded = tomllib.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"Invalid Codex config TOML: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append("Codex config must be a TOML table.")
        return

    validate_codex_approval_policy(loaded, ok, warnings, errors)
    validate_codex_sandbox_mode(loaded, ok, warnings, errors)
    validate_codex_network_access(loaded, ok, warnings, errors)


def validate_codex_approval_policy(
    config: dict[str, object],
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    value = config.get("approval_policy")
    if value == "on-request":
        ok.append("codex config approval_policy")
        return
    if value == "never":
        errors.append("Codex approval_policy must not be never for default Logos target.")
        return
    if value is None:
        warnings.append("Codex config is missing approval_policy.")
        return
    warnings.append(f"Codex approval_policy differs from Logos default: {value}")


def validate_codex_sandbox_mode(
    config: dict[str, object],
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    value = config.get("sandbox_mode")
    if value == "workspace-write":
        ok.append("codex config sandbox_mode")
        return
    if value == "danger-full-access":
        errors.append("Codex sandbox_mode must not be danger-full-access for default Logos target.")
        return
    if value is None:
        warnings.append("Codex config is missing sandbox_mode.")
        return
    warnings.append(f"Codex sandbox_mode differs from Logos default: {value}")


def validate_codex_network_access(
    config: dict[str, object],
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    workspace_write = config.get("sandbox_workspace_write")
    if not isinstance(workspace_write, dict):
        warnings.append("Codex config is missing sandbox_workspace_write table.")
        return

    value = workspace_write.get("network_access")
    if value is False:
        ok.append("codex config network_access")
        return
    if value is True:
        errors.append("Codex sandbox_workspace_write.network_access must be false.")
        return
    warnings.append("Codex config is missing sandbox_workspace_write.network_access.")


def validate_codex_hooks(
    root: Path,
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    path = root / ".codex/hooks.json"
    if not path.exists():
        return
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid Codex hooks JSON: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append("Codex hooks config must be a JSON object.")
        return

    hooks = loaded.get("hooks")
    if not isinstance(hooks, dict):
        errors.append("Codex hooks config must contain hooks table.")
        return

    required_hooks = {
        "PreToolUse": ".codex/hooks/pre_tool_use.py",
        "PermissionRequest": ".codex/hooks/permission_request.py",
        "PostToolUse": ".codex/hooks/post_tool_use.py",
        "PostCompact": ".codex/hooks/post_compact.py",
    }
    error_count = len(errors)
    for hook_name, script_path in required_hooks.items():
        entries = hooks.get(hook_name)
        if not isinstance(entries, list) or not entries:
            errors.append(f"Codex hooks config must define {hook_name}.")
            continue
        if not hook_entries_reference(entries, script_path):
            errors.append(f"Codex {hook_name} hook must reference {script_path}.")

    if len(errors) == error_count:
        ok.append("Codex hooks config shape")
        warnings.append("Project-local Codex hooks may require trust review before they run.")


def hook_entries_reference(entries: list[object], script_path: str) -> bool:
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        commands = entry.get("hooks")
        if not isinstance(commands, list):
            continue
        for command_hook in commands:
            if not isinstance(command_hook, dict):
                continue
            command = command_hook.get("command")
            if isinstance(command, str) and script_path in command:
                return True
    return False


def validate_codex_install_shape(root: Path, ok: list[str], errors: list[str]) -> None:
    for relative in CODEX_OBSOLETE_PATHS:
        if (root / relative).exists():
            errors.append(f"Obsolete standalone Codex skill must not be installed: {relative}")

    if (root / ".gemini").exists():
        errors.append("Gemini target artifacts must not be present in Codex install: .gemini")
    else:
        ok.append("no Gemini target artifacts")


def validate_codex_runtime_dirs(root: Path, ok: list[str], errors: list[str]) -> None:
    for relative in CODEX_RUNTIME_REQUIRED_DIRS:
        path = root / relative
        if path.is_dir():
            ok.append(relative)
        else:
            errors.append(f"Missing required runtime directory: {relative}")

    skills_dir = root / ".agents/skills"
    if skills_dir.exists():
        unexpected = [
            path.relative_to(root).as_posix()
            for path in skills_dir.iterdir()
            if path.is_dir() and path.name != "nous"
        ]
        for relative in sorted(unexpected):
            errors.append(f"Unexpected auto-discoverable Codex skill: {relative}")
        if not unexpected:
            ok.append("Codex installs only nous as auto-discoverable skill")


def validate_codex_work_state(root: Path, ok: list[str], errors: list[str]) -> None:
    for relative in CODEX_MEMORY_REQUIRED_PATHS:
        path = root / relative
        if path.exists():
            ok.append(relative)
        else:
            errors.append(f"Missing required work-state path: {relative}")

    validate_work_state_json(
        root / ".logos/memory/active-work.json",
        {"schema_version", "status", "active_plan_id", "active_run_id", "updated_at"},
        "active-work shape",
        ok,
        errors,
    )
    validate_work_state_json(
        root / ".logos/memory/run-index.json",
        {"schema_version", "runs", "updated_at"},
        "run-index shape",
        ok,
        errors,
    )
    validate_work_state_json(
        root / ".logos/memory/open-items.json",
        {"schema_version", "items", "updated_at"},
        "open-items shape",
        ok,
        errors,
    )
    validate_run_directories(root, ok, errors)
    for relative in (
        ".logos/evidence/hook-events.jsonl",
        ".logos/evidence/command-results.jsonl",
        ".logos/evidence/test-results.jsonl",
    ):
        for issue in validate_jsonl(root / relative):
            errors.append(issue)


def validate_work_state_json(
    path: Path,
    required: set[str],
    ok_message: str,
    ok: list[str],
    errors: list[str],
) -> None:
    if not path.exists():
        return
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid work-state JSON {path}: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append(f"Work-state JSON must be an object: {path}")
        return
    missing = sorted(required - set(loaded))
    if missing:
        errors.append(f"Work-state JSON missing fields {missing}: {path}")
        return
    ok.append(ok_message)


def validate_run_directories(root: Path, ok: list[str], errors: list[str]) -> None:
    runs_dir = root / ".logos/runs"
    if not runs_dir.exists():
        return
    checked = 0
    for path in runs_dir.iterdir():
        if not path.is_dir():
            continue
        run_json = path / "run.json"
        validate_work_state_json(
            run_json,
            {"schema_version", "run_id", "selected_mode", "status", "started_at"},
            f"run record shape: {path.name}",
            ok,
            errors,
        )
        for jsonl in ("commands.jsonl", "files.jsonl", "guards.jsonl"):
            for issue in validate_jsonl(path / jsonl):
                errors.append(issue)
        checked += 1
    if checked == 0:
        ok.append("no run records yet")


def validate_codex_links(root: Path, ok: list[str], errors: list[str]) -> None:
    agents = root / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(encoding="utf-8")
        require_text(
            text,
            ".agents/skills/nous/SKILL.md",
            "AGENTS.md references nous skill",
            "AGENTS.md",
            ok,
            errors,
        )
        if "Gemini CLI is the primary research target" in text:
            errors.append("AGENTS.md contains Gemini-only primary target wording.")

    nous = root / ".agents/skills/nous/SKILL.md"
    if nous.exists():
        text = nous.read_text(encoding="utf-8")
        for relative in CODEX_PROCEDURE_PATHS:
            require_text(
                text,
                relative,
                f"nous references {Path(relative).name}",
                ".agents/skills/nous/SKILL.md",
                ok,
                errors,
            )
        for relative in CODEX_ROLE_PATHS:
            require_text(
                text,
                relative,
                f"nous references {Path(relative).name}",
                ".agents/skills/nous/SKILL.md",
                ok,
                errors,
            )


def require_text(
    text: str,
    needle: str,
    ok_message: str,
    source: str,
    ok: list[str],
    errors: list[str],
) -> None:
    if needle in text:
        ok.append(ok_message)
    else:
        errors.append(f"{source} must reference {needle}.")


def validate_codex_procedures(root: Path, ok: list[str], errors: list[str]) -> None:
    error_count = len(errors)
    for relative, expected_id in CODEX_PROCEDURE_IDS.items():
        path = root / relative
        if not path.exists():
            continue
        asset, issues = load_asset(path)
        for issue in issues:
            errors.append(f"{relative}: {issue.message}")
        if asset is None:
            continue
        frontmatter = asset.frontmatter
        if frontmatter.get("id") != expected_id:
            errors.append(f"{relative}: id must be {expected_id}.")
        if frontmatter.get("kind") != "procedure":
            errors.append(f"{relative}: kind must be procedure.")
        if frontmatter.get("status") != "active":
            errors.append(f"{relative}: status must be active.")
        if "triggers" in frontmatter:
            errors.append(f"{relative}: procedure must not use triggers.")
        if "do_not_trigger_when" in frontmatter:
            errors.append(f"{relative}: procedure must not use do_not_trigger_when.")
    if len(errors) == error_count:
        ok.append("Codex procedure frontmatter shape")


def validate_codex_roles(root: Path, ok: list[str], errors: list[str]) -> None:
    error_count = len(errors)
    implementation_codes = {"bd", "fd", "db", "sys", "test"}
    for relative, expected_id in CODEX_ROLE_IDS.items():
        path = root / relative
        if not path.exists():
            continue
        asset, issues = load_asset(path)
        for issue in issues:
            errors.append(f"{relative}: {issue.message}")
        if asset is None:
            continue
        frontmatter = asset.frontmatter
        role_code = Path(relative).stem
        expected_kind = "implementation-role" if role_code in implementation_codes else "role"
        if frontmatter.get("id") != expected_id:
            errors.append(f"{relative}: id must be {expected_id}.")
        if frontmatter.get("kind") != expected_kind:
            errors.append(f"{relative}: kind must be {expected_kind}.")
        if frontmatter.get("status") != "active":
            errors.append(f"{relative}: status must be active.")
        if frontmatter.get("role_code") != role_code:
            errors.append(f"{relative}: role_code must be {role_code}.")
    if len(errors) == error_count:
        ok.append("Codex role frontmatter shape")


def validate_codex_target_profile(root: Path, ok: list[str], errors: list[str]) -> None:
    validate_toml_value(
        root / ".logos/target.toml",
        ["target", "name"],
        "codex-cli",
        "target is codex-cli",
        ok,
        errors,
    )
    validate_toml_value(
        root / ".logos/active-profile.toml",
        ["profile", "name"],
        "codex",
        "active profile is codex",
        ok,
        errors,
    )


def validate_toml_value(
    path: Path,
    keys: list[str],
    expected: str,
    ok_message: str,
    ok: list[str],
    errors: list[str],
) -> None:
    if not path.exists():
        return
    try:
        loaded = tomllib.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"Invalid TOML {path}: {exc}")
        return
    value: object = loaded
    for key in keys:
        if not isinstance(value, dict):
            value = None
            break
        value = value.get(key)
    if value == expected:
        ok.append(ok_message)
    else:
        relative = path.relative_to(path.parents[1]).as_posix()
        errors.append(f"{relative} must set {'.'.join(keys)} = {expected}.")


def collect_markdown_assets(root: Path, required_paths: list[str]) -> list[Path]:
    paths = {root / relative for relative in required_paths if relative.endswith(".md")}

    manifest_path = root / ".logos/generated/install-manifest.json"
    if manifest_path.exists():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = {}
        files = loaded.get("files") if isinstance(loaded, dict) else None
        if isinstance(files, list):
            for item in files:
                if not isinstance(item, dict) or item.get("managed") is not True:
                    continue
                value = item.get("path")
                if isinstance(value, str) and value.endswith(".md") and not value.endswith("README.md"):
                    paths.add(root / value)

    return sorted(paths)


def validate_session_state(root: Path, ok: list[str], errors: list[str]) -> None:
    path = root / ".logos/session/nous-state.json"
    if not path.exists():
        return
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid session state JSON: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append("Session state must be a JSON object.")
        return
    issues = validate_session_state_payload(loaded)
    for issue in issues:
        errors.append(issue.message)
    if issues:
        return
    ok.append("session state shape")


def validate_manifest(root: Path, ok: list[str], errors: list[str]) -> dict[str, object] | None:
    path = root / ".logos/generated/install-manifest.json"
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid install manifest JSON: {exc}")
        return None
    if not isinstance(loaded, dict):
        errors.append("Install manifest must be a JSON object.")
        return None
    files = loaded.get("files")
    if not isinstance(files, list) or not files:
        errors.append("Install manifest must contain managed files.")
        return loaded
    ok.append("install manifest shape")
    return loaded


def validate_codex_manifest_files(
    root: Path,
    manifest: dict[str, object] | None,
    ok: list[str],
    errors: list[str],
) -> None:
    if manifest is None:
        return
    files = manifest.get("files")
    if not isinstance(files, list):
        return

    error_count = len(errors)
    manifest_paths: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            errors.append("Install manifest file entries must be JSON objects.")
            continue
        value = item.get("path")
        if not isinstance(value, str):
            errors.append("Install manifest file entries require path.")
            continue
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Install manifest path must stay inside root: {value}")
            continue
        manifest_paths.add(value)
        if value.startswith(".gemini/"):
            errors.append(f"Gemini artifact listed in Codex install manifest: {value}")
        if value in CODEX_OBSOLETE_PATHS:
            errors.append(f"Obsolete standalone skill listed in Codex install manifest: {value}")
        if not (root / relative).exists():
            errors.append(f"Install manifest file is missing on disk: {value}")

    for relative in CODEX_MANIFEST_TRACKED_REQUIRED_PATHS:
        if relative not in manifest_paths:
            errors.append(f"Required Codex file missing from install manifest: {relative}")
    if len(errors) == error_count:
        ok.append("Codex install manifest files match disk")


def validate_core_manifests(
    root: Path,
    source_root: Path,
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    asset_manifest = load_json_manifest(root / ".logos/generated/asset-manifest.json", errors)
    hash_manifest = load_json_manifest(root / ".logos/generated/asset-hashes.json", errors)
    guards_manifest = load_json_manifest(root / ".logos/generated/guards-manifest.json", errors)

    if isinstance(asset_manifest, dict):
        validate_asset_manifest(asset_manifest, ok, errors)

    if isinstance(hash_manifest, dict):
        validate_hash_manifest(source_root, hash_manifest, ok, warnings, errors)

    if isinstance(guards_manifest, dict):
        validate_guards_manifest(guards_manifest, ok, errors)


def validate_prompt_assembly(
    root: Path,
    marker_checks: dict[str, str],
    ok: list[str],
    errors: list[str],
) -> None:
    manifest = load_json_manifest(root / ".logos/generated/prompt-assembly-manifest.json", errors)
    if not isinstance(manifest, dict):
        return

    require_int(manifest, "schema_version", errors)
    input_count = require_int(manifest, "input_count", errors)
    for field in ("target", "profile", "mode"):
        require_str(manifest, field, errors)

    inputs = manifest.get("inputs")
    if not isinstance(inputs, list):
        errors.append("Prompt assembly manifest must contain inputs list.")
    elif input_count is not None and input_count != len(inputs):
        errors.append("Prompt assembly manifest input_count must equal inputs length.")

    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        errors.append("Prompt assembly manifest must contain string outputs list.")

    markers = manifest.get("markers")
    if not isinstance(markers, list) or not all(isinstance(item, str) for item in markers):
        errors.append("Prompt assembly manifest must contain string markers list.")

    for relative, marker in marker_checks.items():
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if marker not in text:
            errors.append(f"Missing assembled marker in {relative}: {marker}")

    ok.append("prompt assembly manifest shape")
    ok.append("assembled instruction markers")


def load_json_manifest(path: Path, errors: list[str]) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid manifest JSON {path}: {exc}")
        return None
    if not isinstance(loaded, dict):
        errors.append(f"Manifest must be a JSON object: {path}")
        return None
    return loaded


def validate_asset_manifest(
    manifest: dict[str, object],
    ok: list[str],
    errors: list[str],
) -> None:
    require_int(manifest, "schema_version", errors)
    total_assets = require_int(manifest, "total_assets", errors)
    selected_assets = require_int(manifest, "selected_assets", errors)
    require_int(manifest, "validation_issue_count", errors)
    validate_selection_policy(manifest.get("selection_policy"), errors)

    assets = manifest.get("assets")
    if not isinstance(assets, list):
        errors.append("Asset manifest must contain assets list.")
        return
    if total_assets is not None and total_assets != len(assets):
        errors.append("Asset manifest total_assets must equal assets length.")

    selected_count = 0
    for item in assets:
        if not isinstance(item, dict):
            errors.append("Asset manifest entries must be JSON objects.")
            continue
        validate_asset_entry(item, errors)
        if item.get("selected") is True:
            selected_count += 1
    if selected_assets is not None and selected_assets != selected_count:
        errors.append("Asset manifest selected_assets must equal selected entries.")

    ok.append("asset manifest shape")


def validate_asset_entry(item: dict[str, object], errors: list[str]) -> None:
    for field in ("id", "path", "kind", "status", "sha256"):
        require_str(item, field, errors)
    for field in ("selected", "has_frontmatter"):
        if not isinstance(item.get(field), bool):
            errors.append(f"Asset manifest entries require boolean {field}.")
    value = item.get("sha256")
    if isinstance(value, str) and not is_sha256(value):
        errors.append(f"Asset manifest entry has invalid sha256: {item.get('path')}")


def validate_hash_manifest(
    source_root: Path,
    manifest: dict[str, object],
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    require_int(manifest, "schema_version", errors)
    validate_selection_policy(manifest.get("selection_policy"), errors)
    if manifest.get("algorithm") != "sha256":
        errors.append("Asset hashes manifest algorithm must be sha256.")

    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("Asset hashes manifest must contain files list.")
        return
    ok.append("asset hashes shape")
    validate_core_hashes(source_root, files, ok, warnings, errors)


def validate_guards_manifest(
    manifest: dict[str, object],
    ok: list[str],
    errors: list[str],
) -> None:
    require_int(manifest, "schema_version", errors)
    guard_count = require_int(manifest, "guard_count", errors)
    validate_selection_policy(manifest.get("selection_policy"), errors)

    guards = manifest.get("guards")
    if not isinstance(guards, list):
        errors.append("Guards manifest must contain guards list.")
        return
    if guard_count is not None and guard_count != len(guards):
        errors.append("Guards manifest guard_count must equal guards length.")

    for item in guards:
        if not isinstance(item, dict):
            errors.append("Guard manifest entries must be JSON objects.")
            continue
        validate_guard_entry(item, errors)
    ok.append("guards manifest shape")


def validate_guard_entry(item: dict[str, object], errors: list[str]) -> None:
    for field in ("id", "path", "status", "sha256"):
        require_str(item, field, errors)
    for field in ("selected", "has_frontmatter"):
        if not isinstance(item.get(field), bool):
            errors.append(f"Guard manifest entries require boolean {field}.")
    value = item.get("sha256")
    if isinstance(value, str) and not is_sha256(value):
        errors.append(f"Guard manifest entry has invalid sha256: {item.get('path')}")
    if item.get("has_frontmatter") is True:
        if item.get("enforcement") != "hard":
            errors.append(f"Frontmatter guard must use hard enforcement: {item.get('path')}")
        if not isinstance(item.get("enforcement_status"), str):
            errors.append(f"Frontmatter guard requires enforcement_status: {item.get('path')}")


def validate_core_hashes(
    root: Path,
    files: list[object],
    ok: list[str],
    warnings: list[str],
    errors: list[str],
) -> None:
    current_by_path = {
        asset.relative_path.as_posix(): asset.sha256 for asset in scan_core_assets(root).assets
    }
    manifest_paths: set[str] = set()
    saw_file = False
    for item in files:
        if not isinstance(item, dict):
            errors.append("Asset hash entries must be JSON objects.")
            continue
        path = item.get("path")
        expected = item.get("sha256")
        if not isinstance(path, str) or not isinstance(expected, str):
            errors.append("Asset hash entries require path and sha256 strings.")
            continue
        if not is_sha256(expected):
            errors.append(f"Asset hash entry has invalid sha256: {path}")
            continue
        manifest_paths.add(path)
        saw_file = True
        current = current_by_path.get(path)
        if current is None:
            warnings.append(f"Core asset missing since install: {path}")
        elif current != expected:
            warnings.append(f"Core asset changed since install: {path}")

    for path in sorted(set(current_by_path) - manifest_paths):
        warnings.append(f"New core asset not present in install manifest: {path}")

    if saw_file:
        ok.append("core asset hashes checked")


def validate_selection_policy(value: object, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("Manifest requires selection_policy object.")
        return
    if value.get("default_status") != "active":
        errors.append("Manifest selection_policy.default_status must be active.")
    if value.get("raw_assets_selected") is not False:
        errors.append("Manifest selection_policy.raw_assets_selected must be false.")
    for field in ("target", "profile"):
        if not isinstance(value.get(field), str):
            errors.append(f"Manifest selection_policy requires string {field}.")


def require_int(mapping: dict[str, object], field: str, errors: list[str]) -> int | None:
    value = mapping.get(field)
    if not isinstance(value, int):
        errors.append(f"Manifest requires integer {field}.")
        return None
    return value


def require_str(mapping: dict[str, object], field: str, errors: list[str]) -> str | None:
    value = mapping.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"Manifest entries require string {field}.")
        return None
    return value


def is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)
