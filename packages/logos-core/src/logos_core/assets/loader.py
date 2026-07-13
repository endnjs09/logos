"""Load Logos core assets from disk."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from logos_core.assets.model import CoreAsset
from logos_core.assets.validate import parse_frontmatter


def load_core_asset(core_root: Path, path: Path) -> CoreAsset:
    relative_path = path.relative_to(core_root)
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    frontmatter = read_frontmatter(text) if path.suffix.lower() == ".md" else {}
    return CoreAsset(
        path=path,
        relative_path=relative_path,
        suffix=path.suffix.lower(),
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        has_frontmatter=bool(frontmatter),
        frontmatter=frontmatter,
    )


def read_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = find_frontmatter_end(lines)
    if end is None:
        return {}
    try:
        return parse_frontmatter("\n".join(lines[1:end]))
    except ValueError:
        return {}


def find_frontmatter_end(lines: list[str]) -> int | None:
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index
    return None
