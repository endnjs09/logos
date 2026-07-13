"""Write hash manifests for Logos core assets."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from logos_core import __version__
from logos_core.assets.scanner import CoreAssetScan


def build_hash_manifest(
    scan: CoreAssetScan,
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
) -> dict[str, Any]:
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
        "algorithm": "sha256",
        "files": [
            {
                "path": asset.relative_path.as_posix(),
                "sha256": asset.sha256,
            }
            for asset in scan.assets
        ],
    }
