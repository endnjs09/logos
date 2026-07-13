"""Write asset manifests for discovered Logos core assets."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from logos_core import __version__
from logos_core.assets.scanner import CoreAssetScan


def selection_policy(target: str, profile: str) -> dict[str, str | bool]:
    return {
        "default_status": "active",
        "raw_assets_selected": False,
        "target": target,
        "profile": profile,
    }


def build_asset_manifest(
    scan: CoreAssetScan,
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "logos_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection_policy": selection_policy(target, profile),
        "total_assets": len(scan.assets),
        "selected_assets": len(scan.selected_assets),
        "validation_issue_count": len(scan.validation_issues),
        "assets": [
            {
                "id": asset.asset_id,
                "path": asset.relative_path.as_posix(),
                "kind": asset.kind,
                "status": asset.status,
                "selected": asset.selected,
                "has_frontmatter": asset.has_frontmatter,
                "version": asset.frontmatter.get("version"),
                "sha256": asset.sha256,
            }
            for asset in scan.assets
        ],
        "validation_issues": [
            {"path": issue.path.as_posix(), "message": issue.message}
            for issue in scan.validation_issues
        ],
    }
