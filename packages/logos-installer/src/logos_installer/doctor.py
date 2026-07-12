"""Doctor checks for a Logos Gemini installation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from logos_core.assets.validate import validate_paths


REQUIRED_PATHS = [
    ".gemini/GEMINI.md",
    ".gemini/commands/nous.md",
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
]


@dataclass(frozen=True)
class DoctorReport:
    ok: list[str]
    warnings: list[str]
    errors: list[str]

    @property
    def passed(self) -> bool:
        return not self.errors


def doctor_gemini(root: Path) -> DoctorReport:
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if (root / relative).exists():
            ok.append(relative)
        else:
            errors.append(f"Missing required path: {relative}")

    target_toml = root / ".logos/target.toml"
    if target_toml.exists():
        text = target_toml.read_text(encoding="utf-8")
        if 'status = "assumed"' in text:
            warnings.append("Target support contains assumed surfaces.")
        if 'status = "unsupported"' in text:
            errors.append("Target support contains unsupported active surfaces.")

    validate_session_state(root, ok, errors)
    validate_manifest(root, ok, errors)

    markdown_paths = collect_markdown_assets(root)
    for issue in validate_paths([path for path in markdown_paths if path.exists()]):
        errors.append(f"{issue.path}: {issue.message}")

    return DoctorReport(ok=ok, warnings=warnings, errors=errors)


def collect_markdown_assets(root: Path) -> list[Path]:
    paths = {root / relative for relative in REQUIRED_PATHS if relative.endswith(".md")}

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
    if not isinstance(loaded.get("nous_mode"), bool):
        errors.append("Session state requires boolean nous_mode.")
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
