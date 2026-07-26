from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

from logos_runner.codex.capabilities import inspect_codex
from logos_runner.engine import (
    apply_stage_gate,
    check_gate_status,
    prepare_stage_prompt,
    record_stage_result,
    run_execute_stage,
    run_planning_sequence,
    run_stage_once,
    run_verify_stage,
)
from logos_runner.errors import LogosRunnerError
from logos_runner.state.interview import merge_interview_draft
from logos_runner.state.store import PlanStore
from logos_runner.stages.registry import STAGE_REGISTRY, get_stage
from logos_runner.stages.subagent_prompt import build_subagent_assignment


def _project_root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd().resolve()


def _print_subagent_assignment(root: Path, plan_id: str, stage_name: str, prompt_path: Path) -> None:
    stage = get_stage(stage_name)
    print("Subagent assignment:")
    print(
        build_subagent_assignment(
            project_root=root,
            plan_id=plan_id,
            stage=stage,
            prompt_path=prompt_path,
        )
    )


def cmd_doctor(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    result = inspect_codex()
    store = PlanStore(root)
    required_paths = store.required_install_paths()

    print(f"Logos Runner doctor: {root}")
    for item in required_paths:
        status = "OK  " if item.exists() else "ERR "
        print(f"{status} {item.relative_to(root)}")

    runner_errors = _validate_runner_target(root)
    for item in runner_errors:
        print(f"ERR  {item}")
    if not runner_errors:
        print("OK   runner target metadata")

    codex_status = "OK" if result.codex_found and not result.inaccessible else "WARN"
    if not result.codex_found:
        codex_status = "ERR"
    print(f"Codex CLI: {codex_status}")
    if result.version:
        print(f"Version: {result.version}")
    if result.auth_mode:
        print(f"Auth: {result.auth_mode}")
    print("nested codex exec: not_used")
    print("native subagents: required in active Codex session")

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

    missing = [item for item in required_paths if not item.exists()]
    return (
        1
        if missing
        or runner_errors
        or not result.codex_found
        else 0
    )


def _validate_runner_target(root: Path) -> list[str]:
    path = root / ".logos" / "target.toml"
    if not path.exists():
        return ["runner target metadata missing .logos/target.toml"]
    try:
        loaded = tomllib.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))
    except tomllib.TOMLDecodeError as exc:
        return [f"invalid target.toml: {exc}"]
    runner = loaded.get("runner") if isinstance(loaded, dict) else None
    if not isinstance(runner, dict):
        return ["target.toml requires [runner] table"]

    errors: list[str] = []
    if runner.get("enabled") is not True:
        errors.append("runner.enabled must be true")
    if runner.get("package") != "logos-runner":
        errors.append("runner.package must be logos-runner")
    if runner.get("execute_stage") != "manual":
        errors.append("runner.execute_stage must be manual")
    if runner.get("verify_stage") != "manual":
        errors.append("runner.verify_stage must be manual")
    if runner.get("worker_execution") != "codex-native-subagent":
        errors.append("runner.worker_execution must be codex-native-subagent")
    if runner.get("nested_codex_exec") is not False:
        errors.append("runner.nested_codex_exec must be false")
    sequence = runner.get("planning_sequence")
    if sequence != ["scan", "intake", "spec", "plan", "review_lite"]:
        errors.append("runner.planning_sequence is invalid")
    provides = loaded.get("provides") if isinstance(loaded, dict) else None
    if not isinstance(provides, dict) or provides.get("runner_bin") != ".logos/bin/logos-runner.cmd":
        errors.append("provides.runner_bin must be .logos/bin/logos-runner.cmd")
    if not (root / ".logos" / "bin" / "logos-runner.ps1").exists():
        errors.append("project-local Runner shim is missing: .logos/bin/logos-runner.ps1")
    if not (root / ".logos" / "bin" / "logos-runner.cmd").exists():
        errors.append("project-local Runner cmd shim is missing: .logos/bin/logos-runner.cmd")
    return errors


