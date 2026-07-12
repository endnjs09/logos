"""Install Logos scaffold into a project."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from logos_core import __version__
from logos_installer.models import InstallResult, RenderedFile
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


def install_gemini(root: Path, *, force: bool = False) -> InstallResult:
    created: list[Path] = []
    updated: list[Path] = []
    skipped: list[Path] = []
    warnings: list[str] = []

    for directory in RUNTIME_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

    manifest = read_manifest(root)
    installed_files: list[dict[str, str | bool]] = []

    for rendered in all_rendered_files(root):
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

    write_manifest(root, installed_files)
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


def write_manifest(root: Path, files: list[dict[str, str | bool]]) -> None:
    path = manifest_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "target": "gemini-cli",
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "logos_version": __version__,
        "files": files,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
