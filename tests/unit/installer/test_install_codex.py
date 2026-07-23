from pathlib import Path
import json

from logos_installer.doctor import doctor_codex
from logos_installer.install import install_codex


def test_install_codex_generates_agents_config_and_manifests(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "source"
    project_root = tmp_path / "project"
    project_root.mkdir()
    create_codex_templates(source_root)
    create_core_assets(source_root)

    monkeypatch.chdir(source_root)
    result = install_codex(project_root)

    assert not result.warnings
    assert (project_root / "AGENTS.md").exists()
    assert (project_root / ".agents/skills/nous/SKILL.md").exists()
    assert not (project_root / ".agents/skills/codebase-exploration/SKILL.md").exists()
    assert not (project_root / ".agents/skills/implementation-planning/SKILL.md").exists()
    assert not (project_root / ".agents/skills/risk-review/SKILL.md").exists()
    assert not (project_root / ".agents/skills/verification/SKILL.md").exists()
    assert (project_root / ".agents/logos/procedures/codebase-exploration.md").exists()
    assert (project_root / ".agents/logos/procedures/implementation-planning.md").exists()
    assert (project_root / ".agents/logos/procedures/risk-review.md").exists()
    assert (project_root / ".agents/logos/procedures/verification.md").exists()
    assert (project_root / ".codex/config.toml").exists()
    assert (project_root / ".codex/hooks.json").exists()
    assert (project_root / ".codex/hooks/pre_tool_use.py").exists()
    assert (project_root / ".codex/hooks/permission_request.py").exists()
    assert (project_root / ".codex/hooks/post_tool_use.py").exists()
    assert (project_root / ".codex/hooks/post_compact.py").exists()
    assert (project_root / ".logos/session/nous-state.json").exists()
    assert (project_root / ".logos/generated/prompt-assembly-manifest.json").exists()
    assert "logos-assembly: codex-operating-context" in (
        project_root / "AGENTS.md"
    ).read_text(encoding="utf-8")

    report = doctor_codex(project_root, source_root=source_root)

    assert report.errors == []
    assert "Target support contains experimental surfaces." in report.warnings
    assert "Project-local Codex hooks may require trust review before they run." in report.warnings
    assert "AGENTS.md" in report.ok
    assert ".agents/skills/nous/SKILL.md" in report.ok
    assert ".agents/logos/procedures/codebase-exploration.md" in report.ok
    assert ".codex/config.toml" in report.ok
    assert ".codex/hooks.json" in report.ok
    assert ".codex/hooks/pre_tool_use.py" in report.ok
    assert ".codex/hooks/permission_request.py" in report.ok
    assert ".codex/hooks/post_tool_use.py" in report.ok
    assert ".codex/hooks/post_compact.py" in report.ok
    assert "target provides instructions" in report.ok
    assert "target provides skills" in report.ok
    assert "target provides procedures" in report.ok
    assert "target provides codex config" in report.ok
    assert "target provides hooks" in report.ok
    assert "codex config approval_policy" in report.ok
    assert "codex config sandbox_mode" in report.ok
    assert "codex config network_access" in report.ok
    assert "Codex hooks config shape" in report.ok
    assert ".logos/session" in report.ok
    assert ".logos/evidence" in report.ok
    assert ".logos/checkpoints" in report.ok
    assert ".logos/runs" in report.ok
    agents_text = (project_root / "AGENTS.md").read_text(encoding="utf-8")
    assert "Default Workflow" in agents_text
    assert "Skill Routing" in agents_text
    assert "uses Logos Nous Mode by default" in agents_text
    assert ".agents/skills/nous/SKILL.md" in agents_text
    assert ".agents/logos/procedures/" in agents_text
    assert ".logos/generated/prompt-assembly-manifest.json" in agents_text
    assert "logos-asset-version: 0.2.0" in agents_text
    assert "/nous" not in agents_text
    assert "Do not claim hard guard enforcement" not in agents_text
    assert "Guard Enforcement Status" not in agents_text
    nous_text = (project_root / ".agents/skills/nous/SKILL.md").read_text(encoding="utf-8")
    assert "version: 0.2.0" in nous_text
    assert "logos-asset-version: 0.2.0" in nous_text
    assert "logos.procedure.codebase-exploration" in nous_text
    assert "logos.procedure.implementation-planning" in nous_text
    assert "logos.procedure.risk-review" in nous_text
    assert "logos.procedure.verification" in nous_text
    assert ".agents/logos/procedures/codebase-exploration.md" in nous_text
    assert "logos.rule.verification" in nous_text
    assert "/nous" not in nous_text
    assert "Use `.agents/logos/procedures/risk-review.md` as the source of truth" in nous_text
    exploration_text = (
        project_root / ".agents/logos/procedures/codebase-exploration.md"
    ).read_text(encoding="utf-8")
    assert "kind: procedure" in exploration_text
    assert "logos-assembly: codex-codebase-exploration-skill" not in exploration_text
    assert "logos.rule.context-handoff" in exploration_text
    assert "### Verification" not in exploration_text
    planning_text = (
        project_root / ".agents/logos/procedures/implementation-planning.md"
    ).read_text(encoding="utf-8")
    assert "kind: procedure" in planning_text
    assert "logos-assembly: codex-implementation-planning-skill" not in planning_text
    assert "logos.rule.verification" in planning_text
    assert "### Verification" not in planning_text
    risk_text = (project_root / ".agents/logos/procedures/risk-review.md").read_text(encoding="utf-8")
    assert "version: 0.2.0" in risk_text
    assert "kind: procedure" in risk_text
    assert "## Guard Enforcement Status" in risk_text
    assert "Current Limits" not in risk_text
    assert "logos-assembly: codex-risk-review-skill" not in risk_text
    verification_text = (
        project_root / ".agents/logos/procedures/verification.md"
    ).read_text(encoding="utf-8")
    assert "logos-assembly: codex-verification-skill" not in verification_text
    assert "logos.rule.verification" in verification_text
    assert "### Verification" not in verification_text
    assert 'status = "not_used"' in (project_root / ".logos/target.toml").read_text(
        encoding="utf-8"
    )
    session_state = json.loads(
        (project_root / ".logos/session/nous-state.json").read_text(encoding="utf-8")
    )
    assert session_state["nous_mode"] is True
    assert session_state["activated_by"] == "logos install --target codex-cli"


def test_doctor_codex_rejects_unsafe_config(tmp_path: Path, monkeypatch) -> None:
    source_root, project_root = install_sample_codex_project(tmp_path, monkeypatch)
    (project_root / ".codex/config.toml").write_text(
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n'
        "\n"
        "[sandbox_workspace_write]\n"
        "network_access = true\n",
        encoding="utf-8",
    )

    report = doctor_codex(project_root, source_root=source_root)

    assert "Codex approval_policy must not be never for default Logos target." in report.errors
    assert "Codex sandbox_mode must not be danger-full-access for default Logos target." in report.errors
    assert "Codex sandbox_workspace_write.network_access must be false." in report.errors


def test_doctor_codex_rejects_obsolete_standalone_skills(tmp_path: Path, monkeypatch) -> None:
    source_root, project_root = install_sample_codex_project(tmp_path, monkeypatch)
    obsolete = project_root / ".agents/skills/codebase-exploration/SKILL.md"
    obsolete.parent.mkdir(parents=True)
    obsolete.write_text("# obsolete\n", encoding="utf-8")

    report = doctor_codex(project_root, source_root=source_root)

    assert (
        "Obsolete standalone Codex skill must not be installed: "
        ".agents/skills/codebase-exploration/SKILL.md"
    ) in report.errors
    assert "Unexpected auto-discoverable Codex skill: .agents/skills/codebase-exploration" in report.errors


def test_doctor_codex_rejects_missing_instruction_links(tmp_path: Path, monkeypatch) -> None:
    source_root, project_root = install_sample_codex_project(tmp_path, monkeypatch)
    (project_root / "AGENTS.md").write_text("# Missing link\n", encoding="utf-8")
    (project_root / ".agents/skills/nous/SKILL.md").write_text(
        "---\nid: logos.skill.nous\nkind: skill\nname: nous\n"
        "description: Nous.\nstatus: active\nversion: 0.2.0\n---\n",
        encoding="utf-8",
    )

    report = doctor_codex(project_root, source_root=source_root)

    assert "AGENTS.md must reference .agents/skills/nous/SKILL.md." in report.errors
    assert (
        ".agents/skills/nous/SKILL.md must reference "
        ".agents/logos/procedures/codebase-exploration.md."
    ) in report.errors


def test_doctor_codex_rejects_procedure_trigger_fields(tmp_path: Path, monkeypatch) -> None:
    source_root, project_root = install_sample_codex_project(tmp_path, monkeypatch)
    procedure = project_root / ".agents/logos/procedures/codebase-exploration.md"
    procedure.write_text(
        "---\n"
        "id: logos.procedure.codebase-exploration\n"
        "kind: procedure\n"
        "name: codebase-exploration\n"
        "description: Explore.\n"
        "status: active\n"
        "version: 0.2.0\n"
        "triggers:\n"
        "  - explore\n"
        "do_not_trigger_when:\n"
        "  - never\n"
        "---\n"
        "Explore.\n",
        encoding="utf-8",
    )

    report = doctor_codex(project_root, source_root=source_root)

    assert (
        ".agents/logos/procedures/codebase-exploration.md: procedure must not use triggers."
        in report.errors
    )
    assert (
        ".agents/logos/procedures/codebase-exploration.md: "
        "procedure must not use do_not_trigger_when."
    ) in report.errors


def test_doctor_codex_rejects_manifest_mismatch(tmp_path: Path, monkeypatch) -> None:
    source_root, project_root = install_sample_codex_project(tmp_path, monkeypatch)
    manifest_path = project_root / ".logos/generated/install-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"] = [
        item for item in manifest["files"] if item["path"] != ".agents/skills/nous/SKILL.md"
    ]
    manifest["files"].append({"path": ".gemini/GEMINI.md", "managed": True, "sha256": "0" * 64})
    manifest["files"].append({"path": "../outside.md", "managed": True, "sha256": "0" * 64})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    report = doctor_codex(project_root, source_root=source_root)

    assert "Required Codex file missing from install manifest: .agents/skills/nous/SKILL.md" in report.errors
    assert "Gemini artifact listed in Codex install manifest: .gemini/GEMINI.md" in report.errors
    assert "Install manifest path must stay inside root: ../outside.md" in report.errors


def install_sample_codex_project(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    source_root = tmp_path / "source"
    project_root = tmp_path / "project"
    project_root.mkdir()
    create_codex_templates(source_root)
    create_core_assets(source_root)
    monkeypatch.chdir(source_root)
    install_codex(project_root)
    return source_root, project_root


def create_codex_templates(root: Path) -> None:
    templates = root / "targets" / "codex-cli" / "templates"
    files = {
        "AGENTS.md.template": (
            "---\n"
            "id: logos.template.codex-agents\n"
            "kind: template\n"
            "name: codex-agents\n"
            "description: Codex agents.\n"
            "status: active\n"
            "version: 0.2.0\n"
            "---\n"
            "<!-- logos-manifest: .logos/generated/prompt-assembly-manifest.json -->\n"
            "<!-- logos-asset-version: 0.2.0 -->\n"
            "## Default Workflow\n"
            "This installed project uses Logos Nous Mode by default.\n"
            "## Skill Routing\n"
            "Use `.agents/skills/nous/SKILL.md`.\n"
            "Detailed step procedures live under `.agents/logos/procedures/`.\n"
            "{{logos_codex_operating_context}}\n"
        ),
        "agents/skills/nous/SKILL.md.template": (
            "---\nid: logos.skill.nous\nkind: skill\nname: nous\n"
            "description: Nous.\nstatus: active\nversion: 0.2.0\n"
            "depends_on:\n"
            "  - logos.procedure.codebase-exploration\n"
            "  - logos.procedure.implementation-planning\n"
            "  - logos.procedure.risk-review\n"
            "  - logos.procedure.verification\n"
            "related_rules:\n"
            "  - logos.rule.verification\n"
            "---\n"
            "<!-- logos-asset-version: 0.2.0 -->\n"
            "Use `.agents/logos/procedures/risk-review.md` as the source of truth.\n"
            "{{logos_codex_nous_skill}}\n"
        ),
        "agents/logos/procedures/codebase-exploration.md.template": (
            "---\nid: logos.procedure.codebase-exploration\nkind: procedure\n"
            "name: codebase-exploration\ndescription: Explore.\n"
            "status: active\nversion: 0.2.0\n"
            "related_rules:\n"
            "  - logos.rule.context-handoff\n"
            "---\n"
            "Explore only.\n"
        ),
        "agents/logos/procedures/implementation-planning.md.template": (
            "---\nid: logos.procedure.implementation-planning\nkind: procedure\n"
            "name: implementation-planning\ndescription: Plan.\n"
            "status: active\nversion: 0.2.0\n"
            "depends_on:\n"
            "  - logos.procedure.codebase-exploration\n"
            "related_rules:\n"
            "  - logos.rule.verification\n"
            "---\n"
            "Plan only.\n"
        ),
        "agents/logos/procedures/risk-review.md.template": (
            "---\nid: logos.procedure.risk-review\nkind: procedure\n"
            "name: risk-review\ndescription: Risk.\n"
            "status: active\nversion: 0.2.0\n"
            "related_rules:\n"
            "  - logos.rule.security\n"
            "---\n"
            "## Guard Enforcement Status\n"
            "Review risk.\n"
        ),
        "agents/logos/procedures/verification.md.template": (
            "---\nid: logos.procedure.verification\nkind: procedure\n"
            "name: verification\ndescription: Verify.\n"
            "status: active\nversion: 0.2.0\n"
            "related_rules:\n"
            "  - logos.rule.verification\n"
            "---\n"
            "Verify only.\n"
        ),
        "codex/config.toml.template": (
            'approval_policy = "on-request"\n'
            'sandbox_mode = "workspace-write"\n'
            "\n"
            "[sandbox_workspace_write]\n"
            "network_access = false\n"
        ),
        "codex/hooks.json.template": (
            '{"hooks":{"PreToolUse":[{"hooks":[{"command":"python .codex/hooks/pre_tool_use.py"}]}],'
            '"PermissionRequest":[{"hooks":[{"command":"python .codex/hooks/permission_request.py"}]}],'
            '"PostToolUse":[{"hooks":[{"command":"python .codex/hooks/post_tool_use.py"}]}],'
            '"PostCompact":[{"hooks":[{"command":"python .codex/hooks/post_compact.py"}]}]}}\n'
        ),
        "codex/hooks/pre_tool_use.py.template": "# logos-managed: true\n",
        "codex/hooks/permission_request.py.template": "# logos-managed: true\n",
        "codex/hooks/post_tool_use.py.template": "# logos-managed: true\n",
        "codex/hooks/post_compact.py.template": "# logos-managed: true\n",
        "logos/config.toml.template": 'target = "codex-cli"\n',
        "logos/target.toml.template": (
            "[target]\n"
            'name = "codex-cli"\n'
            "\n"
            "[provides]\n"
            'instructions = "AGENTS.md"\n'
            'skills = ".agents/skills"\n'
            'procedures = ".agents/logos/procedures"\n'
            'config = ".codex/config.toml"\n'
            'hooks = ".codex/hooks.json"\n'
            "\n"
            "[target_support.agents_md]\n"
            'status = "confirmed"\n'
            "[target_support.commands]\n"
            'status = "not_used"\n'
            "[target_support.execpolicy]\n"
            'status = "experimental"\n'
        ),
        "logos/active-profile.toml.template": "[profile]\nname = \"codex\"\n",
        "logos/session/nous-state.json.template": (
            "{\"schema_version\": 1, \"nous_mode\": true, "
            "\"activated_at\": \"{{generated_at}}\", "
            "\"activated_by\": \"logos install --target codex-cli\", "
            "\"last_updated_at\": \"{{generated_at}}\", "
            "\"target\": \"codex-cli\", \"profile\": \"codex\"}\n"
        ),
    }
    for relative, content in files.items():
        path = templates / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def create_core_assets(root: Path) -> None:
    write_asset(
        root / "core" / "prompts" / "base-system.md",
        "logos.template.base-system",
        "template",
        "# Base\n\nUse Logos.",
    )
    write_asset(
        root / "core" / "rules" / "verification.md",
        "logos.rule.verification",
        "rule",
        "# Verification\n\nVerify.",
    )


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
