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


class InstallError(RuntimeError):
    """Raised when Logos cannot safely complete installation."""

    def __init__(self, messages: list[str]) -> None:
        super().__init__("\n".join(messages))
        self.messages = messages
