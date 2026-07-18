"""Logos CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from logos_installer.doctor import doctor_codex, doctor_gemini
from logos_installer.install import install_codex, install_gemini
from logos_installer.models import InstallError
from logos_installer.session import read_session_state, set_nous_mode
from logos_installer.uninstall import uninstall_gemini


TARGETS = ["gemini-cli", "codex-cli"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="logos")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument(
        "--source-root",
        default=None,
        help="Logos source root containing core/ and targets/. Defaults to current directory.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--target", default="gemini-cli", choices=TARGETS)
    install_parser.add_argument("--force", action="store_true")

    uninstall_parser = subparsers.add_parser("uninstall")
    uninstall_parser.add_argument("--target", default="gemini-cli", choices=TARGETS)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--target", default="gemini-cli", choices=TARGETS)

    subparsers.add_parser("status")

    nous_parser = subparsers.add_parser("nous")
    nous_parser.add_argument("state", choices=["status", "on", "off"])

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    source_root = Path(args.source_root).resolve() if args.source_root else Path.cwd().resolve()

    if args.command == "install":
        try:
            result = install_for_target(
                args.target,
                root,
                source_root=source_root,
                force=args.force,
            )
        except InstallError as exc:
            print("Install failed")
            for message in exc.messages:
                print(f"ERR  {message}")
            return 1
        print_result("Install", result.created, result.updated, result.skipped, result.warnings)
        return 0

    if args.command == "uninstall":
        result = uninstall_gemini(root)
        print_uninstall_result(result.updated, result.skipped, result.warnings)
        return 0

    if args.command == "doctor":
        report = doctor_for_target(args.target, root, source_root=source_root)
        print(f"Logos doctor: {args.target}")
        for item in report.ok:
            print(f"OK   {item}")
        for item in report.warnings:
            print(f"WARN {item}")
        for item in report.errors:
            print(f"ERR  {item}")
        print("Result:", "installed with warnings" if report.passed else "failed")
        return 0 if report.passed else 1

    if args.command == "status":
        state = read_session_state(root)
        print_status(state)
        return 0

    if args.command == "nous":
        if args.state == "status":
            state = read_session_state(root)
            print_status(state)
            return 0
        enabled = args.state == "on"
        state = set_nous_mode(root, enabled, source=f"logos nous {args.state}")
        print_status(state)
        return 0

    parser.error("unknown command")
    return 2


def install_for_target(target: str, root: Path, *, source_root: Path, force: bool):
    if target == "codex-cli":
        return install_codex(root, source_root=source_root, force=force)
    return install_gemini(root, source_root=source_root, force=force)


def doctor_for_target(target: str, root: Path, *, source_root: Path):
    if target == "codex-cli":
        return doctor_codex(root, source_root=source_root)
    return doctor_gemini(root, source_root=source_root)


def print_result(
    label: str,
    created: list[Path],
    updated: list[Path],
    skipped: list[Path],
    warnings: list[str],
) -> None:
    print(f"{label} complete")
    for path in created:
        print(f"CREATED {path.as_posix()}")
    for path in updated:
        print(f"UPDATED {path.as_posix()}")
    for path in skipped:
        print(f"SKIPPED {path.as_posix()}")
    for warning in warnings:
        print(f"WARN {warning}")


def print_uninstall_result(removed: list[Path], skipped: list[Path], warnings: list[str]) -> None:
    print("Uninstall complete")
    for path in removed:
        print(f"REMOVED {path.as_posix()}")
    for path in skipped:
        print(f"SKIPPED {path.as_posix()}")
    for warning in warnings:
        print(f"WARN {warning}")


def print_status(state: dict[str, object]) -> None:
    print("Logos status")
    print(f"Nous mode: {'ON' if state.get('nous_mode') else 'OFF'}")
    print(f"Target: {state.get('target', 'gemini-cli')}")
    print(f"Profile: {state.get('profile', 'gemini')}")
    print(f"Activated by: {state.get('activated_by')}")
    print(f"Activated at: {state.get('activated_at')}")
    print(f"Last updated at: {state.get('last_updated_at')}")


if __name__ == "__main__":
    raise SystemExit(main())
