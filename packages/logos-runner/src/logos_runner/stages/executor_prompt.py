from __future__ import annotations

import json
from pathlib import Path

from logos_runner.paths import RunnerPaths


def build_executor_prompt(project_root: Path, plan_id: str) -> str:
    paths = RunnerPaths(project_root)
    plan_dir = paths.plans_dir / plan_id
    task_plan = _read_json(plan_dir / "task-plan.json")
    target_files = task_plan.get("target_files", [])
    steps = task_plan.get("steps", [])
    verification_plan = task_plan.get("verification_plan", [])
    excluded_scope = task_plan.get("excluded_scope", [])
    role_routing = task_plan.get("role_routing", [])

    return "\n".join(
        [
            "# Logos Executor Worker Prompt",
            "",
            "Stage: `execute`",
            "Role: `exe`",
            f"Project root: `{project_root}`",
            f"Plan id: `{plan_id}`",
            f"Runner output target: `.logos/plans/{plan_id}/execution-result.json`",
            "",
            "## Required Input Artifacts",
            "",
            f"- `.logos/plans/{plan_id}/task-plan.json`",
            f"- `.logos/plans/{plan_id}/context-handoff.json`",
            f"- `.logos/plans/{plan_id}/interview-draft.json`",
            f"- `.logos/plans/{plan_id}/spec.json`",
            "",
            "## Execution Boundary",
            "",
            "- Execute only the approved task plan.",
            "- Treat `task-plan.json` as the highest-priority execution contract.",
            "- Use `context-handoff.json` as the compact handoff for implementation.",
            "- Do not expand scope.",
            "- Do not modify files outside target files unless compilation makes it necessary.",
            "- If a file outside target files must be changed, record it in `deviations_from_plan`.",
            "- If target files are empty or unsafe to infer, return `status: blocked`.",
            "- Do not invent secrets, credentials, tokens, URLs, API keys, or production values.",
            "- Use placeholder names for missing external values and explain them in verification notes.",
            "- Preserve existing project style and patterns.",
            "",
            "## Task Plan Summary",
            "",
            f"- Goal: `{task_plan.get('goal', '')}`",
            "- Target files:",
            _format_list(target_files),
            "- Role routing:",
            _format_json_lines(role_routing),
            "- Steps:",
            _format_json_lines(steps),
            "- Verification plan:",
            _format_list(verification_plan),
            "- Excluded scope:",
            _format_list(excluded_scope),
            "",
            "## Required Final JSON",
            "",
            "Return one JSON object only. Do not wrap it in Markdown fences.",
            "Include these keys:",
            "",
            "- `schema_version`",
            "- `plan_id`",
            "- `status`",
            "- `implemented_steps`",
            "- `modified_files`",
            "- `commands_run`",
            "- `tests_run`",
            "- `verification_notes`",
            "- `deviations_from_plan`",
            "- `blocked_reason`",
            "- `next_step`",
            "",
            "`next_step` must be `verify` when implementation completed.",
            "Use `plan` or `clarification` only when execution cannot proceed safely.",
            "",
        ]
    )


def _read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _format_list(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "- none"
    return "\n".join(f"  - `{item}`" for item in value)


def _format_json_lines(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "- none"
    lines: list[str] = []
    for item in value:
        lines.append("  - `" + json.dumps(item, ensure_ascii=False) + "`")
    return "\n".join(lines)
