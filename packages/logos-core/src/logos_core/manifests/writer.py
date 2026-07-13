"""Persist generated Logos manifests."""

from __future__ import annotations

import json
from pathlib import Path

from logos_core.assets.scanner import CoreAssetScan
from logos_core.manifests.asset_manifest import build_asset_manifest
from logos_core.manifests.guard_manifest import build_guard_manifest
from logos_core.manifests.hash_manifest import build_hash_manifest


def write_core_manifests(
    root: Path,
    scan: CoreAssetScan,
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
) -> None:
    generated = root / ".logos/generated"
    generated.mkdir(parents=True, exist_ok=True)
    write_json(generated / "asset-manifest.json", build_asset_manifest(scan, target=target, profile=profile))
    write_json(generated / "asset-hashes.json", build_hash_manifest(scan, target=target, profile=profile))
    write_json(generated / "guards-manifest.json", build_guard_manifest(scan, target=target, profile=profile))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
