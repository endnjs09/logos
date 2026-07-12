"""Template rendering for V1 installer assets."""

from __future__ import annotations

from pathlib import Path

from logos_core import __version__
from logos_installer.models import RenderedFile


MANAGED_MARKER = "<!-- logos-managed: true -->"
TEMPLATE_ROOT = Path("targets/gemini-cli/templates")

TEMPLATE_MAP = {
    "gemini/GEMINI.md.template": ".gemini/GEMINI.md",
    "gemini/settings.json.template": ".gemini/settings.json",
    "gemini/plugin/README.md.template": ".gemini/plugin/README.md",
    "gemini/commands/nous.md.template": ".gemini/commands/nous.md",
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
}


def all_rendered_files(root: Path, template_base: Path | None = None) -> list[RenderedFile]:
    source_root = template_base or Path.cwd()
    context = {
        "logos_version": __version__,
        "project_name": root.name,
    }
    return [
        RenderedFile(Path(destination), render_template(source_root / TEMPLATE_ROOT / template, context))
        for template, destination in TEMPLATE_MAP.items()
    ]


def render_template(path: Path, context: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    return text
