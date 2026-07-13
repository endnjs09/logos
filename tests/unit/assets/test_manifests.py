from pathlib import Path

from logos_core.assets.scanner import scan_core_assets
from logos_core.manifests.asset_manifest import build_asset_manifest
from logos_core.manifests.guard_manifest import build_guard_manifest
from logos_core.manifests.hash_manifest import build_hash_manifest


def test_builds_asset_hash_and_guard_manifests(tmp_path: Path) -> None:
    guard_dir = tmp_path / "core" / "guards"
    guard_dir.mkdir(parents=True)
    (guard_dir / "secret.yaml").write_text("schema_version: 1\n", encoding="utf-8")

    scan = scan_core_assets(tmp_path)
    asset_manifest = build_asset_manifest(scan)
    hash_manifest = build_hash_manifest(scan)
    guard_manifest = build_guard_manifest(scan)

    assert asset_manifest["total_assets"] == 1
    assert asset_manifest["selection_policy"]["raw_assets_selected"] is False
    assert asset_manifest["assets"][0]["kind"] == "guard"
    assert len(asset_manifest["assets"][0]["sha256"]) == 64
    assert hash_manifest["algorithm"] == "sha256"
    assert len(hash_manifest["files"][0]["sha256"]) == 64
    assert guard_manifest["guard_count"] == 1
    assert guard_manifest["selection_policy"]["default_status"] == "active"
    assert guard_manifest["guards"][0]["path"] == "guards/secret.yaml"
