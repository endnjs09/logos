from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StageDefinition:
    name: str
    role: str
    procedure: str
    output_file: str
    schema_file: str | None
    required_keys: tuple[str, ...]
    sandbox: str
    reads_project: bool


STAGE_REGISTRY: tuple[StageDefinition, ...] = (
    StageDefinition(
        name="scan",
        role="exp",
        procedure="exploration.md",
        output_file="scan-result.json",
        schema_file="schemas/exploration-result.schema.json",
        required_keys=(
            "schema_version",
            "exploration_summary",
            "files_read",
            "question_candidates",
            "blocking_unknowns",
            "next_step",
        ),
        sandbox="read-only",
        reads_project=True,
    ),
    StageDefinition(
        name="intake",
        role="intk",
        procedure="intake.md",
        output_file="intake-result.json",
        schema_file="schemas/intake-result.schema.json",
        required_keys=(
            "schema_version",
            "intake_summary",
            "essential_information_status",
            "complexity",
            "questions",
            "blocking_unknowns",
            "next_step",
        ),
        sandbox="read-only",
        reads_project=False,
    ),
    StageDefinition(
        name="spec",
        role="sp",
        procedure="spec.md",
        output_file="spec.json",
        schema_file="schemas/spec-result.schema.json",
        required_keys=(
            "schema_version",
            "complexity",
            "spec_type",
            "blocking_open_questions",
            "next_step",
        ),
        sandbox="read-only",
        reads_project=False,
    ),
    StageDefinition(
        name="plan",
        role="pln",
        procedure="planning.md",
        output_file="task-plan.json",
        schema_file="schemas/task-plan-result.schema.json",
        required_keys=(
            "schema_version",
            "plan_id",
            "goal",
            "target_files",
            "steps",
            "verification_plan",
            "context_handoff",
            "next_step",
        ),
        sandbox="read-only",
        reads_project=False,
    ),
    StageDefinition(
        name="review_lite",
        role="rv",
        procedure="review.md",
        output_file="review-lite.json",
        schema_file=None,
        required_keys=("schema_version", "passed", "findings", "next_step"),
        sandbox="read-only",
        reads_project=False,
    ),
    StageDefinition(
        name="execute",
        role="exe",
        procedure="execution.md",
        output_file="execution-result.json",
        schema_file="schemas/execution-result.schema.json",
        required_keys=(
            "schema_version",
            "plan_id",
            "status",
            "implemented_steps",
            "modified_files",
            "commands_run",
            "tests_run",
            "verification_notes",
            "deviations_from_plan",
            "next_step",
        ),
        sandbox="workspace-write",
        reads_project=True,
    ),
    StageDefinition(
        name="verify",
        role="vf",
        procedure="verification.md",
        output_file="verification-result.json",
        schema_file="schemas/verification-result.schema.json",
        required_keys=(
            "schema_version",
            "plan_id",
            "passed",
            "checked_files",
            "commands_run",
            "tests_run",
            "success_criteria_status",
            "quality_gate_status",
            "modified_files_review",
            "remaining_risk",
            "findings",
            "next_step",
        ),
        sandbox="read-only",
        reads_project=True,
    ),
)

PLANNING_SEQUENCE: tuple[str, ...] = ("scan", "intake", "spec", "plan", "review_lite")


def get_stage(name: str) -> StageDefinition:
    for stage in STAGE_REGISTRY:
        if stage.name == name:
            return stage
    raise KeyError(name)
