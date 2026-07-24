from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from logos_runner.errors import LogosRunnerError
from logos_runner.stages.registry import StageDefinition


@dataclass(frozen=True)
class WorkerResult:
    stage: str
    return_code: int
    command: tuple[str, ...]
    raw_output_path: Path
    stdout_path: Path
    stderr_path: Path
    metadata_path: Path


def run_codex_worker(
    *,
    project_root: Path,
    plan_dir: Path,
    stage: StageDefinition,
    plan_id: str,
    prompt_path: Path,
    timeout_seconds: int | None = None,
    dry_run: bool = False,
    simulate_intake_missing: bool = False,
) -> WorkerResult:
    if not prompt_path.exists():
        raise LogosRunnerError(f"stage prompt does not exist: {prompt_path}")

    raw_output_path = plan_dir / f"{stage.name}-raw.md"
    stdout_path = plan_dir / f"{stage.name}-stdout.jsonl"
    stderr_path = plan_dir / f"{stage.name}-stderr.txt"
    metadata_path = plan_dir / f"{stage.name}-worker.json"

    command = (
        "codex",
        "exec",
        "--cd",
        str(project_root),
        "--sandbox",
        stage.sandbox,
        "--output-last-message",
        str(raw_output_path),
        "-",
    )

    started_at = datetime.now(UTC).isoformat()
    if dry_run:
        raw_output_path.write_text(
            _dry_run_stage_json(
                stage,
                plan_id=plan_id,
                simulate_intake_missing=simulate_intake_missing,
            ),
            encoding="utf-8",
        )
        _write_worker_metadata(
            metadata_path,
            stage=stage,
            command=command,
            started_at=started_at,
            finished_at=started_at,
            return_code=0,
            dry_run=True,
        )
        return WorkerResult(
            stage=stage.name,
            return_code=0,
            command=command,
            raw_output_path=raw_output_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            metadata_path=metadata_path,
        )

    completed = _run_command(command, timeout_seconds, prompt_path)
    finished_at = datetime.now(UTC).isoformat()
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    _write_worker_metadata(
        metadata_path,
        stage=stage,
        command=command,
        started_at=started_at,
        finished_at=finished_at,
        return_code=completed.returncode,
        dry_run=False,
    )

    return WorkerResult(
        stage=stage.name,
        return_code=completed.returncode,
        command=command,
        raw_output_path=raw_output_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        metadata_path=metadata_path,
    )


