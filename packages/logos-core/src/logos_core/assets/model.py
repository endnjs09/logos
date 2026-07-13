"""Asset models for Logos core asset compilation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


CORE_ASSET_SUFFIXES = {".md", ".yaml", ".yml"}


@dataclass(frozen=True)
class CoreAsset:
    """A file discovered under the core asset tree."""

    path: Path
    relative_path: Path
    suffix: str
    sha256: str
    has_frontmatter: bool
    frontmatter: dict[str, Any]

    @property
    def asset_id(self) -> str:
        value = self.frontmatter.get("id")
        if isinstance(value, str) and value:
            return value
        return path_asset_id(self.relative_path)

    @property
    def kind(self) -> str:
        value = self.frontmatter.get("kind")
        if isinstance(value, str) and value:
            return value
        return infer_kind(self.relative_path)

    @property
    def status(self) -> str:
        value = self.frontmatter.get("status")
        if isinstance(value, str) and value:
            return value
        return "raw"

    @property
    def selected(self) -> bool:
        return self.status == "active"


def infer_kind(relative_path: Path) -> str:
    if not relative_path.parts:
        return "asset"
    first = relative_path.parts[0]
    mapping = {
        "roles": "role",
        "rules": "rule",
        "guards": "guard",
        "workflows": "workflow",
        "prompts": "prompt",
        "profiles": "profile",
        "context": "context",
        "evaluation": "rubric",
    }
    return mapping.get(first, "asset")


def path_asset_id(relative_path: Path) -> str:
    stem = relative_path.with_suffix("").as_posix().replace("/", ".").replace("_", "-")
    return f"logos.core.{stem}"
