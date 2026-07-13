"""Markdown formatting helpers for assembled instructions."""

from __future__ import annotations

import re
from collections.abc import Iterable

from logos_core.prompt_assembly.model import AssemblySource


def source_section(title: str, sources: Iterable[AssemblySource]) -> str:
    parts = [f"## {title}"]
    for source in sources:
        parts.append(f"### {source_title(source)}")
        if source.path.suffix.lower() in {".yaml", ".yml"}:
            parts.append("```yaml")
            parts.append(source.body)
            parts.append("```")
        else:
            parts.append(normalize_markdown_body(source.body))
    return "\n\n".join(part for part in parts if part.strip())


def bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def source_title(source: AssemblySource) -> str:
    return source.relative_path.stem.replace("-", " ").title()


def normalize_markdown_body(body: str) -> str:
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)

    if lines and re.match(r"^#\s+", lines[0]):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)

    return "\n".join(demote_heading(line) for line in lines).strip()


def demote_heading(line: str) -> str:
    match = re.match(r"^(#{1,4})(\s+.+)$", line)
    if not match:
        return line
    return f"##{match.group(1)}{match.group(2)}"
