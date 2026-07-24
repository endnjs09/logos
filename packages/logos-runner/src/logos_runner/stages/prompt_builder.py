from __future__ import annotations

from pathlib import Path

from logos_runner.paths import RunnerPaths
from logos_runner.stages.registry import StageDefinition


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_stage_prompt(project_root: Path, plan_id: str, stage: StageDefinition) -> str:
    paths = RunnerPaths(project_root)
    plan_dir = paths.plans_dir / plan_id
    request = _read_optional(plan_dir / "request.json")
    procedure = _read_optional(paths.procedures_dir / stage.procedure)
    role = _read_optional(paths.roles_dir / f"{stage.role}.md")

    previous_artifacts = [
        "scan-result.json",
        "intake-result.json",
        "interview-draft.json",
        "spec.json",
        "task-plan.json",
        "context-handoff.json",
        "review-lite.json",
    ]
    available = [name for name in previous_artifacts if (plan_dir / name).exists()]
    required_inputs = _required_input_artifacts(stage.name)

    return "\n".join(
        [
            "# Logos Worker Prompt",
            "",
            f"Stage: `{stage.name}`",
            f"Role: `{stage.role}`",
            f"Project root: `{project_root}`",
            f"Plan id: `{plan_id}`",
            f"Runner output target: `.logos/plans/{plan_id}/{stage.output_file}`",
            "",
            "## Operating Boundary",
            "",
            "- Perform only this stage.",
            "- Do not write files unless this stage explicitly requires implementation edits.",
            "- Return the stage result in the final response.",
            "- The Logos Runner stores the final response and converts it into plan artifacts.",
            "- Do not proceed to later stages.",
            "- If required information is missing, record the blocker instead of guessing.",
            "- Final response must be one JSON object only.",
            "- Do not wrap the JSON in Markdown fences.",
            "- Do not add prose before or after the JSON.",
            "- Include every required field for this stage.",
            "",
            "## Required JSON Fields",
            "",
            "\n".join(f"- `{key}`" for key in stage.required_keys),
            "",
            "## Schema Reference",
            "",
            f"- `{stage.schema_file}`" if stage.schema_file else "- no schema file registered yet",
            "",
            "## User Request",
            "",
            "```json",
            request.strip(),
            "```",
            "",
            "## Available Previous Artifacts",
            "",
            "\n".join(f"- `.logos/plans/{plan_id}/{name}`" for name in available) or "- none",
            "",
            "## Required Input Artifacts For This Stage",
            "",
            "\n".join(f"- `.logos/plans/{plan_id}/{name}`" for name in required_inputs)
            or "- `request.json` only",
            "",
            "## Clarification Artifacts",
            "",
            f"- `.logos/plans/{plan_id}/user-answers.jsonl`",
            f"- `.logos/plans/{plan_id}/interview-draft.json`",
            "",
            "If user answers exist, apply them before asking more questions.",
            "Do not ask the same answered question again.",
            "Use `interview-draft.json` as the current clarified requirement state when present.",
            "",
            "## Role Directive",
            "",
            role.strip() or "(role directive not installed)",
            "",
            "## Procedure",
            "",
            procedure.strip() or "(procedure directive not installed)",
            "",
        ]
    )


def _required_input_artifacts(stage_name: str) -> tuple[str, ...]:
    if stage_name == "scan":
        return ("request.json",)
    if stage_name == "intake":
        return ("request.json", "scan-result.json")
    if stage_name == "spec":
        return ("request.json", "scan-result.json", "intake-result.json")
    if stage_name == "plan":
        return ("request.json", "scan-result.json", "intake-result.json", "spec.json")
    if stage_name == "review_lite":
        return ("request.json", "spec.json", "task-plan.json")
    if stage_name == "execute":
        return ("task-plan.json", "context-handoff.json")
    if stage_name == "verify":
        return ("task-plan.json", "execution-result.json")
    return ("request.json",)