def cmd_start(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    plan = store.create_plan(args.request)
    print(f"Created Logos plan: {plan.plan_id}")
    print(f"Created Logos run: {plan.run_id}")
    print(plan.plan_dir)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    plans = store.list_plans()
    print(f"Logos Runner status: {root}")
    if not plans:
        print("No Logos plans found.")
        return 0
    for plan in plans:
        print(f"{plan['plan_id']}  {plan['status']}  {plan['updated_at']}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    stage = store.current_stage(args.plan_id)
    prompt_path = prepare_stage_prompt(
        project_root=root,
        plan_id=args.plan_id,
        stage=stage,
        rebuild_prompt=args.rebuild_prompt,
    )
    print(f"Prepared {stage.name} prompt:")
    print(prompt_path)
    _print_subagent_assignment(root, args.plan_id, stage.name, prompt_path)
    if args.print:
        print(prompt_path.read_text(encoding="utf-8"))
    return 0


def cmd_run_stage(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    stage = get_stage(args.stage)
    if stage.name == "execute":
        result = run_execute_stage(
            project_root=root,
            plan_id=args.plan_id,
            timeout_seconds=args.timeout,
            dry_run=args.dry_run,
        )
        print(f"Stage: {result.stage}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        if result.result_path:
            print(f"Prompt: {result.result_path}")
            _print_subagent_assignment(root, args.plan_id, stage.name, result.result_path)
        return 0 if result.status == "prompt_ready" else 1

    result = run_stage_once(
        project_root=root,
        plan_id=args.plan_id,
        stage=stage,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run,
        rebuild_prompt=args.rebuild_prompt,
    )

    print(f"Stage: {result.stage}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    if result.result_path:
        print(f"Prompt: {result.result_path}")
        _print_subagent_assignment(root, args.plan_id, stage.name, result.result_path)

    return 0 if result.status == "prompt_ready" else 1


def cmd_run(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    result = run_planning_sequence(
        project_root=root,
        plan_id=args.plan_id,
        from_stage=args.from_stage,
        until_stage=args.until_stage,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run,
        simulate_intake_missing=args.simulate_intake_missing,
    )

    print(f"Plan: {result.plan_id}")
    print(f"Status: {result.status}")
    print(f"Completed stages: {', '.join(result.completed_stages) or '(none)'}")
    print(f"Message: {result.message}")
    if result.status == "prompt_ready":
        store = PlanStore(root)
        stage = store.current_stage(args.plan_id)
        prompt_path = store.stage_prompt_path(args.plan_id, stage.name)
        _print_subagent_assignment(root, args.plan_id, stage.name, prompt_path)
    return 0 if result.status == "prompt_ready" else 1


def cmd_record_stage(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    stage = get_stage(args.stage)
    raw_text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    if not raw_text.strip():
        raise LogosRunnerError("stage result text is empty")

    result = record_stage_result(
        project_root=root,
        plan_id=args.plan_id,
        stage=stage,
        raw_text=raw_text,
    )
    print(f"Stage: {result.stage}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    if result.result_path:
        print(f"Result JSON: {result.result_path}")
    if result.status == "result_ready":
        print(f"Next: .\\.logos\\bin\\logos-runner.cmd gate --root . {args.plan_id} {stage.name} --apply")
    return 0 if result.status == "result_ready" else 1


def cmd_gate(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    result = (
        apply_stage_gate(root, args.plan_id, args.stage)
        if args.apply
        else check_gate_status(root, args.plan_id, args.stage)
    )
    print(f"Stage: {result.stage}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    if result.result_path:
        print(f"Path: {result.result_path}")
    if result.status == "next_prompt_ready" and result.result_path:
        next_stage = PlanStore(root).current_stage(args.plan_id)
        _print_subagent_assignment(root, args.plan_id, next_stage.name, result.result_path)
    if result.status == "ready_for_execute":
        print(f"Next: .\\.logos\\bin\\logos-runner.cmd execute --root . {args.plan_id}")
    if result.status == "ready_for_verify":
        print(f"Next: .\\.logos\\bin\\logos-runner.cmd verify --root . {args.plan_id}")
    return 0 if result.status not in {"failed", "gate_blocked"} else 1


def cmd_answer(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    state = store.read_state(args.plan_id)
    if state.get("status") != "waiting_user":
        raise LogosRunnerError("plan is not waiting for user input")

    answer = _read_answer(args)
    if not answer.strip():
        raise LogosRunnerError("answer is empty")

    answers_path = store.append_user_answer(args.plan_id, answer.strip())
    draft_path = merge_interview_draft(root, args.plan_id)
    updated = store.read_state(args.plan_id)
    print(f"Recorded answer: {answers_path}")
    print(f"Interview draft: {draft_path}")
    print(f"Stage: {updated.get('current_stage')}")
    print(f"Next: .\\.logos\\bin\\logos-runner.cmd continue --root . {args.plan_id}")
    return 0


def cmd_continue(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    state = store.read_state(args.plan_id)
    if state.get("status") not in {"answered", "waiting_user", "redirect", "ready"}:
        raise LogosRunnerError(f"plan cannot continue from status: {state.get('status')}")

    merge_interview_draft(root, args.plan_id)
    current_stage = str(state.get("current_stage", "intake"))
    if current_stage == "execute":
        print("Plan is ready for execute.")
        return 0

    result = run_planning_sequence(
        project_root=root,
        plan_id=args.plan_id,
        from_stage=current_stage,
        until_stage=args.until_stage,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run,
        simulate_intake_missing=False,
    )
    print(f"Plan: {result.plan_id}")
    print(f"Status: {result.status}")
    print(f"Completed stages: {', '.join(result.completed_stages) or '(none)'}")
    print(f"Message: {result.message}")
    if result.status == "prompt_ready":
        store = PlanStore(root)
        stage = store.current_stage(args.plan_id)
        prompt_path = store.stage_prompt_path(args.plan_id, stage.name)
        _print_subagent_assignment(root, args.plan_id, stage.name, prompt_path)
    return 0 if result.status == "prompt_ready" else 1


def cmd_execute(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    result = run_execute_stage(
        project_root=root,
        plan_id=args.plan_id,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run,
    )
    print(f"Plan: {args.plan_id}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    if result.result_path:
        print(f"Prompt: {result.result_path}")
        _print_subagent_assignment(root, args.plan_id, "execute", result.result_path)
    return 0 if result.status == "prompt_ready" else 1


def cmd_verify(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    result = run_verify_stage(
        project_root=root,
        plan_id=args.plan_id,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run,
    )
    print(f"Plan: {args.plan_id}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    if result.result_path:
        print(f"Prompt: {result.result_path}")
        _print_subagent_assignment(root, args.plan_id, "verify", result.result_path)
    return 0 if result.status == "prompt_ready" else 1


def _read_answer(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    return args.answer or ""


def cmd_stages(_: argparse.Namespace) -> int:
    for stage in STAGE_REGISTRY:
        print(f"{stage.name}\t{stage.role}\t{stage.sandbox}\t{stage.output_file}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logos-runner")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--root")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    start = sub.add_parser("start")
    start.add_argument("request")
    start.add_argument("--root")
    start.set_defaults(func=cmd_start)

    status = sub.add_parser("status")
    status.add_argument("--root")
    status.set_defaults(func=cmd_status)

    next_stage = sub.add_parser("next")
    next_stage.add_argument("plan_id")
    next_stage.add_argument("--root")
    next_stage.add_argument("--print", action="store_true")
    next_stage.add_argument("--rebuild-prompt", action="store_true")
    next_stage.set_defaults(func=cmd_next)

    run_stage = sub.add_parser("run-stage")
    run_stage.add_argument("plan_id")
    run_stage.add_argument("stage")
    run_stage.add_argument("--root")
    run_stage.add_argument("--timeout", type=int)
    run_stage.add_argument("--dry-run", action="store_true")
    run_stage.add_argument("--rebuild-prompt", action="store_true")
    run_stage.set_defaults(func=cmd_run_stage)

    run = sub.add_parser("run")
    run.add_argument("plan_id")
    run.add_argument("--root")
    run.add_argument("--from-stage", default="scan")
    run.add_argument("--until-stage", default="review_lite")
    run.add_argument("--timeout", type=int)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--simulate-intake-missing", action="store_true")
    run.set_defaults(func=cmd_run)

    record_stage = sub.add_parser("record-stage")
    record_stage.add_argument("plan_id")
    record_stage.add_argument("stage")
    record_stage.add_argument("--root")
    record_stage.add_argument("--file")
    record_stage.set_defaults(func=cmd_record_stage)

    gate = sub.add_parser("gate")
    gate.add_argument("plan_id")
    gate.add_argument("stage")
    gate.add_argument("--root")
    gate.add_argument("--apply", action="store_true")
    gate.set_defaults(func=cmd_gate)

    answer = sub.add_parser("answer")
    answer.add_argument("plan_id")
    answer.add_argument("answer", nargs="?")
    answer.add_argument("--root")
    answer.add_argument("--file")
    answer.set_defaults(func=cmd_answer)

    continue_cmd = sub.add_parser("continue")
    continue_cmd.add_argument("plan_id")
    continue_cmd.add_argument("--root")
    continue_cmd.add_argument("--until-stage", default="review_lite")
    continue_cmd.add_argument("--timeout", type=int)
    continue_cmd.add_argument("--dry-run", action="store_true")
    continue_cmd.set_defaults(func=cmd_continue)

    execute = sub.add_parser("execute")
    execute.add_argument("plan_id")
    execute.add_argument("--root")
    execute.add_argument("--timeout", type=int)
    execute.add_argument("--dry-run", action="store_true")
    execute.set_defaults(func=cmd_execute)

    verify = sub.add_parser("verify")
    verify.add_argument("plan_id")
    verify.add_argument("--root")
    verify.add_argument("--timeout", type=int)
    verify.add_argument("--dry-run", action="store_true")
    verify.set_defaults(func=cmd_verify)

    stages = sub.add_parser("stages")
    stages.set_defaults(func=cmd_stages)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except LogosRunnerError as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
