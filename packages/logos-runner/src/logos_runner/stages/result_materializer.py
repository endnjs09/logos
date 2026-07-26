from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from logos_runner.stages.registry import StageDefinition
from logos_runner.stages.result_parser import parse_result_object

ROOT_OFFICIAL_OUTPUTS = {
    "spec.json",
    "task-plan.json",
    "review-lite.json",
    "execution-result.json",
    "verification-result.json",
}


@dataclass(frozen=True)
class MaterializeResult:
    ok: bool
    result_path: Path
    error_path: Path | None
    error: str | None


def materialize_stage_result(
    *,
    plan_dir: Path,
    stage: StageDefinition,
    raw_output_path: Path,
    stage_result_path: Path,
    official_result_path: Path,
    error_path: Path,
) -> MaterializeResult:
    raw = raw_output_path.read_text(encoding="utf-8")
    parsed = parse_result_object(raw)
    if parsed.data is None:
        _remove_stale_outputs(stage_result_path, official_result_path, plan_dir, stage)
        _write_error(error_path, stage, raw_output_path, parsed.error or "parse failed")
        return MaterializeResult(ok=False, result_path=stage_result_path, error_path=error_path, error=parsed.error)

    validation_error = _validate_required_keys(parsed.data, stage)
    if validation_error:
        _remove_stale_outputs(stage_result_path, official_result_path, plan_dir, stage)
        _write_error(error_path, stage, raw_output_path, validation_error)
        return MaterializeResult(
            ok=False,
            result_path=stage_result_path,
            error_path=error_path,
            error=validation_error,
        )

    stage_result_path.parent.mkdir(parents=True, exist_ok=True)
    stage_result_path.write_text(
        json.dumps(parsed.data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if stage.output_file in ROOT_OFFICIAL_OUTPUTS:
        official_result_path.write_text(
            json.dumps(parsed.data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if stage.name == "plan":
        _write_context_handoff(plan_dir, parsed.data)
    if error_path.exists():
        error_path.unlink()
    return MaterializeResult(ok=True, result_path=stage_result_path, error_path=None, error=None)


def _remove_stale_outputs(
    stage_result_path: Path, official_result_path: Path, plan_dir: Path, stage: StageDefinition
) -> None:
    for path in (stage_result_path, official_result_path):
        if path.exists():
            path.unlink()
    if stage.name == "plan":
        context_handoff = plan_dir / "context-handoff.json"
        if context_handoff.exists():
            context_handoff.unlink()


def _validate_required_keys(data: dict[str, object], stage: StageDefinition) -> str | None:
    missing = [key for key in stage.required_keys if key not in data]
    if missing:
        return "missing required keys: " + ", ".join(missing)

    if "schema_version" in stage.required_keys and data.get("schema_version") != 1:
        return "schema_version must be 1"

    return None


def _write_error(path: Path, stage: StageDefinition, raw_output_path: Path, error: str) -> None:
    data: dict[str, object] = {
        "schema_version": 1,
        "stage": stage.name,
        "raw_output": str(raw_output_path),
        "error": error,
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_context_handoff(plan_dir: Path, data: dict[str, object]) -> None:
    context_handoff = data.get("context_handoff")
    if not isinstance(context_handoff, dict):
        return
    path = plan_dir / "context-handoff.json"
    path.write_text(
        json.dumps(context_handoff, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
