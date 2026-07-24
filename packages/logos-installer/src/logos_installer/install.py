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
from logos_core.work_state.memory import initialize_memory_state
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
    ".logos/evidence/artifacts",
    ".logos/memory",
    ".logos/approvals",
    ".logos/checkpoints",
    ".logos/cache",
    ".logos/generated",
]

CODEX_RUNTIME_DIRS = [
    ".codex",
    ".codex/hooks",
    ".agents/skills",
    ".agents/logos/procedures",
    ".agents/logos/roles",
    ".logos/session",
    ".logos/plans",
    ".logos/runs",
    ".logos/evidence",
    ".logos/evidence/artifacts",
    ".logos/memory",
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
    return install_target(
        root,
        target="gemini-cli",
        profile="gemini",
        runtime_dirs=RUNTIME_DIRS,
        source_root=source_root,
        force=force,
    )


def install_codex(
    root: Path,
    *,
    source_root: Path | None = None,
    force: bool = False,
) -> InstallResult:
    return install_target(
        root,
        target="codex-cli",
        profile="codex",
        runtime_dirs=CODEX_RUNTIME_DIRS,
        source_root=source_root,
        force=force,
    )


def install_target(
    root: Path,
    *,
    target: str,
    profile: str,
    runtime_dirs: list[str],
    source_root: Path | None = None,
    force: bool = False,
) -> InstallResult:
    source = (source_root or Path.cwd()).resolve()
    created: list[Path] = []
    updated: list[Path] = []
    skipped: list[Path] = []
    warnings: list[str] = []

    for directory in runtime_dirs:
        (root / directory).mkdir(parents=True, exist_ok=True)
    initialize_memory_state(root)

    core_scan = scan_core_assets(source)
    if core_scan.validation_issues:
        raise InstallError(
            [
                f"{issue.path.as_posix()}: {issue.message}"
                for issue in core_scan.validation_issues
            ]
        )
    write_core_manifests(root, core_scan, target=target, profile=profile)
    assembly_bundle = assemble_prompt_bundle(source, core_scan, target=target, profile=profile)
    write_prompt_assembly_manifest(root, assembly_bundle)

    manifest = read_manifest(root)
    installed_files: list[dict[str, str | bool]] = []
    rendered_files = all_rendered_files(
        root,
        template_base=source,
        target=target,
        extra_context=assembly_context(assembly_bundle),
    )
    validate_rendered_paths(rendered_files)
    rendered_paths = {rendered.path.as_posix() for rendered in rendered_files}

    for obsolete in remove_obsolete_managed_files(root, manifest, rendered_paths):
        warnings.append(f"Removed obsolete managed file: {obsolete.as_posix()}")

    for rendered in rendered_files:
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

    write_manifest(root, installed_files, source_root=source, target=target)
    return InstallResult(created=created, updated=updated, skipped=skipped, warnings=warnings)


def remove_obsolete_managed_files(
    root: Path,
    manifest: dict[str, object],
    rendered_paths: set[str],
) -> list[Path]:
    files = manifest.get("files")
    if not isinstance(files, list):
        return []

    removed: list[Path] = []
    for item in files:
        if not isinstance(item, dict) or item.get("managed") is not True:
            continue
        value = item.get("path")
        if not isinstance(value, str) or value in rendered_paths:
            continue
        path = root / value
        if not path.exists() or not is_managed(path, Path(value), manifest):
            continue
        path.unlink()
        removed.append(Path(value))
        remove_empty_parents(root, path.parent)
    return removed


def remove_empty_parents(root: Path, directory: Path) -> None:
    protected = {root, root / ".agents", root / ".agents/skills", root / ".agents/logos"}
    current = directory
    while current not in protected and root in [current, *current.parents]:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


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


def validate_rendered_paths(rendered_files: list[RenderedFile]) -> None:
    messages: list[str] = []
    for rendered in rendered_files:
        if rendered.path.is_absolute() or ".." in rendered.path.parts:
            messages.append(f"Rendered path must stay inside install root: {rendered.path.as_posix()}")
    if messages:
        raise InstallError(messages)


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


def write_manifest(
    root: Path,
    files: list[dict[str, str | bool]],
    *,
    source_root: Path,
    target: str,
) -> None:
    path = manifest_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "target": target,
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
        "logos_codex_operating_context": bundle.codex_operating_context,
        "logos_codex_nous_skill": bundle.codex_nous_skill,
        "logos_codex_codebase_exploration_skill": bundle.codex_codebase_exploration_skill,
        "logos_codex_implementation_planning_skill": bundle.codex_implementation_planning_skill,
        "logos_codex_risk_review_skill": bundle.codex_risk_review_skill,
        "logos_codex_verification_skill": bundle.codex_verification_skill,
    }
