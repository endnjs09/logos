"""Template rendering for V1 installer assets."""

from __future__ import annotations

import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

from logos_core import __version__
from logos_installer.models import RenderedFile


MANAGED_MARKER = "<!-- logos-managed: true -->"
TEMPLATE_MAPS = {
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
        "codex/config.toml.template": ".codex/config.toml",
        "codex/hooks.json.template": ".codex/hooks.json",
        "codex/hooks/pre_tool_use.py.template": ".codex/hooks/pre_tool_use.py",
        "codex/hooks/permission_request.py.template": ".codex/hooks/permission_request.py",
        "codex/hooks/post_tool_use.py.template": ".codex/hooks/post_tool_use.py",
        "codex/hooks/post_compact.py.template": ".codex/hooks/post_compact.py",
        "logos/bin/logos-runner.ps1.template": ".logos/bin/logos-runner.ps1",
        "logos/bin/logos-runner.cmd.template": ".logos/bin/logos-runner.cmd",
        "logos/config.toml.template": ".logos/config.toml",
        "logos/target.toml.template": ".logos/target.toml",
        "logos/active-profile.toml.template": ".logos/active-profile.toml",
        "logos/session/nous-state.json.template": ".logos/session/nous-state.json",
    },
}

ROLE_SOURCE_MAP = {
    "codex-cli": {
        "core/roles/orch.md": ".agents/logos/roles/orch.md",
        "core/roles/exp.md": ".agents/logos/roles/exp.md",
        "core/roles/intk.md": ".agents/logos/roles/intk.md",
        "core/roles/sp.md": ".agents/logos/roles/sp.md",
        "core/roles/pln.md": ".agents/logos/roles/pln.md",
        "core/roles/exe.md": ".agents/logos/roles/exe.md",
        "core/roles/mem.md": ".agents/logos/roles/mem.md",
        "core/roles/implementation/bd.md": ".agents/logos/roles/bd.md",
        "core/roles/implementation/fd.md": ".agents/logos/roles/fd.md",
        "core/roles/implementation/db.md": ".agents/logos/roles/db.md",
        "core/roles/implementation/sys.md": ".agents/logos/roles/sys.md",
        "core/roles/implementation/test.md": ".agents/logos/roles/test.md",
        "core/roles/review/rv.md": ".agents/logos/roles/rv.md",
        "core/roles/review/sec.md": ".agents/logos/roles/sec.md",
        "core/roles/review/vf.md": ".agents/logos/roles/vf.md",
        "core/roles/references/orch-details.md": ".agents/logos/roles/references/orch-details.md",
        "core/roles/references/exp-details.md": ".agents/logos/roles/references/exp-details.md",
        "core/roles/references/intk-details.md": ".agents/logos/roles/references/intk-details.md",
        "core/roles/references/sp-details.md": ".agents/logos/roles/references/sp-details.md",
        "core/roles/references/pln-details.md": ".agents/logos/roles/references/pln-details.md",
        "core/roles/references/exe-details.md": ".agents/logos/roles/references/exe-details.md",
        "core/roles/references/mem-details.md": ".agents/logos/roles/references/mem-details.md",
        "core/roles/references/bd-details.md": ".agents/logos/roles/references/bd-details.md",
        "core/roles/references/fd-details.md": ".agents/logos/roles/references/fd-details.md",
        "core/roles/references/db-details.md": ".agents/logos/roles/references/db-details.md",
        "core/roles/references/sys-details.md": ".agents/logos/roles/references/sys-details.md",
        "core/roles/references/test-details.md": ".agents/logos/roles/references/test-details.md",
        "core/roles/references/rv-details.md": ".agents/logos/roles/references/rv-details.md",
        "core/roles/references/sec-details.md": ".agents/logos/roles/references/sec-details.md",
        "core/roles/references/vf-details.md": ".agents/logos/roles/references/vf-details.md",
    },
}


def all_rendered_files(
    root: Path,
    template_base: Path | None = None,
    target: str = "codex-cli",
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
        "profile": "codex",
        "logos_source_root": str(source_root),
        "logos_python_executable": sys.executable,
        "codex_executable": detect_codex_executable(),
    }
    if extra_context:
        context.update(extra_context)
    rendered = [
        RenderedFile(Path(destination), render_template(source_root / template_root / template, context))
        for template, destination in template_map.items()
    ]
    rendered.extend(render_role_sources(source_root, target))
    return rendered


def render_template(path: Path, context: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def render_role_sources(source_root: Path, target: str) -> list[RenderedFile]:
    rendered: list[RenderedFile] = []
    for source, destination in ROLE_SOURCE_MAP[target].items():
        content = (source_root / source).read_text(encoding="utf-8")
        rendered.append(RenderedFile(Path(destination), content))
    return rendered


def detect_codex_executable() -> str:
    for name in ("codex", "codex.cmd", "codex.exe"):
        found = shutil.which(name)
        if found:
            return found
    return ""
