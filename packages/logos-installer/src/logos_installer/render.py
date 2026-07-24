"""Template rendering for V1 installer assets."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from logos_core import __version__
from logos_installer.models import RenderedFile


MANAGED_MARKER = "<!-- logos-managed: true -->"
TEMPLATE_MAPS = {
    "gemini-cli": {
        "gemini/GEMINI.md.template": ".gemini/GEMINI.md",
        "gemini/settings.json.template": ".gemini/settings.json",
        "gemini/plugin/README.md.template": ".gemini/plugin/README.md",
        "gemini/commands/nous.toml.template": ".gemini/commands/nous.toml",
        "agents/AGENTS.md.template": ".agents/AGENTS.md",
        "agents/skills/nous/SKILL.md.template": ".agents/skills/nous/SKILL.md",
        "agents/skills/codebase-exploration/SKILL.md.template": ".agents/skills/codebase-exploration/SKILL.md",
        "agents/skills/implementation-planning/SKILL.md.template": ".agents/skills/implementation-planning/SKILL.md",
        "agents/skills/risk-review/SKILL.md.template": ".agents/skills/risk-review/SKILL.md",
        "agents/skills/verification/SKILL.md.template": ".agents/skills/verification/SKILL.md",
        "logos/config.toml.template": ".logos/config.toml",
        "logos/target.toml.template": ".logos/target.toml",
        "logos/active-profile.toml.template": ".logos/active-profile.toml",
        "logos/session/nous-state.json.template": ".logos/session/nous-state.json",
    },
    "codex-cli": {
        "AGENTS.md.template": "AGENTS.md",
        "agents/skills/nous/SKILL.md.template": ".agents/skills/nous/SKILL.md",
        "agents/logos/procedures/intake.md.template": ".agents/logos/procedures/intake.md",
        "agents/logos/procedures/exploration.md.template": ".agents/logos/procedures/exploration.md",
        "agents/logos/procedures/spec.md.template": ".agents/logos/procedures/spec.md",
        "agents/logos/procedures/planning.md.template": ".agents/logos/procedures/planning.md",
        "agents/logos/procedures/execution.md.template": ".agents/logos/procedures/execution.md",
        "agents/logos/procedures/verification.md.template": ".agents/logos/procedures/verification.md",
        "agents/logos/procedures/review.md.template": ".agents/logos/procedures/review.md",
        "agents/logos/procedures/resume.md.template": ".agents/logos/procedures/resume.md",
        "agents/logos/roles/orch.md.template": ".agents/logos/roles/orch.md",
        "agents/logos/roles/intk.md.template": ".agents/logos/roles/intk.md",
        "agents/logos/roles/exp.md.template": ".agents/logos/roles/exp.md",
        "agents/logos/roles/sp.md.template": ".agents/logos/roles/sp.md",
        "agents/logos/roles/pln.md.template": ".agents/logos/roles/pln.md",
        "agents/logos/roles/exe.md.template": ".agents/logos/roles/exe.md",
        "agents/logos/roles/bd.md.template": ".agents/logos/roles/bd.md",
        "agents/logos/roles/fd.md.template": ".agents/logos/roles/fd.md",
        "agents/logos/roles/db.md.template": ".agents/logos/roles/db.md",
        "agents/logos/roles/sys.md.template": ".agents/logos/roles/sys.md",
        "agents/logos/roles/test.md.template": ".agents/logos/roles/test.md",
        "agents/logos/roles/sec.md.template": ".agents/logos/roles/sec.md",
        "agents/logos/roles/rv.md.template": ".agents/logos/roles/rv.md",
        "agents/logos/roles/vf.md.template": ".agents/logos/roles/vf.md",
        "agents/logos/roles/mem.md.template": ".agents/logos/roles/mem.md",
        "codex/config.toml.template": ".codex/config.toml",
        "codex/hooks.json.template": ".codex/hooks.json",
        "codex/hooks/pre_tool_use.py.template": ".codex/hooks/pre_tool_use.py",
        "codex/hooks/permission_request.py.template": ".codex/hooks/permission_request.py",
        "codex/hooks/post_tool_use.py.template": ".codex/hooks/post_tool_use.py",
        "codex/hooks/post_compact.py.template": ".codex/hooks/post_compact.py",
        "logos/config.toml.template": ".logos/config.toml",
        "logos/target.toml.template": ".logos/target.toml",
        "logos/active-profile.toml.template": ".logos/active-profile.toml",
        "logos/session/nous-state.json.template": ".logos/session/nous-state.json",
    },
}


def all_rendered_files(
    root: Path,
    template_base: Path | None = None,
    target: str = "gemini-cli",
    extra_context: dict[str, str] | None = None,
) -> list[RenderedFile]:
    source_root = template_base or Path.cwd()
    template_root = Path("targets") / target / "templates"
    template_map = TEMPLATE_MAPS[target]
    context = {
        "logos_version": __version__,
        "project_name": root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "profile": "codex" if target == "codex-cli" else "gemini",
    }
    if extra_context:
        context.update(extra_context)
    return [
        RenderedFile(Path(destination), render_template(source_root / template_root / template, context))
        for template, destination in template_map.items()
    ]


def render_template(path: Path, context: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    return text
