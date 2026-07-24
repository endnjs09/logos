from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from logos_runner.errors import LogosRunnerError
from logos_runner.state.store import PlanStore


@dataclass(frozen=True)
class VerificationGateResult:
    ok: bool
    reason: str | None = None


def check_verification_gate(project_root: Path, plan_id: str) -> VerificationGateResult:
    store = PlanStore(project_root)
    state = store.read_state(plan_id)
    plan_dir = store.plan_dir(plan_id)

    if state.get("status") != "ready_for_verify":
        return VerificationGateResult(False, "plan is not ready for verify")

    for file_name in ("execution-result.json", "task-plan.json", "spec.json"):
        if not (plan_dir / file_name).exists():
            return VerificationGateResult(False, f"{file_name} is missing")

    try:
        execution = store.read_stage_result(plan_id, "execution-result.json")
    except (OSError, ValueError) as exc:
        return VerificationGateResult(False, f"failed to read execution result: {exc}")

    if execution.get("status") != "completed":
        return VerificationGateResult(False, "execution result is not completed")

    if execution.get("next_step") != "verify":
        return VerificationGateResult(False, "execution result next_step is not verify")

    return VerificationGateResult(True)


def require_verification_gate(project_root: Path, plan_id: str) -> None:
    result = check_verification_gate(project_root, plan_id)
    if not result.ok:
        raise LogosRunnerError(result.reason or "verification gate failed")

