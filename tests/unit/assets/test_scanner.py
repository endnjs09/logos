from pathlib import Path

from logos_core.assets.scanner import scan_core_assets


def test_scans_core_markdown_and_yaml(tmp_path: Path) -> None:
    core = tmp_path / "core"
    (core / "rules").mkdir(parents=True)
    (core / "guards").mkdir(parents=True)
    (core / "rules" / "plain.md").write_text("# Plain\n", encoding="utf-8")
    (core / "guards" / "secret.yaml").write_text("schema_version: 1\n", encoding="utf-8")
    (core / "rules" / "ignored.txt").write_text("ignore\n", encoding="utf-8")

    scan = scan_core_assets(tmp_path)

    assert [asset.relative_path.as_posix() for asset in scan.assets] == [
        "guards/secret.yaml",
        "rules/plain.md",
    ]
    assert scan.validation_issues == []


def test_validates_markdown_with_frontmatter(tmp_path: Path) -> None:
    core = tmp_path / "core" / "rules"
    core.mkdir(parents=True)
    (core / "bad.md").write_text(
        "---\n"
        "id: logos.rule.bad\n"
        "kind: rule\n"
        "name: bad\n"
        "description: Bad rule.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "enforcement: hard\n"
        "---\n"
        "\n"
        "# Bad\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)

    assert [issue.message for issue in scan.validation_issues] == [
        "rule assets must not use enforcement: hard"
    ]


def test_validates_id_kind_name_pattern(tmp_path: Path) -> None:
    core = tmp_path / "core" / "rules"
    core.mkdir(parents=True)
    (core / "bad-id.md").write_text(
        "---\n"
        "id: logos.rules.bad-id\n"
        "kind: rule\n"
        "name: bad-id\n"
        "description: Bad id rule.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "---\n"
        "\n"
        "# Bad Id\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)

    assert [issue.message for issue in scan.validation_issues] == [
        "id must match logos.<kind>.<name>: expected logos.rule.bad-id"
    ]
