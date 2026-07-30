from pathlib import Path

from logos_core.assets.scanner import scan_core_assets
from logos_core.manifests.asset_manifest import build_asset_manifest
from logos_core.manifests.guard_manifest import build_guard_manifest
from logos_core.manifests.hash_manifest import build_hash_manifest
from logos_core.manifests.rule_manifest import build_rule_manifest


def test_builds_asset_hash_and_guard_manifests(tmp_path: Path) -> None:
    guard_dir = tmp_path / "core" / "guards"
    guard_dir.mkdir(parents=True)
    (guard_dir / "secret.yaml").write_text(
        "id: logos.guard.secret\n"
        "kind: guard\n"
        "name: secret\n"
        "description: Test guard.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "enforcement: hard\n"
        "enforcement_status: policy-only\n"
        "decision: allow_block_ask\n"
        "risk_level: medium\n"
        "severity: 2\n"
        "surfaces: [pre_tool_use]\n"
        "inputs: [command]\n"
        "outputs: [guard-result]\n"
        "runtime_modules: [logos_core.guards.secret]\n"
        "detail_reference: core/guards/references/secret-details.md\n",
        encoding="utf-8",
    )

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
    assert guard_manifest["guards"][0]["selected"] is True
    assert guard_manifest["guards"][0]["surfaces"] == ["pre_tool_use"]
    assert guard_manifest["guards"][0]["runtime_modules"] == ["logos_core.guards.secret"]


def test_builds_rule_manifest(tmp_path: Path) -> None:
    rule_dir = tmp_path / "core" / "rules"
    rule_dir.mkdir(parents=True)
    (rule_dir / "testing.md").write_text(
        "---\n"
        "id: logos.rule.testing\n"
        "kind: rule\n"
        "name: testing\n"
        "description: Test rule.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "enforcement: soft\n"
        "always_apply: false\n"
        "stages: [execute, verify]\n"
        "globs:\n"
        "  - \"**/*Test.*\"\n"
        "related_guards: []\n"
        "detail_reference: core/rules/references/testing-details.md\n"
        "---\n"
        "\n"
        "# Testing\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)
    manifest = build_rule_manifest(scan)

    assert manifest["rule_count"] == 1
    assert manifest["rules"][0]["id"] == "logos.rule.testing"
    assert manifest["rules"][0]["installed_path"] == ".agents/logos/rules/testing.md"
    assert manifest["rules"][0]["enforcement"] == "soft"
    assert manifest["rules"][0]["stages"] == ["execute", "verify"]
    assert manifest["rules"][0]["globs"] == ["**/*Test.*"]
    assert (
        manifest["rules"][0]["detail_installed_path"]
        == ".agents/logos/rules/references/testing-details.md"
    )
