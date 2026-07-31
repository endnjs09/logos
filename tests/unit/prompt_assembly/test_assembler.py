from pathlib import Path

from logos_core.assets.scanner import scan_core_assets
from logos_core.prompt_assembly.assembler import assemble_prompt_bundle


def test_assembles_minimal_active_assets(tmp_path: Path) -> None:
    write_asset(
        tmp_path / "core" / "prompts" / "worker-envelope.md",
        "logos.prompt.worker-envelope",
        "prompt",
        "# Base\n\nUse Logos.",
    )
    write_asset(
        tmp_path / "core" / "rules" / "verification.md",
        "logos.rule.verification",
        "rule",
        "# Verification\n\nVerify.",
    )
    raw = tmp_path / "core" / "rules" / "raw.md"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text("# Raw\n\nDo not assemble automatically.\n", encoding="utf-8")

    scan = scan_core_assets(tmp_path)
    bundle = assemble_prompt_bundle(tmp_path, scan)

    assert "logos-assembly: codex-operating-context" in bundle.codex_operating_context
    assert "Use Logos." in bundle.codex_operating_context
    assert "logos-assembly: agents-operating-rules" in bundle.agents_operating_rules
    assert "### Verification" in bundle.agents_operating_rules
    assert "# Verification" not in bundle.agents_operating_rules.splitlines()
    assert "Verify." in bundle.agents_operating_rules
    assert all(item.path != "rules/raw.md" for item in bundle.inputs)


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
