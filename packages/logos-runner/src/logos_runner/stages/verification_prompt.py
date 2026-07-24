from __future__ import annotations

import json
from pathlib import Path

from logos_runner.paths import RunnerPaths


def build_verification_prompt(project_root: Path, plan_id: str) -> str:
    paths = RunnerPaths(project_root)
    plan_dir = paths.plans_dir / plan_id
    task_plan = _read_json(plan_dir / "task-plan.json")
    execution = _read_json(plan_dir / "execution-result.json")
    spec = _read_json(plan_dir / "spec.json")

    return "\n".join(
        [
            "# Logos Verification Worker Prompt",
            "",
            "Stage: `verify`",
            "Role: `vf`",
            f"Project root: `{project_root}`",
            f"Plan id: `{plan_id}`",
            f"Runner output target: `.logos/plans/{plan_id}/verification-result.json`",
            "",
            "## Required Input Artifacts",
            "",
            f"- `.logos/plans/{plan_id}/task-plan.json`",
            f"- `.logos/plans/{plan_id}/spec.json`",
            f"- `.logos/plans/{plan_id}/context-handoff.json`",
            f"- `.logos/plans/{plan_id}/execution-result.json`",
            "",
            "## Verification Boundary",
            "",
            "- Verify only the completed implementation.",
            "- Do not modify files.",
            "- Compare implementation against `task-plan.json`, `spec.json`, and `execution-result.json`.",
            "- Check success criteria, verification plan, target file scope, excluded scope, and deviations.",
            "- Run tests only when safe and relevant in read-only mode.",
            "- If tests cannot run, inspect diffs or record why checks were skipped.",
            "- Do not introduce new requirements.",
            "- Do not expand implementation scope.",
            "",
            "## Comparison Summary",
            "",
            f"- Goal: `{task_plan.get('goal', '')}`",
            "- Target files:",
            _format_list(task_plan.get("target_files")),
            "- Verification plan:",
            _format_list(task_plan.get("verification_plan")),
            "- Excluded scope:",
            _format_list(task_plan.get("excluded_scope")),
            "- Modified files from execution:",
            _format_list(execution.get("modified_files")),
            "- Deviations from plan:",
            _format_list(execution.get("deviations_from_plan")),
            "- Spec type:",
            f"  - `{spec.get('spec_type', '')}`",
            "",
            "## Required Final JSON",
            "",
            "Return one JSON object only. Do not wrap it in Markdown fences.",
            "Include these keys:",
            "",
            "- `schema_version`",
            "- `plan_id`",
            "- `passed`",
            "- `checked_files`",
            "- `commands_run`",
            "- `tests_run`",
            "- `success_criteria_status`",
            "- `quality_gate_status`",
            "- `modified_files_review`",
            "- `remaining_risk`",
            "- `findings`",
            "- `next_step`",
            "",
            "Use `next_step: complete` only when verification passes.",
            "Use `execute` for implementation rework, `plan` for plan revision, or `clarification` for user input.",
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

