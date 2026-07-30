"""Scan core assets for Logos installation manifests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from logos_core.assets.loader import load_core_asset
from logos_core.assets.model import CORE_ASSET_SUFFIXES, CoreAsset
from logos_core.assets.validate import (
    Asset,
    ValidationIssue,
    validate_asset_graph,
    validate_frontmatter,
)


@dataclass(frozen=True)
class CoreAssetScan:
    assets: list[CoreAsset]
    validation_issues: list[ValidationIssue]

    @property
    def selected_assets(self) -> list[CoreAsset]:
        return [asset for asset in self.assets if asset.selected]


def scan_core_assets(root: Path) -> CoreAssetScan:
    core_root = root / "core"
    if not core_root.exists():
        return CoreAssetScan(assets=[], validation_issues=[])

    paths = [
        path
        for path in sorted(core_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in CORE_ASSET_SUFFIXES
    ]
    assets = [load_core_asset(core_root, path) for path in paths]
    validation_assets = [
        Asset(path=asset.path, frontmatter=asset.frontmatter)
        for asset in assets
        if asset.has_frontmatter
    ]
    validation_issues: list[ValidationIssue] = []
    for asset in validation_assets:
        validation_issues.extend(validate_frontmatter(asset))
    validation_issues.extend(validate_asset_graph(validation_assets))
    return CoreAssetScan(assets=assets, validation_issues=validation_issues)
