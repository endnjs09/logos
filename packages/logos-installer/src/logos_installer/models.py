"""Installer data models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderedFile:
    path: Path
    content: str
    managed: bool = True


@dataclass(frozen=True)
class InstallResult:
    created: list[Path]
    updated: list[Path]
    skipped: list[Path]
    warnings: list[str]
