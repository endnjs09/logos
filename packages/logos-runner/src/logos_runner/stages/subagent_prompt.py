from __future__ import annotations

from pathlib import Path

from logos_runner.stages.registry import StageDefinition


def build_subagent_assignment(
    *,
    project_root: Path,
    plan_id: str,
    stage: StageDefinition,
    prompt_path: Path,
) -> str:
    raw_output_path = prompt_path.parent / "raw.md"
    result_path = prompt_path.parent / "result.json"
    return "\n".join(
        [
            f"Logos native subagent assignment for stage `{stage.name}`.",
            "",
            f"- Project root: `{project_root}`",
            f"- Plan ID: `{plan_id}`",
            f"- Role: `{stage.role}`",
            f"- Sandbox expectation: `{stage.sandbox}`",
            f"- Stage prompt: `{prompt_path}`",
            f"- Raw result path: `{raw_output_path}`",
            f"- Stage JSON result path: `{result_path}`",
            f"- Official output file: `{stage.output_file}`",
            "",
            "Instructions:",
            "1. Read the stage prompt completely.",
            "2. Work only within the stage role and sandbox expectation.",
            "3. Return one JSON object that satisfies the stage prompt contract.",
            "4. Do not call `codex exec` or start another Codex process.",
            "5. Write persisted Logos artifact content in English.",
            "6. Do not write official `.logos/plans/<plan_id>/*-result.json`, `spec.json`, `task-plan.json`, `context-handoff.json`, `execution-result.json`, or `verification-result.json` files directly.",
            "7. The parent Codex session will record your final JSON with `logos-runner record-stage`.",
            "8. If the parent is waiting, keep working until the JSON result is ready; do not send partial progress unless blocked.",
        ]
    )
