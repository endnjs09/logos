from pathlib import Path

from logos_core.assets.scanner import scan_core_assets


def test_scans_core_markdown_and_yaml(tmp_path: Path) -> None:
    core = tmp_path / "core"
    (core / "rules").mkdir(parents=True)
    (core / "guards").mkdir(parents=True)
    (core / "rules" / "plain.md").write_text("# Plain\n", encoding="utf-8")
    (core / "guards" / "secret.yaml").write_text(
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
        "inputs: [command]\n"
        "outputs: [guard-result]\n",
        encoding="utf-8",
    )
    (core / "rules" / "ignored.txt").write_text("ignore\n", encoding="utf-8")

    scan = scan_core_assets(tmp_path)

    assert [asset.relative_path.as_posix() for asset in scan.assets] == [
        "guards/secret.yaml",
        "rules/plain.md",
    ]
    assert scan.validation_issues == []


def test_validates_yaml_guard_frontmatter(tmp_path: Path) -> None:
    core = tmp_path / "core" / "guards"
    core.mkdir(parents=True)
    (core / "bad.yaml").write_text(
        "id: logos.guard.bad\n"
        "kind: guard\n"
        "name: bad\n"
        "description: Bad guard.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "enforcement_status: policy-only\n"
        "decision: record_only\n"
        "risk_level: high\n"
        "severity: 3\n"
        "inputs: [command]\n"
        "outputs: [guard-result]\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)

    assert [issue.message for issue in scan.validation_issues] == [
        "guard assets must use enforcement: hard",
        "high-risk or severity 3 guards cannot be record_only",
    ]


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
        "rule assets must use enforcement: soft",
        "rule assets require stages",
        "rule assets require globs",
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
        "enforcement: soft\n"
        "always_apply: false\n"
        "stages:\n"
        "  - verify\n"
        "globs: []\n"
        "---\n"
        "\n"
        "# Bad Id\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)

    assert [issue.message for issue in scan.validation_issues] == [
        "id must match logos.<kind>.<name>: expected logos.rule.bad-id"
    ]


def test_validates_rule_stage_values(tmp_path: Path) -> None:
    core = tmp_path / "core" / "rules"
    core.mkdir(parents=True)
    (core / "bad-stage.md").write_text(
        "---\n"
        "id: logos.rule.bad-stage\n"
        "kind: rule\n"
        "name: bad-stage\n"
        "description: Bad stage rule.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "enforcement: soft\n"
        "always_apply: false\n"
        "stages:\n"
        "  - planning\n"
        "globs: []\n"
        "---\n"
        "\n"
        "# Bad Stage\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)

    assert [issue.message for issue in scan.validation_issues] == [
        "unknown rule stage: planning"
    ]


def test_validates_workflow_stage_values(tmp_path: Path) -> None:
    core = tmp_path / "core" / "workflows"
    core.mkdir(parents=True)
    (core / "bad-workflow.yaml").write_text(
        "schema_version: 1\n"
        "id: logos.workflow.bad-workflow\n"
        "kind: workflow\n"
        "name: bad-workflow\n"
        "description: Bad workflow.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "required_stages:\n"
        "  - scan\n"
        "  - planning\n"
        "stage_policy:\n"
        "  exploration:\n"
        "    depth: focused\n",
        encoding="utf-8",
    )

    scan = scan_core_assets(tmp_path)

    assert [issue.message for issue in scan.validation_issues] == [
        "legacy workflow stage planning in required_stages; use plan",
        "legacy workflow stage exploration in stage_policy; use scan",
    ]
