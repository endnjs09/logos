from pathlib import Path

import pytest

from logos_installer.install import install_gemini
from logos_installer.install import validate_rendered_paths
from logos_installer.models import InstallError
from logos_installer.models import RenderedFile


def test_install_generates_core_manifests(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "source"
    project_root = tmp_path / "project"
    project_root.mkdir()
    create_templates(source_root)

    guard_dir = source_root / "core" / "guards"
    guard_dir.mkdir(parents=True)
    (guard_dir / "secret.yaml").write_text("schema_version: 1\n", encoding="utf-8")

    monkeypatch.chdir(source_root)
    result = install_gemini(project_root)

    assert not result.warnings
    assert (project_root / ".logos/generated/asset-manifest.json").exists()
    assert (project_root / ".logos/generated/asset-hashes.json").exists()
    assert (project_root / ".logos/generated/guards-manifest.json").exists()
    assert (project_root / ".logos/generated/prompt-assembly-manifest.json").exists()
    assert "logos-assembly: gemini-bootstrap" in (
        project_root / ".gemini/GEMINI.md"
    ).read_text(encoding="utf-8")
    assert "logos-assembly: agents-operating-rules" in (
        project_root / ".agents/AGENTS.md"
    ).read_text(encoding="utf-8")
    assert "logos-assembly: nous-skill-directive" in (
        project_root / ".agents/skills/nous/SKILL.md"
    ).read_text(encoding="utf-8")


def test_install_rejects_invalid_frontmatter_asset(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "source"
    project_root = tmp_path / "project"
    project_root.mkdir()
    create_templates(source_root)

    rule_dir = source_root / "core" / "rules"
    rule_dir.mkdir(parents=True)
    (rule_dir / "bad.md").write_text(
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

    monkeypatch.chdir(source_root)

    with pytest.raises(InstallError):
        install_gemini(project_root)


def test_validate_rendered_paths_rejects_paths_outside_root() -> None:
    rendered_files = [
        RenderedFile(Path("../outside.md"), "outside"),
        RenderedFile(Path("C:/absolute.md"), "absolute"),
    ]

    with pytest.raises(InstallError) as exc:
        validate_rendered_paths(rendered_files)

    assert "Rendered path must stay inside install root: ../outside.md" in exc.value.messages
    assert "Rendered path must stay inside install root: C:/absolute.md" in exc.value.messages


def create_templates(root: Path) -> None:
    templates = root / "targets" / "gemini-cli" / "templates"
    files = {
        "gemini/GEMINI.md.template": "---\nid: test.gemini\nkind: template\nname: gemini\ndescription: Gemini.\nstatus: active\nversion: 0.1.0\n---\n",
        "gemini/settings.json.template": "{}\n",
        "gemini/plugin/README.md.template": "# Plugin\n",
        "gemini/commands/nous.toml.template": 'description = "Nous."\nprompt = "Activate nous."\n',
        "agents/AGENTS.md.template": "---\nid: test.agents\nkind: template\nname: agents\ndescription: Agents.\nstatus: active\nversion: 0.1.0\n---\n",
        "agents/skills/nous/SKILL.md.template": "---\nid: test.skill.nous\nkind: skill\nname: nous\ndescription: Nous.\nstatus: active\nversion: 0.1.0\n---\n",
        "agents/skills/codebase-exploration/SKILL.md.template": "---\nid: test.skill.explore\nkind: skill\nname: explore\ndescription: Explore.\nstatus: active\nversion: 0.1.0\n---\n",
        "agents/skills/implementation-planning/SKILL.md.template": "---\nid: test.skill.plan\nkind: skill\nname: plan\ndescription: Plan.\nstatus: active\nversion: 0.1.0\n---\n",
        "agents/skills/risk-review/SKILL.md.template": "---\nid: test.skill.risk\nkind: skill\nname: risk\ndescription: Risk.\nstatus: active\nversion: 0.1.0\n---\n",
        "agents/skills/verification/SKILL.md.template": "---\nid: test.skill.verify\nkind: skill\nname: verify\ndescription: Verify.\nstatus: active\nversion: 0.1.0\n---\n",
        "logos/config.toml.template": "name = \"test\"\n",
        "logos/target.toml.template": "target = \"gemini-cli\"\n",
        "logos/active-profile.toml.template": "profile = \"default\"\n",
        "logos/session/nous-state.json.template": (
            "{\"schema_version\": 1, \"nous_mode\": false, "
            "\"activated_at\": null, \"activated_by\": null, "
            "\"last_updated_at\": \"{{generated_at}}\", "
            "\"target\": \"gemini-cli\", \"profile\": \"gemini\"}\n"
        ),
    }
    for relative, content in files.items():
        path = templates / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
