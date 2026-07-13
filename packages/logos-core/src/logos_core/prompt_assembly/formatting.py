"""Markdown formatting helpers for assembled instructions."""

from __future__ import annotations

from collections.abc import Iterable

from logos_core.prompt_assembly.model import AssemblySource


def source_section(title: str, sources: Iterable[AssemblySource]) -> str:
    parts = [f"## {title}"]
    for source in sources:
        parts.append(f"### {source.relative_path.as_posix()}")
        if source.path.suffix.lower() in {".yaml", ".yml"}:
            parts.append("```yaml")
            parts.append(source.body)
            parts.append("```")
        else:
            parts.append(source.body)
    return "\n\n".join(part for part in parts if part.strip())


def bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
