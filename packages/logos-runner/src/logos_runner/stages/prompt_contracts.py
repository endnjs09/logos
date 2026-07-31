from __future__ import annotations

from pathlib import Path

from logos_runner.paths import RunnerPaths


def format_prompt_contracts(
    project_root: Path,
    names: list[str],
) -> str:
    paths = RunnerPaths(project_root)
    blocks: list[str] = []
    for name in names:
        body = read_prompt_contract(paths.prompts_dir / name)
        if body:
            blocks.append(body)
    return "\n\n".join(blocks).strip()


def read_prompt_contract(path: Path) -> str:
    if not path.exists():
        return ""
    return strip_frontmatter(path.read_text(encoding="utf-8")).strip()


def strip_frontmatter(text: str) -> str:
    normalized = text.lstrip("\ufeff")
    lines = normalized.splitlines()
    if not lines or lines[0].strip() != "---":
        return normalized
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :])
    return normalized
