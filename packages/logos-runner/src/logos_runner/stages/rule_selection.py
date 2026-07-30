"""Select compact rule pointers for Runner stage prompts."""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path, PurePosixPath
from typing import Any


def format_relevant_rules(
    project_root: Path,
    *,
    stage_name: str,
    paths: list[str] | None = None,
) -> str:
    rules = select_relevant_rules(project_root, stage_name=stage_name, paths=paths or [])
    if not rules:
        return "- none"
    lines: list[str] = []
    for rule in rules:
        detail = rule.get("detail_reference")
        suffix = f"; details: `{detail}`" if isinstance(detail, str) and detail else ""
        lines.append(f"- `{rule['id']}` ({rule['reason']}{suffix})")
    return "\n".join(lines)


def select_relevant_rules(
    project_root: Path,
    *,
    stage_name: str,
    paths: list[str],
) -> list[dict[str, str]]:
    manifest = _read_rules_manifest(project_root)
    rules = manifest.get("rules")
    if not isinstance(rules, list):
        return []

    selected: list[dict[str, str]] = []
    normalized_paths = [_normalize_path(path) for path in paths if path]
    for item in rules:
        if not isinstance(item, dict) or item.get("selected") is not True:
            continue
        rule_id = item.get("id")
        if not isinstance(rule_id, str):
            continue
        reason = _match_reason(item, stage_name=stage_name, paths=normalized_paths)
        if reason is None:
            continue
        selected.append(
            {
                "id": rule_id,
                "reason": reason,
                "detail_reference": str(
                    item.get("detail_installed_path")
                    or item.get("detail_reference")
                    or ""
                ),
            }
        )
    return selected


def _read_rules_manifest(project_root: Path) -> dict[str, object]:
    path = project_root / ".logos" / "generated" / "rules-manifest.json"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _match_reason(item: dict[str, Any], *, stage_name: str, paths: list[str]) -> str | None:
    if item.get("always_apply") is True:
        return "always_apply"

    stages = item.get("stages")
    if isinstance(stages, list) and stage_name in [stage for stage in stages if isinstance(stage, str)]:
        return f"stage:{stage_name}"

    globs = item.get("globs")
    if isinstance(globs, list):
        for pattern in [glob for glob in globs if isinstance(glob, str) and glob]:
            if any(_matches(path, pattern) for path in paths):
                return f"glob:{pattern}"

    return None


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, _normalize_path(pattern))


def _normalize_path(path: str) -> str:
    return PurePosixPath(path.replace("\\", "/")).as_posix()
