"""Install Logos scaffold into a project."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from logos_core import __version__
from logos_core.assets.scanner import scan_core_assets
from logos_core.manifests.writer import write_core_manifests
from logos_core.prompt_assembly.assembler import assemble_prompt_bundle
from logos_core.prompt_assembly.manifest import write_prompt_assembly_manifest
from logos_installer.models import InstallError, InstallResult, RenderedFile
from logos_installer.render import MANAGED_MARKER, all_rendered_files


RUNTIME_DIRS = [
    ".gemini/commands",
    ".gemini/plugin",
    ".agents/skills",
    ".logos/session",
    ".logos/plans",
    ".logos/runs",
    ".logos/evidence",
    ".logos/approvals",
    ".logos/checkpoints",
    ".logos/cache",
    ".logos/generated",
]


def install_gemini(
    root: Path,
    *,
    source_root: Path | None = None,
    force: bool = False,
) -> InstallResult:
    source = (source_root or Path.cwd()).resolve()
    created: list[Path] = []
    updated: list[Path] = []
    skipped: list[Path] = []
    warnings: list[str] = []

    for directory in RUNTIME_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

    core_scan = scan_core_assets(source)
    if core_scan.validation_issues:
        raise InstallError(
            [
                f"{issue.path.as_posix()}: {issue.message}"
                for issue in core_scan.validation_issues
            ]
        )
    write_core_manifests(root, core_scan, target="gemini-cli", profile="gemini")
    assembly_bundle = assemble_prompt_bundle(source, core_scan, target="gemini-cli", profile="gemini")
    write_prompt_assembly_manifest(root, assembly_bundle)

    manifest = read_manifest(root)
    installed_files: list[dict[str, str | bool]] = []

    for rendered in all_rendered_files(
        root,
        template_base=source,
        extra_context=assembly_context(assembly_bundle),
    ):
        outcome = write_rendered_file(root, rendered, manifest=manifest, force=force)
        if outcome == "created":
            created.append(rendered.path)
        elif outcome == "updated":
            updated.append(rendered.path)
        else:
            skipped.append(rendered.path)
            warnings.append(f"Skipped unmanaged existing file: {rendered.path.as_posix()}")

        path = root / rendered.path
        if path.exists():
            installed_files.append(
                {
                    "path": rendered.path.as_posix(),
                    "managed": True,
                    "sha256": sha256_text(path.read_text(encoding="utf-8")),
                }
            )

    write_manifest(root, installed_files, source_root=source)
    return InstallResult(created=created, updated=updated, skipped=skipped, warnings=warnings)


def write_rendered_file(
    root: Path,
    rendered: RenderedFile,
    *,
    manifest: dict[str, object],
    force: bool,
) -> str:
    path = root / rendered.path
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(rendered.content, encoding="utf-8")
        return "created"

    if force or is_managed(path, rendered.path, manifest):
        path.write_text(rendered.content, encoding="utf-8")
        return "updated"

    return "skipped"


def is_managed(path: Path, relative_path: Path, manifest: dict[str, object]) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = ""
    if MANAGED_MARKER in text:
        return True

    files = manifest.get("files")
    if not isinstance(files, list):
        return False
    return any(
        isinstance(item, dict)
        and item.get("path") == relative_path.as_posix()
        and item.get("managed") is True
        for item in files
    )


def manifest_path(root: Path) -> Path:
    return root / ".logos/generated/install-manifest.json"


def read_manifest(root: Path) -> dict[str, object]:
    path = manifest_path(root)
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def write_manifest(root: Path, files: list[dict[str, str | bool]], *, source_root: Path) -> None:
    path = manifest_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "target": "gemini-cli",
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "logos_version": __version__,
        "source_root": str(source_root),
        "files": files,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def assembly_context(bundle) -> dict[str, str]:
    return {
        "logos_gemini_bootstrap_context": bundle.gemini_bootstrap_context,
        "logos_agents_operating_rules": bundle.agents_operating_rules,
        "logos_nous_skill_directive": bundle.nous_skill_directive,
    }
