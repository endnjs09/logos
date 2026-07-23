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
        "agents/logos/procedures/codebase-exploration.md.template": ".agents/logos/procedures/codebase-exploration.md",
        "agents/logos/procedures/implementation-planning.md.template": ".agents/logos/procedures/implementation-planning.md",
        "agents/logos/procedures/risk-review.md.template": ".agents/logos/procedures/risk-review.md",
        "agents/logos/procedures/verification.md.template": ".agents/logos/procedures/verification.md",
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
