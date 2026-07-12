"""Uninstall Logos-managed files."""

from __future__ import annotations

from pathlib import Path

from logos_installer.install import read_manifest
from logos_installer.models import InstallResult


def uninstall_gemini(root: Path) -> InstallResult:
    manifest = read_manifest(root)
    removed: list[Path] = []
    skipped: list[Path] = []
    warnings: list[str] = []

    files = manifest.get("files")
    if not isinstance(files, list):
        return InstallResult(created=[], updated=[], skipped=[], warnings=["No install manifest found."])

    for item in files:
        if not isinstance(item, dict) or item.get("managed") is not True:
            continue
        value = item.get("path")
        if not isinstance(value, str):
            continue
        relative = Path(value)
        path = root / relative
        if path.exists():
            path.unlink()
            removed.append(relative)
        else:
            skipped.append(relative)

    cleanup_empty_parents(root, removed)
    return InstallResult(created=[], updated=removed, skipped=skipped, warnings=warnings)


def cleanup_empty_parents(root: Path, removed: list[Path]) -> None:
    stop_dirs = {root, root / ".gemini", root / ".agents", root / ".logos"}
    for relative in sorted(removed, key=lambda value: len(value.parts), reverse=True):
        current = (root / relative).parent
        while current not in stop_dirs and current.exists():
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent
