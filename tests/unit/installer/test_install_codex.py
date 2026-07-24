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
    assert (project_root / ".agents/logos/procedures/intake.md").exists()
    assert (project_root / ".agents/logos/procedures/exploration.md").exists()
    assert (project_root / ".agents/logos/procedures/spec.md").exists()
    assert (project_root / ".agents/logos/procedures/planning.md").exists()
    assert (project_root / ".agents/logos/procedures/execution.md").exists()
    assert (project_root / ".agents/logos/procedures/verification.md").exists()
    assert (project_root / ".agents/logos/procedures/review.md").exists()
    assert (project_root / ".agents/logos/procedures/resume.md").exists()
    assert (project_root / ".agents/logos/roles/orch.md").exists()
    assert (project_root / ".agents/logos/roles/sp.md").exists()
    assert (project_root / ".agents/logos/roles/bd.md").exists()
    assert (project_root / ".codex/config.toml").exists()
    assert (project_root / ".codex/hooks.json").exists()
    assert (project_root / ".codex/hooks/pre_tool_use.py").exists()
    assert (project_root / ".codex/hooks/permission_request.py").exists()
    assert (project_root / ".codex/hooks/post_tool_use.py").exists()
    assert (project_root / ".codex/hooks/post_compact.py").exists()
    assert (project_root / ".logos/session/nous-state.json").exists()
    assert (project_root / ".logos/memory/active-work.json").exists()
    assert (project_root / ".logos/memory/run-index.json").exists()
    assert (project_root / ".logos/memory/open-items.json").exists()
    assert (project_root / ".logos/memory/resume-snapshot.md").exists()
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
    assert ".agents/logos/procedures/intake.md" in report.ok
    assert ".agents/logos/procedures/spec.md" in report.ok
    assert ".agents/logos/roles/orch.md" in report.ok
    assert ".agents/logos/roles/sp.md" in report.ok
    assert ".codex/config.toml" in report.ok
    assert ".codex/hooks.json" in report.ok
    assert ".codex/hooks/pre_tool_use.py" in report.ok
    assert ".codex/hooks/permission_request.py" in report.ok
    assert ".codex/hooks/post_tool_use.py" in report.ok
    assert ".codex/hooks/post_compact.py" in report.ok
    assert "target provides instructions" in report.ok
    assert "target provides skills" in report.ok
    assert "target provides procedures" in report.ok
    assert "target provides roles" in report.ok
    assert "target provides codex config" in report.ok
    assert "target provides hooks" in report.ok
    assert "codex config approval_policy" in report.ok
    assert "codex config sandbox_mode" in report.ok
    assert "codex config network_access" in report.ok
    assert "Codex hooks config shape" in report.ok
    assert ".logos/session" in report.ok
    assert ".logos/evidence" in report.ok
    assert ".logos/evidence/artifacts" in report.ok
    assert ".logos/memory" in report.ok
    assert ".logos/plans" in report.ok
    assert ".logos/checkpoints" in report.ok
    assert ".logos/runs" in report.ok
    assert ".logos/memory/active-work.json" in report.ok
    assert ".logos/memory/run-index.json" in report.ok
    assert ".logos/memory/open-items.json" in report.ok
    assert ".logos/memory/resume-snapshot.md" in report.ok
    assert "active-work shape" in report.ok
    assert "run-index shape" in report.ok
    assert "open-items shape" in report.ok
    assert "no run records yet" in report.ok
    agents_text = (project_root / "AGENTS.md").read_text(encoding="utf-8")
    assert "Default Workflow" in agents_text
    assert "Skill Routing" in agents_text
    assert "uses Logos Nous Mode by default" in agents_text
    assert ".agents/skills/nous/SKILL.md" in agents_text
    assert "planning has produced `next_step: executor`" in agents_text
    assert "Read `.agents/logos/procedures/execution.md` only after" in agents_text
    assert ".agents/logos/procedures/" in agents_text
    assert ".logos/generated/prompt-assembly-manifest.json" in agents_text
    assert ".logos/memory/resume-snapshot.md" in agents_text
    assert "Do not read" in agents_text
    assert "logos-asset-version: 0.2.0" in agents_text
    assert "/nous" not in agents_text
    assert "Do not claim hard guard enforcement" not in agents_text
    assert "Guard Enforcement Status" not in agents_text
    nous_text = (project_root / ".agents/skills/nous/SKILL.md").read_text(encoding="utf-8")
    assert "version: 0.2.0" in nous_text
    assert "logos-asset-version: 0.2.0" in nous_text
    assert "logos.procedure.intake" in nous_text
    assert "logos.procedure.exploration" in nous_text
    assert "logos.procedure.spec" in nous_text
    assert "logos.procedure.planning" in nous_text
    assert "logos.procedure.execution" in nous_text
    assert "logos.procedure.verification" in nous_text
    assert "logos.procedure.review" in nous_text
    assert "logos.procedure.resume" in nous_text
    assert "logos.role.orch" in nous_text
    assert "logos.role.sp" in nous_text
    assert "logos.implementation-role.bd" in nous_text
    assert ".agents/logos/procedures/exploration.md" in nous_text
    assert ".agents/logos/procedures/spec.md" in nous_text
    assert ".agents/logos/roles/orch.md" in nous_text
    assert ".agents/logos/roles/sp.md" in nous_text
    assert ".logos/memory/resume-snapshot.md" in nous_text
    assert "Resume Policy" in nous_text
    assert "logos.rule.verification" in nous_text
    assert "/nous" not in nous_text
    assert "Use `.agents/logos/procedures/review.md` as the source of truth" in nous_text
    assert "Complexity is an internal agent judgment" in nous_text
    assert "ask the blocking questions and wait" in nous_text
    assert "## Runner Gate" in nous_text
    assert "Do not edit files, run build/test commands, or start implementation" in nous_text
    assert "Use Logos Runner as the default orchestration path." in nous_text
    assert "manual recovery path" in nous_text
    assert "A Codex `Updated Plan` checklist is not enough by itself" in nous_text
    assert "exploration → spec → planning" not in nous_text
    intake_text = (project_root / ".agents/logos/procedures/intake.md").read_text(
        encoding="utf-8"
    )
    assert "essential_information_status" in intake_text
    assert "complexity: low | middle | high" in intake_text
    assert "no more than 10 at once" in intake_text
    assert "next_step: ask_user | exploration" in intake_text
    assert "schemas/intake-result.schema.json" in intake_text
    assert "interview_draft_update" in intake_text
    assert ".logos/memory/resume-snapshot.md" in intake_text
    assert "Do not scan `.logos/runs/` or `.logos/evidence/` by default during intake" in intake_text
    intk_text = (project_root / ".agents/logos/roles/intk.md").read_text(
        encoding="utf-8"
    )
    assert "role_code: intk" in intk_text
    assert "intake-result" in intk_text
    assert "Interview Draft" in intk_text
    exploration_text = (
        project_root / ".agents/logos/procedures/exploration.md"
    ).read_text(encoding="utf-8")
    assert "kind: procedure" in exploration_text
    assert "version: 0.2.0" in exploration_text
    assert "exploration-result" in exploration_text
    assert "schemas/exploration-result.schema.json" in exploration_text
    assert "Read-Only Boundary" in exploration_text
    assert "Snapshot Check" in exploration_text
    assert "Feature Scan" in exploration_text
    assert "code_evidence" in exploration_text
    assert "project_intent" in exploration_text
    assert "hash_diff" in exploration_text
    assert "interview_draft_update" in exploration_text
    assert "next_step: clarification | spec" in exploration_text
    assert "role_code: exp" not in exploration_text
    assert "logos.rule.context-handoff" in exploration_text
    assert "### Verification" not in exploration_text
    exp_text = (project_root / ".agents/logos/roles/exp.md").read_text(
        encoding="utf-8"
    )
    assert "role_code: exp" in exp_text
    assert "exploration-result" in exp_text
    assert "read-only" in exp_text
    spec_text = (project_root / ".agents/logos/procedures/spec.md").read_text(
        encoding="utf-8"
    )
    assert "kind: procedure" in spec_text
    assert "spec-result" in spec_text
    assert "schemas/spec-result.schema.json" in spec_text
    assert "Low Fast Path" in spec_text
    assert "Mini Spec" in spec_text
    assert "Structured Spec" in spec_text
    assert "blocking_open_questions" in spec_text
    assert "next_step: task_plan | clarification" in spec_text
    sp_text = (project_root / ".agents/logos/roles/sp.md").read_text(
        encoding="utf-8"
    )
    assert "role_code: sp" in sp_text
    assert "spec-result" in sp_text
    assert "Spec separate from Task Plan" in sp_text
    planning_text = (
        project_root / ".agents/logos/procedures/planning.md"
    ).read_text(encoding="utf-8")
    assert "kind: procedure" in planning_text
    assert "version: 0.2.0" in planning_text
    assert "logos-asset-version: 0.2.0" in planning_text
    assert "logos.procedure.exploration" in planning_text
    assert "logos.procedure.spec" in planning_text
    assert "task-plan-result" in planning_text
    assert "schemas/task-plan-result.schema.json" in planning_text
    assert "schemas/context-handoff.schema.json" in planning_text
    assert "Context Handoff" in planning_text
    assert "Review-Lite" in planning_text
    assert "target_files" in planning_text
    assert "role_routing" in planning_text
    assert "verification_plan" in planning_text
    assert "rollback_criteria" in planning_text
    assert "next_step: executor | clarification | spec" in planning_text
    assert "logos.rule.verification" in planning_text
    assert "### Verification" not in planning_text
    pln_text = (project_root / ".agents/logos/roles/pln.md").read_text(
        encoding="utf-8"
    )
    assert "role_code: pln" in pln_text
    assert "task-plan-result" in pln_text
    assert "context-handoff" in pln_text
    assert "Review-Lite" in pln_text
    assert "Do not edit files during planning" in pln_text
    risk_text = (project_root / ".agents/logos/procedures/review.md").read_text(encoding="utf-8")
    assert "version: 0.2.0" in risk_text
    assert "kind: procedure" in risk_text
    assert "## Guard Enforcement Status" in risk_text
    assert "Current Limits" not in risk_text
    assert "logos.role.sec" in risk_text
    verification_text = (
        project_root / ".agents/logos/procedures/verification.md"
    ).read_text(encoding="utf-8")
    assert "logos-assembly: codex-verification-skill" not in verification_text
    assert "logos.rule.verification" in verification_text
    assert "### Verification" not in verification_text
    role_text = (project_root / ".agents/logos/roles/bd.md").read_text(encoding="utf-8")
    assert "kind: implementation-role" in role_text
    assert "role_code: bd" in role_text
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
        ".agents/logos/procedures/intake.md."
    ) in report.errors


def test_doctor_codex_rejects_procedure_trigger_fields(tmp_path: Path, monkeypatch) -> None:
    source_root, project_root = install_sample_codex_project(tmp_path, monkeypatch)
    procedure = project_root / ".agents/logos/procedures/intake.md"
    procedure.write_text(
        "---\n"
        "id: logos.procedure.intake\n"
        "kind: procedure\n"
        "name: intake\n"
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
        ".agents/logos/procedures/intake.md: procedure must not use triggers."
        in report.errors
    )
    assert (
        ".agents/logos/procedures/intake.md: "
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
            "Do not edit files, run build/test commands, or start implementation before planning has produced `next_step: executor`.\n"
            "Read `.agents/logos/procedures/execution.md` only after the planning gate returns `next_step: executor`.\n"
            "Do not read `.logos/runs/` or `.logos/evidence/` by default.\n"
            "Read `.logos/memory/resume-snapshot.md` first when context is unclear.\n"
            "{{logos_codex_operating_context}}\n"
        ),
        "agents/skills/nous/SKILL.md.template": (
            "---\nid: logos.skill.nous\nkind: skill\nname: nous\n"
            "description: Nous.\nstatus: active\nversion: 0.2.0\n"
            "depends_on:\n"
            "  - logos.procedure.intake\n"
            "  - logos.procedure.exploration\n"
            "  - logos.procedure.spec\n"
            "  - logos.procedure.planning\n"
            "  - logos.procedure.execution\n"
            "  - logos.procedure.verification\n"
            "  - logos.procedure.review\n"
            "  - logos.procedure.resume\n"
            "  - logos.role.orch\n"
            "  - logos.role.sp\n"
            "  - logos.implementation-role.bd\n"
            "related_rules:\n"
            "  - logos.rule.verification\n"
            "---\n"
            "<!-- logos-asset-version: 0.2.0 -->\n"
            "Use `.agents/logos/procedures/review.md` as the source of truth.\n"
            "Use `.agents/logos/procedures/intake.md`.\n"
            "Use `.agents/logos/procedures/exploration.md`.\n"
            "Use `.agents/logos/procedures/spec.md`.\n"
            "Use `.agents/logos/procedures/planning.md`.\n"
            "Load `.agents/logos/procedures/execution.md` only after planning returns `next_step: executor`.\n"
            "Use `.agents/logos/procedures/verification.md`.\n"
            "Use `.agents/logos/procedures/review.md`.\n"
            "Use `.agents/logos/procedures/resume.md`.\n"
            "Use `.agents/logos/roles/orch.md`.\n"
            "Use `.agents/logos/roles/intk.md`.\n"
            "Use `.agents/logos/roles/exp.md`.\n"
            "Use `.agents/logos/roles/sp.md`.\n"
            "Use `.agents/logos/roles/pln.md`.\n"
            "Use `.agents/logos/roles/exe.md`.\n"
            "Use `.agents/logos/roles/bd.md`.\n"
            "Use `.agents/logos/roles/fd.md`.\n"
            "Use `.agents/logos/roles/db.md`.\n"
            "Use `.agents/logos/roles/sys.md`.\n"
            "Use `.agents/logos/roles/test.md`.\n"
            "Use `.agents/logos/roles/sec.md`.\n"
            "Use `.agents/logos/roles/rv.md`.\n"
            "Use `.agents/logos/roles/vf.md`.\n"
            "Use `.agents/logos/roles/mem.md`.\n"
            "Complexity is an internal agent judgment.\n"
            "If intake finds missing essential information, ask the blocking questions and wait.\n"
            "## Runner Gate\n"
            "Do not edit files, run build/test commands, or start implementation before planning has produced `next_step: executor`.\n"
            "A Codex `Updated Plan` checklist is not enough by itself.\n"
            "## Resume Policy\n"
            "Read `.logos/memory/resume-snapshot.md` first when context is unclear.\n"
            "{{logos_codex_nous_skill}}\n"
        ),
        "agents/logos/procedures/intake.md.template": (
            "---\nid: logos.procedure.intake\nkind: procedure\n"
            "name: intake\ndescription: Intake.\n"
            "status: active\nversion: 0.2.0\n"
            "outputs:\n"
            "  - intake-result\n"
            "schemas:\n"
            "  - schemas/intake-result.schema.json\n"
            "related_rules:\n"
            "  - logos.rule.context-handoff\n"
            "---\n"
            "essential_information_status\n"
            "complexity: low | middle | high\n"
            "no more than 10 at once\n"
            "next_step: ask_user | exploration\n"
            "interview_draft_update\n"
            ".logos/memory/resume-snapshot.md\n"
            "Do not scan `.logos/runs/` or `.logos/evidence/` by default during intake\n"
        ),
        "agents/logos/procedures/planning.md.template": (
            "---\nid: logos.procedure.planning\nkind: procedure\n"
            "name: planning\ndescription: Plan.\n"
            "status: active\nversion: 0.2.0\n"
            "outputs:\n"
            "  - task-plan-result\n"
            "  - context-handoff\n"
            "schemas:\n"
            "  - schemas/task-plan-result.schema.json\n"
            "  - schemas/context-handoff.schema.json\n"
            "depends_on:\n"
            "  - logos.procedure.intake\n"
            "  - logos.procedure.exploration\n"
            "  - logos.procedure.spec\n"
            "related_rules:\n"
            "  - logos.rule.verification\n"
            "---\n"
            "<!-- logos-asset-version: 0.2.0 -->\n"
            "Task Plan\n"
            "task-plan-result\n"
            "Context Handoff\n"
            "context-handoff\n"
            "Review-Lite\n"
            "target_files\n"
            "role_routing\n"
            "verification_plan\n"
            "rollback_criteria\n"
            "next_step: executor | clarification | spec\n"
        ),
        "agents/logos/procedures/spec.md.template": (
            "---\nid: logos.procedure.spec\nkind: procedure\n"
            "name: spec\ndescription: Spec.\n"
            "status: active\nversion: 0.1.0\n"
            "outputs:\n"
            "  - spec-result\n"
            "schemas:\n"
            "  - schemas/spec-result.schema.json\n"
            "depends_on:\n"
            "  - logos.procedure.intake\n"
            "  - logos.procedure.exploration\n"
            "  - logos.role.sp\n"
            "---\n"
            "## Low Fast Path\n"
            "## Mini Spec\n"
            "## Structured Spec\n"
            "blocking_open_questions\n"
            "next_step: task_plan | clarification\n"
        ),
        "agents/logos/procedures/exploration.md.template": (
            "---\nid: logos.procedure.exploration\nkind: procedure\n"
            "name: exploration\ndescription: Explore.\n"
            "status: active\nversion: 0.2.0\n"
            "outputs:\n"
            "  - exploration-result\n"
            "schemas:\n"
            "  - schemas/exploration-result.schema.json\n"
            "related_rules:\n"
            "  - logos.rule.context-handoff\n"
            "---\n"
            "## Read-Only Boundary\n"
            "## Snapshot Check\n"
            "## Feature Scan\n"
            "code_evidence\n"
            "project_intent\n"
            "hash_diff\n"
            "interview_draft_update\n"
            "next_step: clarification | spec\n"
        ),
        "agents/logos/procedures/execution.md.template": (
            "---\nid: logos.procedure.execution\nkind: procedure\n"
            "name: execution\ndescription: Execute.\n"
            "status: active\nversion: 0.2.0\n"
            "depends_on:\n"
            "  - logos.procedure.planning\n"
            "---\n"
            "Execute only.\n"
        ),
        "agents/logos/procedures/review.md.template": (
            "---\nid: logos.procedure.review\nkind: procedure\n"
            "name: review\ndescription: Risk.\n"
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
        "agents/logos/procedures/resume.md.template": (
            "---\nid: logos.procedure.resume\nkind: procedure\n"
            "name: resume\ndescription: Resume.\n"
            "status: active\nversion: 0.2.0\n"
            "---\n"
            "Resume only.\n"
        ),
        "agents/logos/roles/orch.md.template": (
            "---\nid: logos.role.orch\nkind: role\nname: orch\n"
            "description: Orchestrate.\nstatus: active\nversion: 0.1.0\n"
            "role_code: orch\n---\n"
        ),
        "agents/logos/roles/intk.md.template": (
            "---\nid: logos.role.intk\nkind: role\nname: intk\n"
            "description: Intake.\nstatus: active\nversion: 0.2.0\n"
            "outputs:\n"
            "  - intake-result\n"
            "schemas:\n"
            "  - schemas/intake-result.schema.json\n"
            "role_code: intk\n---\n"
            "intake-result\n"
            "Interview Draft\n"
        ),
        "agents/logos/roles/pln.md.template": (
            "---\nid: logos.role.pln\nkind: role\nname: pln\n"
            "description: Plan.\nstatus: active\nversion: 0.2.0\n"
            "outputs:\n"
            "  - task-plan-result\n"
            "  - context-handoff\n"
            "schemas:\n"
            "  - schemas/task-plan-result.schema.json\n"
            "  - schemas/context-handoff.schema.json\n"
            "role_code: pln\n---\n"
            "task-plan-result\n"
            "context-handoff\n"
            "Review-Lite\n"
            "Do not edit files during planning\n"
        ),
        "agents/logos/roles/sp.md.template": (
            "---\nid: logos.role.sp\nkind: role\nname: sp\n"
            "description: Spec.\nstatus: active\nversion: 0.1.0\n"
            "outputs:\n"
            "  - spec-result\n"
            "schemas:\n"
            "  - schemas/spec-result.schema.json\n"
            "role_code: sp\n---\n"
            "Spec separate from Task Plan\n"
            "spec-result\n"
        ),
        "agents/logos/roles/exp.md.template": (
            "---\nid: logos.role.exp\nkind: role\nname: exp\n"
            "description: Explore.\nstatus: active\nversion: 0.2.0\n"
            "outputs:\n"
            "  - exploration-result\n"
            "schemas:\n"
            "  - schemas/exploration-result.schema.json\n"
            "role_code: exp\n---\n"
            "read-only exploration-result\n"
        ),
        "agents/logos/roles/exe.md.template": (
            "---\nid: logos.role.exe\nkind: role\nname: exe\n"
            "description: Execute.\nstatus: active\nversion: 0.1.0\n"
            "role_code: exe\n---\n"
        ),
        "agents/logos/roles/bd.md.template": (
            "---\nid: logos.implementation-role.bd\nkind: implementation-role\nname: bd\n"
            "description: Backend.\nstatus: active\nversion: 0.1.0\n"
            "role_code: bd\n---\n"
        ),
        "agents/logos/roles/fd.md.template": (
            "---\nid: logos.implementation-role.fd\nkind: implementation-role\nname: fd\n"
            "description: Frontend.\nstatus: active\nversion: 0.1.0\n"
            "role_code: fd\n---\n"
        ),
        "agents/logos/roles/db.md.template": (
            "---\nid: logos.implementation-role.db\nkind: implementation-role\nname: db\n"
            "description: Database.\nstatus: active\nversion: 0.1.0\n"
            "role_code: db\n---\n"
        ),
        "agents/logos/roles/sys.md.template": (
            "---\nid: logos.implementation-role.sys\nkind: implementation-role\nname: sys\n"
            "description: System.\nstatus: active\nversion: 0.1.0\n"
            "role_code: sys\n---\n"
        ),
        "agents/logos/roles/test.md.template": (
            "---\nid: logos.implementation-role.test\nkind: implementation-role\nname: test\n"
            "description: Test.\nstatus: active\nversion: 0.1.0\n"
            "role_code: test\n---\n"
        ),
        "agents/logos/roles/sec.md.template": (
            "---\nid: logos.role.sec\nkind: role\nname: sec\n"
            "description: Security.\nstatus: active\nversion: 0.1.0\n"
            "role_code: sec\n---\n"
        ),
        "agents/logos/roles/rv.md.template": (
            "---\nid: logos.role.rv\nkind: role\nname: rv\n"
            "description: Review.\nstatus: active\nversion: 0.1.0\n"
            "role_code: rv\n---\n"
        ),
        "agents/logos/roles/vf.md.template": (
            "---\nid: logos.role.vf\nkind: role\nname: vf\n"
            "description: Verify.\nstatus: active\nversion: 0.1.0\n"
            "role_code: vf\n---\n"
        ),
        "agents/logos/roles/mem.md.template": (
            "---\nid: logos.role.mem\nkind: role\nname: mem\n"
            "description: Memory.\nstatus: active\nversion: 0.1.0\n"
            "role_code: mem\n---\n"
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
            'roles = ".agents/logos/roles"\n'
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
