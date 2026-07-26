from __future__ import annotations

from pathlib import Path

from logos_runner.paths import RunnerPaths
from logos_runner.state.store import PlanStore
from logos_runner.stages.registry import STAGE_REGISTRY, StageDefinition

ROOT_OFFICIAL_OUTPUTS = {
    "spec.json",
    "task-plan.json",
    "review-lite.json",
    "execution-result.json",
    "verification-result.json",
}


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_stage_prompt(project_root: Path, plan_id: str, stage: StageDefinition) -> str:
    paths = RunnerPaths(project_root)
    store = PlanStore(project_root)
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
    available = [
        (name, _artifact_display_path(plan_id, _artifact_path(store, plan_id, name)))
        for name in previous_artifacts
        if _artifact_path(store, plan_id, name).exists()
    ]
    required_inputs = _required_input_artifacts(stage.name)

    return "\n".join(
        [
            "# Logos Worker Prompt",
            "",
            f"Stage: `{stage.name}`",
            f"Role: `{stage.role}`",
            f"Project root: `{project_root}`",
            f"Plan id: `{plan_id}`",
            f"Runner stage output target: `.logos/plans/{plan_id}/stages/{stage.name.replace('_', '-')}/result.json`",
            f"Official output file: `.logos/plans/{plan_id}/{stage.output_file}`",
            "",
            "## Operating Boundary",
            "",
            "- Perform only this stage.",
            "- Do not write files unless this stage explicitly requires implementation edits.",
            "- Return the stage result in the final response.",
            "- The Logos Runner stores the final response and converts it into plan artifacts.",
            "- Do not directly create or edit official result files such as `spec.json`, `task-plan.json`, `context-handoff.json`, `execution-result.json`, or `verification-result.json`.",
            "- Only Runner `record-stage` may materialize official result JSON files.",
            "- Do not proceed to later stages.",
            "- If required information is missing, record the blocker instead of guessing.",
            "- Read the compact role directive first; do not load role detail references unless the role directive explicitly points to one and this stage needs it.",
            "- Final response must be one JSON object only.",
            "- Do not wrap the JSON in Markdown fences.",
            "- Do not add prose before or after the JSON.",
            "- Include every required field for this stage.",
            "- Persisted Logos artifacts are English-only.",
            "- Translate or summarize user-provided text into English before writing official JSON fields.",
            "- Preserve original user wording only in raw user-answer records, not in official stage result JSON.",
            "- Escape JSON strings correctly; invalid JSON blocks the stage gate.",
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
            "\n".join(f"- `{display}`" for _, display in available) or "- none",
            "",
            "## Required Input Artifacts For This Stage",
            "",
            "\n".join(f"- `{_artifact_display_path(plan_id, _artifact_path(store, plan_id, name))}`" for name in required_inputs)
            or "- `request.json` only",
            "",
            "## Clarification Artifacts",
            "",
            f"- `.logos/plans/{plan_id}/user-answers.jsonl`",
            f"- `.logos/plans/{plan_id}/interview-draft.json`",
            "",
            "Use `user-answers.jsonl` as the only official user clarification log.",
            "Do not create ad hoc clarification files such as `user-clarification.txt`.",
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


def _artifact_path(store: PlanStore, plan_id: str, name: str) -> Path:
    for definition in STAGE_REGISTRY:
        if definition.output_file == name:
            existing = store.existing_stage_result_path(plan_id, definition.name, name)
            if existing.exists():
                return existing
            if name in ROOT_OFFICIAL_OUTPUTS:
                return store.official_result_path(plan_id, name)
            return store.stage_result_path(plan_id, definition.name)
    return store.plan_dir(plan_id) / name


def _artifact_display_path(plan_id: str, path: Path) -> str:
    parts = path.parts
    try:
        index = parts.index(plan_id)
    except ValueError:
        return str(path)
    return str(Path(".logos") / "plans" / Path(*parts[index:]))
