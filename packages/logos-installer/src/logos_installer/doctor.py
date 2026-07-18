"""Doctor checks for a Logos Gemini installation."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path

from logos_core.assets.scanner import scan_core_assets
from logos_core.assets.validate import validate_paths
from logos_core.session.state import validate_session_state_payload


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
    ".agents/logos/procedures/codebase-exploration.md",
    ".agents/logos/procedures/implementation-planning.md",
    ".agents/logos/procedures/risk-review.md",
    ".agents/logos/procedures/verification.md",
    ".codex/config.toml",
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
        if 'status = "unsupported"' in text:
            errors.append("Target support contains unsupported active surfaces.")

    if target == "codex-cli":
        validate_target_provides(root, target, ok, errors)
        validate_codex_config(root, ok, warnings, errors)

    validate_session_state(root, ok, errors)
    validate_manifest(root, ok, errors)
    validate_core_manifests(root, source, ok, warnings, errors)
    validate_prompt_assembly(root, marker_checks, ok, errors)

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
        loaded = tomllib.loads(path.read_text(encoding="utf-8"))
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
                "config": ".codex/config.toml",
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
        loaded = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"Invalid Codex config TOML: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append("Codex config must be a TOML table.")
        return

    validate_codex_approval_policy(loaded, ok, warnings)
    validate_codex_sandbox_mode(loaded, ok, warnings, errors)
    validate_codex_network_access(loaded, ok, warnings)


def validate_codex_approval_policy(
    config: dict[str, object],
    ok: list[str],
    warnings: list[str],
) -> None:
    value = config.get("approval_policy")
    if value == "on-request":
        ok.append("codex config approval_policy")
        return
    if value == "never":
        warnings.append("Codex approval_policy is never; risky commands may run without prompts.")
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
        warnings.append("Codex workspace network_access is true.")
        return
    warnings.append("Codex config is missing sandbox_workspace_write.network_access.")


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


def validate_manifest(root: Path, ok: list[str], errors: list[str]) -> None:
    path = root / ".logos/generated/install-manifest.json"
    if not path.exists():
        return
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid install manifest JSON: {exc}")
        return
    if not isinstance(loaded, dict):
        errors.append("Install manifest must be a JSON object.")
        return
    files = loaded.get("files")
    if not isinstance(files, list) or not files:
        errors.append("Install manifest must contain managed files.")
        return
    ok.append("install manifest shape")


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
