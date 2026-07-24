from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

from logos_runner.codex.capabilities import inspect_codex
from logos_runner.engine import run_execute_stage, run_planning_sequence, run_stage_once, run_verify_stage
from logos_runner.errors import LogosRunnerError
from logos_runner.state.interview import merge_interview_draft
from logos_runner.state.store import PlanStore
from logos_runner.stages.prompt_builder import build_stage_prompt
from logos_runner.stages.registry import STAGE_REGISTRY, get_stage


def _project_root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd().resolve()


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
    exec_status = "OK" if result.exec_supported else ("WARN" if result.inaccessible else "ERR")
    print(f"exec: {exec_status}")
    print(f"exec --output-schema: {'OK' if result.output_schema_supported else 'WARN'}")
    print(f"exec --sandbox: {'OK' if result.sandbox_supported else 'WARN'}")
    print(f"features multi_agent: {result.multi_agent_status}")

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

    missing = [item for item in required_paths if not item.exists()]
    return (
        1
        if missing
        or runner_errors
        or not result.codex_found
        or (not result.exec_supported and not result.inaccessible)
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
    sequence = runner.get("planning_sequence")
    if sequence != ["scan", "intake", "spec", "plan", "review_lite"]:
        errors.append("runner.planning_sequence is invalid")
    return errors


def cmd_start(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    plan = store.create_plan(args.request)
    print(f"Created Logos plan: {plan.plan_id}")
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
    prompt = build_stage_prompt(root, args.plan_id, stage)
    prompt_path = store.plan_dir(args.plan_id) / f"{stage.name}-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    store.mark_stage_prompted(args.plan_id, stage.name, prompt_path)
    print(f"Prepared {stage.name} prompt:")
    print(prompt_path)
    if args.print:
        print(prompt)
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    root = _project_root(args.root)
    store = PlanStore(root)
    store.mark_stage_completed(args.plan_id, args.stage)
    print(f"Marked stage complete: {args.stage}")
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
        print(f"Worker stage: {result.stage}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        if result.result_path:
            print(f"Result JSON: {result.result_path}")
        return 0 if result.status in {"ready_for_verify", "waiting_user", "redirect"} else 1

    result = run_stage_once(
        project_root=root,
        plan_id=args.plan_id,
        stage=stage,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run,
        rebuild_prompt=args.rebuild_prompt,
    )

    print(f"Worker stage: {result.stage}")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    if result.result_path:
        print(f"Result JSON: {result.result_path}")

    if result.status != "result_ready":
        return 1

    if args.complete:
        store = PlanStore(root)
        store.mark_stage_completed(args.plan_id, stage.name)
        print(f"Marked stage complete: {stage.name}")

    return 0


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
    return 0 if result.status in {"complete", "ready_for_execute", "waiting_user", "redirect"} else 1


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
    print(f"Next: logos-runner continue {args.plan_id}")
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
    return 0 if result.status in {"complete", "ready_for_execute", "waiting_user", "redirect"} else 1


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
        print(f"Result JSON: {result.result_path}")
    return 0 if result.status in {"ready_for_verify", "waiting_user", "redirect"} else 1


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
        print(f"Result JSON: {result.result_path}")
    return 0 if result.status in {"verified", "needs_rework", "needs_plan_revision", "waiting_user"} else 1


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
    next_stage.set_defaults(func=cmd_next)

    complete = sub.add_parser("complete")
    complete.add_argument("plan_id")
    complete.add_argument("stage")
    complete.add_argument("--root")
    complete.set_defaults(func=cmd_complete)

    run_stage = sub.add_parser("run-stage")
    run_stage.add_argument("plan_id")
    run_stage.add_argument("stage")
    run_stage.add_argument("--root")
    run_stage.add_argument("--timeout", type=int)
    run_stage.add_argument("--dry-run", action="store_true")
    run_stage.add_argument("--complete", action="store_true")
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
