from pathlib import Path

from logos_installer.doctor import validate_core_hashes, validate_guards_manifest


def test_validate_core_hashes_reports_changed_missing_and_new(tmp_path: Path) -> None:
    guard_dir = tmp_path / "core" / "guards"
    guard_dir.mkdir(parents=True)
    (guard_dir / "changed.yaml").write_text("new\n", encoding="utf-8")
    (guard_dir / "new.yaml").write_text("new\n", encoding="utf-8")
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_core_hashes(
        tmp_path,
        [
            {"path": "guards/changed.yaml", "sha256": "0" * 64},
            {"path": "guards/missing.yaml", "sha256": "1" * 64},
        ],
        ok,
        warnings,
        errors,
    )

    assert errors == []
    assert "core asset hashes checked" in ok
    assert "Core asset changed since install: guards/changed.yaml" in warnings
    assert "Core asset missing since install: guards/missing.yaml" in warnings
    assert "New core asset not present in install manifest: guards/new.yaml" in warnings


def test_validate_guards_manifest_rejects_count_mismatch() -> None:
    ok: list[str] = []
    errors: list[str] = []

    validate_guards_manifest(
        {
            "schema_version": 1,
            "selection_policy": {
                "default_status": "active",
                "raw_assets_selected": False,
                "target": "gemini-cli",
                "profile": "gemini",
            },
            "guard_count": 2,
            "guards": [],
        },
        ok,
        errors,
    )

    assert "Guards manifest guard_count must equal guards length." in errors
