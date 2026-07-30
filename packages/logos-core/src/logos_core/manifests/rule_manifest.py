"""Write rule manifests for Logos core rule assets."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from logos_core import __version__
from logos_core.assets.scanner import CoreAssetScan


def build_rule_manifest(
    scan: CoreAssetScan,
    *,
    target: str = "codex-cli",
    profile: str = "codex",
) -> dict[str, Any]:
    rules = [asset for asset in scan.assets if asset.kind == "rule"]
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
        "rule_count": len(rules),
        "rules": [
            {
                "id": asset.asset_id,
                "path": asset.relative_path.as_posix(),
                "installed_path": installed_rule_path(asset.relative_path.as_posix()),
                "status": asset.status,
                "selected": asset.selected,
                "has_frontmatter": asset.has_frontmatter,
                "version": asset.frontmatter.get("version"),
                "enforcement": asset.frontmatter.get("enforcement"),
                "always_apply": asset.frontmatter.get("always_apply", False),
                "stages": asset.frontmatter.get("stages", []),
                "globs": asset.frontmatter.get("globs", []),
                "related_guards": asset.frontmatter.get("related_guards", []),
                "detail_reference": asset.frontmatter.get("detail_reference"),
                "detail_installed_path": installed_rule_path(
                    str(asset.frontmatter.get("detail_reference") or "")
                ),
                "sha256": asset.sha256,
            }
            for asset in rules
        ],
    }


def installed_rule_path(path: str) -> str:
    prefix = "rules/"
    if path.startswith(prefix):
        return f".agents/logos/rules/{path[len(prefix):]}"
    core_prefix = "core/rules/"
    if path.startswith(core_prefix):
        return f".agents/logos/rules/{path[len(core_prefix):]}"
    return path
