"""Write guard manifests for Logos core guard assets."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from logos_core import __version__
from logos_core.assets.scanner import CoreAssetScan


def build_guard_manifest(
    scan: CoreAssetScan,
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
) -> dict[str, Any]:
    guards = [asset for asset in scan.assets if asset.kind == "guard"]
    return {
        "schema_version": 1,
        "logos_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection_policy": {
            "default_status": "active",
            "raw_assets_selected": False,
            "target": target,
            "profile": profile,
        },
        "guard_count": len(guards),
        "guards": [
            {
                "id": asset.asset_id,
                "path": asset.relative_path.as_posix(),
                "status": asset.status,
                "selected": asset.selected,
                "has_frontmatter": asset.has_frontmatter,
                "enforcement": asset.frontmatter.get("enforcement"),
                "enforcement_status": asset.frontmatter.get("enforcement_status"),
                "decision": asset.frontmatter.get("decision"),
                "risk_level": asset.frontmatter.get("risk_level"),
                "severity": asset.frontmatter.get("severity"),
                "sha256": asset.sha256,
            }
            for asset in guards
        ],
    }
