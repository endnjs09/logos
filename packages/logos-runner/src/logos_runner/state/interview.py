from __future__ import annotations

import json
from pathlib import Path

from logos_runner.state.store import PlanStore
from logos_runner.stages.registry import get_stage


def merge_interview_draft(project_root: Path, plan_id: str) -> Path:
    store = PlanStore(project_root)
    plan_dir = store.plan_dir(plan_id)
    request = store.read_request(plan_id)
    answers = store.read_user_answers(plan_id)

    confirmed_decisions: list[str] = []
    open_questions: list[str] = []
    excluded_scope: list[str] = []
    modes: list[str] = []
    latest_intake_sufficient = False
    latest_intake_has_no_questions = False
    latest_spec_has_no_blocking_questions = False
    latest_spec_has_no_open_questions = False

    for file_name in ("scan-result.json", "intake-result.json", "spec.json"):
        stage = _stage_for_output(file_name)
        path = (
            store.existing_stage_result_path(plan_id, stage.name, file_name)
            if stage is not None
            else plan_dir / file_name
        )
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        update = data.get("interview_draft_update")
        if isinstance(update, dict):
            _extend_strings(confirmed_decisions, update.get("confirmed_decisions"))
            _extend_strings(open_questions, update.get("open_questions"))
            _extend_strings(excluded_scope, update.get("excluded_scope"))

        if file_name == "intake-result.json":
            latest_intake_sufficient = _is_intake_sufficient(data)
            latest_intake_has_no_questions = _has_no_intake_questions(data)
        elif file_name == "spec.json":
            latest_spec_has_no_blocking_questions = _has_no_blocking_open_questions(data)
            latest_spec_has_no_open_questions = _has_no_structured_open_questions(data)

        complexity = data.get("complexity")
        if isinstance(complexity, str):
            modes.append(complexity)
        reassessment = data.get("complexity_reassessment")
        if isinstance(reassessment, dict):
            recommended = reassessment.get("recommended_complexity")
            if isinstance(recommended, str):
                modes.append(recommended)

    for answer in answers:
        stage = answer.get("stage")
        if isinstance(stage, str) and stage:
            confirmed_decisions.append(f"User provided clarification during {stage}; see user-answers.jsonl.")
        else:
            confirmed_decisions.append("User provided clarification; see user-answers.jsonl.")

    state = store.read_state(plan_id)
    pending = state.get("pending_questions")
    if state.get("status") == "waiting_user":
        _extend_strings(open_questions, pending)
    elif latest_intake_sufficient or (
        latest_intake_has_no_questions
        and latest_spec_has_no_blocking_questions
        and latest_spec_has_no_open_questions
    ):
        open_questions.clear()

    final_mode = _last_mode(modes)
    draft = {
        "raw_request_ref": "request.json",
        "initial_mode": modes[0] if modes else "middle",
        "final_mode": final_mode,
        "confirmed_decisions": _dedupe(confirmed_decisions),
        "open_questions": _dedupe(open_questions),
        "excluded_scope": _dedupe(excluded_scope),
    }

    path = plan_dir / "interview-draft.json"
    path.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _extend_strings(target: list[str], value: object) -> None:
    if not isinstance(value, list):
        return
    for item in value:
        if isinstance(item, str) and item.strip():
            target.append(item.strip())
        elif isinstance(item, dict):
            question = item.get("question")
            if isinstance(question, str) and question.strip():
                target.append(question.strip())


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _is_intake_sufficient(data: dict[str, object]) -> bool:
    status = data.get("essential_information_status")
    return status == "sufficient" and _has_no_intake_questions(data)


def _has_no_intake_questions(data: dict[str, object]) -> bool:
    questions = data.get("questions")
    required_questions = data.get("required_questions")
    blocking_unknowns = data.get("blocking_unknowns")
    return (
        (not isinstance(questions, list) or len(questions) == 0)
        and (not isinstance(required_questions, list) or len(required_questions) == 0)
        and (not isinstance(blocking_unknowns, list) or len(blocking_unknowns) == 0)
    )


def _has_no_blocking_open_questions(data: dict[str, object]) -> bool:
    questions = data.get("blocking_open_questions")
    return isinstance(questions, list) and len(questions) == 0


def _has_no_structured_open_questions(data: dict[str, object]) -> bool:
    structured = data.get("structured_spec")
    if not isinstance(structured, dict):
        return True
    questions = structured.get("open_questions")
    return isinstance(questions, list) and len(questions) == 0


def _last_mode(modes: list[str]) -> str:
    for mode in reversed(modes):
        if mode in {"low", "middle", "high"}:
            return mode
    return "middle"


def _stage_for_output(file_name: str):
    for stage_name in ("scan", "intake", "spec"):
        stage = get_stage(stage_name)
        if stage.output_file == file_name:
            return stage
    return None
