from pathlib import Path

from logos_runner.stages.rule_selection import format_relevant_rules, select_relevant_rules


def test_selects_rules_by_stage_and_glob(tmp_path: Path) -> None:
    manifest = tmp_path / ".logos" / "generated" / "rules-manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "{\n"
        '  "schema_version": 1,\n'
        '  "rule_count": 2,\n'
        '  "rules": [\n'
        "    {\n"
        '      "id": "logos.rule.testing",\n'
        '      "selected": true,\n'
        '      "always_apply": false,\n'
        '      "stages": ["verify"],\n'
        '      "globs": ["**/*Test.*"],\n'
        '      "detail_reference": "core/rules/references/testing-details.md",\n'
        '      "detail_installed_path": ".agents/logos/rules/references/testing-details.md"\n'
        "    },\n"
        "    {\n"
        '      "id": "logos.rule.security",\n'
        '      "selected": true,\n'
        '      "always_apply": false,\n'
        '      "stages": ["review"],\n'
        '      "globs": ["**/*Security*"],\n'
        '      "detail_reference": "core/rules/references/security-details.md",\n'
        '      "detail_installed_path": ".agents/logos/rules/references/security-details.md"\n'
        "    }\n"
        "  ]\n"
        "}\n",
        encoding="utf-8",
    )

    selected = select_relevant_rules(
        tmp_path,
        stage_name="execute",
        paths=["src/test/java/UserServiceTest.java", "src/main/java/SecurityConfig.java"],
    )

    assert selected == [
        {
            "id": "logos.rule.testing",
            "reason": "glob:**/*Test.*",
            "detail_reference": ".agents/logos/rules/references/testing-details.md",
        },
        {
            "id": "logos.rule.security",
            "reason": "glob:**/*Security*",
            "detail_reference": ".agents/logos/rules/references/security-details.md",
        },
    ]


def test_formats_relevant_rule_pointers(tmp_path: Path) -> None:
    manifest = tmp_path / ".logos" / "generated" / "rules-manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "{\n"
        '  "schema_version": 1,\n'
        '  "rule_count": 1,\n'
        '  "rules": [\n'
        "    {\n"
        '      "id": "logos.rule.verification",\n'
        '      "selected": true,\n'
        '      "always_apply": false,\n'
        '      "stages": ["verify"],\n'
        '      "globs": [],\n'
        '      "detail_reference": "core/rules/references/verification-details.md",\n'
        '      "detail_installed_path": ".agents/logos/rules/references/verification-details.md"\n'
        "    }\n"
        "  ]\n"
        "}\n",
        encoding="utf-8",
    )

    formatted = format_relevant_rules(tmp_path, stage_name="verify")

    assert "`logos.rule.verification`" in formatted
    assert "stage:verify" in formatted
    assert ".agents/logos/rules/references/verification-details.md" in formatted
