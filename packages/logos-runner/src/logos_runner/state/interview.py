from __future__ import annotations

import json
from pathlib import Path

from logos_runner.state.store import PlanStore


def merge_interview_draft(project_root: Path, plan_id: str) -> Path:
    store = PlanStore(project_root)
    plan_dir = store.plan_dir(plan_id)
    request = store.read_request(plan_id)
    answers = store.read_user_answers(plan_id)

    confirmed_decisions: list[str] = []
    open_questions: list[str] = []
    excluded_scope: list[str] = []
    modes: list[str] = []

    for file_name in ("scan-result.json", "intake-result.json", "spec.json"):
        path = plan_dir / file_name
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

        complexity = data.get("complexity")
        if isinstance(complexity, str):
            modes.append(complexity)
        reassessment = data.get("complexity_reassessment")
        if isinstance(reassessment, dict):
            recommended = reassessment.get("recommended_complexity")
            if isinstance(recommended, str):
                modes.append(recommended)

    for answer in answers:
        text = answer.get("answer")
        stage = answer.get("stage")
        if isinstance(text, str) and text.strip():
            prefix = f"user answer"
            if isinstance(stage, str) and stage:
                prefix = f"user answer during {stage}"
            confirmed_decisions.append(f"{prefix}: {text.strip()}")

    state = store.read_state(plan_id)
    pending = state.get("pending_questions")
    if state.get("status") == "waiting_user":
        _extend_strings(open_questions, pending)

    final_mode = _last_mode(modes)
    draft = {
        "raw_request": str(request.get("user_request", "")),
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


def _last_mode(modes: list[str]) -> str:
    for mode in reversed(modes):
        if mode in {"low", "middle", "high"}:
            return mode
    return "middle"

