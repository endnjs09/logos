from pathlib import Path

from logos_core.assets.scanner import scan_core_assets
from logos_core.prompt_assembly.assembler import assemble_prompt_bundle


def test_assembles_codex_operating_context(tmp_path: Path) -> None:
    write_asset(
        tmp_path / "core" / "prompts" / "base-system.md",
        "logos.template.base-system",
        "template",
        "# Base\n\nUse Logos.",
    )
    write_asset(
        tmp_path / "core" / "rules" / "verification.md",
        "logos.rule.verification",
        "rule",
        "# Verification\n\nVerify.",
    )

    scan = scan_core_assets(tmp_path)
    bundle = assemble_prompt_bundle(tmp_path, scan, target="codex-cli", profile="codex")

    assert bundle.outputs == [
        "AGENTS.md",
        ".agents/skills/nous/SKILL.md",
        ".agents/logos/procedures/codebase-exploration.md",
        ".agents/logos/procedures/implementation-planning.md",
        ".agents/logos/procedures/risk-review.md",
        ".agents/logos/procedures/verification.md",
    ]
    assert "logos-assembly: codex-operating-context" in bundle.codex_operating_context
    assert "logos-assembly: codex-nous-skill" in bundle.codex_nous_skill
    assert bundle.codex_codebase_exploration_skill == ""
    assert bundle.codex_implementation_planning_skill == ""
    assert bundle.codex_risk_review_skill == ""
    assert bundle.codex_verification_skill == ""
    assert "### Verification" not in bundle.codex_operating_context
    assert "### Verification" in bundle.codex_nous_skill
    assert "Verify." in bundle.codex_nous_skill


def write_asset(path: Path, asset_id: str, kind: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"id: {asset_id}\n"
        f"kind: {kind}\n"
        f"name: {path.stem}\n"
        f"description: {path.stem} asset.\n"
        "status: active\n"
        "version: 0.1.0\n"
        "targets:\n"
        "  - codex-cli\n"
        "profiles:\n"
        "  - codex\n"
        "depends_on: []\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