def _dry_run_stage_json(
    stage: StageDefinition, *, plan_id: str, simulate_intake_missing: bool
) -> str:
    data: dict[str, object]
    if stage.name == "scan":
        data = {
            "schema_version": 1,
            "exploration_summary": "dry-run scan result",
            "snapshot_used": False,
            "snapshot_sources": [],
            "files_read": [],
            "feature_scan": [],
            "code_evidence": [],
            "project_intent": [],
            "hash_diff": [],
            "likely_target_files": [],
            "read_only_context": [],
            "existing_patterns": [],
            "constraints_discovered": [],
            "question_candidates": [],
            "blocking_unknowns": [],
            "interview_draft_update": {
                "known_facts": [],
                "confirmed_decisions": [],
                "open_questions": [],
                "excluded_scope": [],
            },
            "complexity_reassessment": {
                "previous_complexity": "middle",
                "recommended_complexity": "middle",
                "basis": ["dry-run"],
            },
            "next_step": "intake",
        }
    elif stage.name == "intake" and simulate_intake_missing:
        data = {
            "schema_version": 1,
            "intake_summary": "dry-run intake requires user clarification",
            "essential_information_status": "missing",
            "complexity": "middle",
            "complexity_basis": ["dry-run"],
            "blocking_unknowns": ["게시판 기능 범위가 실행 전 확정되지 않았습니다."],
            "questions": [
                "게시판 범위에 CRUD, 목록, 상세, 검색, 페이징을 포함하나요?",
                "댓글, 파일 첨부, 관리자 기능은 이번 범위에서 제외하나요?",
            ],
            "known_constraints": [],
            "assumptions_allowed": [],
            "risk_notes": [],
            "interview_draft_update": {
                "raw_request": "dry-run",
                "known_facts": [],
                "confirmed_decisions": [],
                "open_questions": [
                    "게시판 범위 확정이 필요합니다.",
                ],
                "excluded_scope": [],
            },
            "next_step": "ask_user",
        }
    elif stage.name == "intake":
        data = {
            "schema_version": 1,
            "intake_summary": "dry-run intake result",
            "essential_information_status": "sufficient",
            "complexity": "middle",
            "complexity_basis": ["dry-run"],
            "blocking_unknowns": [],
            "questions": [],
            "known_constraints": [],
            "assumptions_allowed": [],
            "risk_notes": [],
            "interview_draft_update": {
                "raw_request": "dry-run",
                "known_facts": [],
                "confirmed_decisions": [],
                "open_questions": [],
                "excluded_scope": [],
            },
            "next_step": "spec",
        }
    elif stage.name == "spec":
        data = {
            "schema_version": 1,
            "complexity": "middle",
            "spec_type": "mini_spec",
            "source_refs": ["dry-run"],
            "one_line_plan": "",
            "mini_spec": {
                "goal": "dry-run goal",
                "success_criteria": ["dry-run success"],
                "key_edge_cases": [],
                "excluded_scope": ["dry-run excluded scope"],
            },
            "structured_spec": {
                "user_story": "",
                "confirmed_requirements": [],
                "success_criteria": [],
                "quality_gates": [],
                "constraints": [],
                "edge_cases": [],
                "excluded_scope": [],
                "open_questions": [],
            },
            "blocking_open_questions": [],
            "interview_draft_update": {
                "confirmed_decisions": [],
                "open_questions": [],
                "excluded_scope": [],
            },
            "next_step": "task_plan",
        }
    elif stage.name == "plan":
        data = {
            "schema_version": 1,
            "plan_id": plan_id,
            "source_spec": "dry-run",
            "complexity": "middle",
            "goal": "dry-run goal",
            "target_files": [],
            "role_routing": [{"role_code": "exe", "reason": "dry-run"}],
            "steps": [
                {
                    "id": "dry-run-step",
                    "role_code": "exe",
                    "description": "dry-run step",
                    "target_files": [],
                }
            ],
            "verification_plan": ["dry-run verification"],
            "risk_notes": [],
            "rollback_criteria": ["dry-run rollback"],
            "excluded_scope": ["dry-run excluded scope"],
            "blocking_open_questions": [],
            "context_handoff": {
                "schema_version": 1,
                "apply": False,
                "handoff_to": [],
                "reason": "dry-run",
                "required_fields": [],
                "payload": {},
                "missing_required_fields": [],
            },
            "review_lite": {"passed": True, "findings": []},
            "next_step": "executor",
        }
    elif stage.name == "execute":
        data = {
            "schema_version": 1,
            "plan_id": plan_id,
            "status": "completed",
            "implemented_steps": ["dry-run execution step"],
            "modified_files": [],
            "commands_run": [],
            "tests_run": [],
            "verification_notes": ["dry-run execution completed without file changes"],
            "deviations_from_plan": [],
            "blocked_reason": "",
            "next_step": "verify",
        }
    elif stage.name == "verify":
        data = {
            "schema_version": 1,
            "plan_id": plan_id,
            "passed": True,
            "checked_files": [],
            "commands_run": [],
            "tests_run": [],
            "success_criteria_status": [
                {
                    "criterion": "dry-run success criteria",
                    "status": "passed",
                    "evidence": "dry-run verification",
                }
            ],
            "quality_gate_status": [
                {
                    "gate": "dry-run quality gate",
                    "status": "passed",
                    "evidence": "dry-run verification",
                }
            ],
            "modified_files_review": [],
            "remaining_risk": [],
            "findings": [],
            "next_step": "complete",
        }
    else:
        data = {
            "schema_version": 1,
            "passed": True,
            "findings": [],
            "next_step": "executor",
        }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _run_command(
    command: tuple[str, ...], timeout_seconds: int | None, prompt_path: Path
) -> subprocess.CompletedProcess[str]:
    prompt = prompt_path.read_text(encoding="utf-8")
    try:
        return subprocess.run(
            list(command),
            input=prompt,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except PermissionError:
        if os.name != "nt":
            raise
        return subprocess.run(
            _powershell_command(command, prompt_path),
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )


def _powershell_command(command: tuple[str, ...], prompt_path: Path) -> list[str]:
    encoded = " ".join(_quote_powershell_invocation_arg(arg) for arg in command)
    prompt = _quote_powershell_string(str(prompt_path))
    script = (
        "$OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
        "[Console]::OutputEncoding = $OutputEncoding; "
        f"Get-Content -Raw -Encoding UTF8 -LiteralPath {prompt} | & {encoded}"
    )
    return ["powershell.exe", "-NoProfile", "-Command", script]


def _quote_powershell_invocation_arg(value: str) -> str:
    if value.replace("-", "").replace("_", "").replace(".", "").isalnum():
        return value
    return _quote_powershell_string(value)


def _quote_powershell_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _write_worker_metadata(
    path: Path,
    *,
    stage: StageDefinition,
    command: tuple[str, ...],
    started_at: str,
    finished_at: str,
    return_code: int,
    dry_run: bool,
) -> None:
    data: dict[str, object] = {
        "schema_version": 1,
        "stage": stage.name,
        "role": stage.role,
        "sandbox": stage.sandbox,
        "command": list(command),
        "started_at": started_at,
        "finished_at": finished_at,
        "return_code": return_code,
        "dry_run": dry_run,
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
