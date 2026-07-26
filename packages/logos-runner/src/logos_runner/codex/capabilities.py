from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CodexCapabilities:
    codex_found: bool
    version: str | None
    auth_mode: str | None
    multi_agent_status: str
    inaccessible: bool = False
    raw_errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "codex_found": self.codex_found,
            "version": self.version,
            "auth_mode": self.auth_mode,
            "multi_agent_status": self.multi_agent_status,
            "inaccessible": self.inaccessible,
            "raw_errors": list(self.raw_errors),
        }


def _run(command: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except PermissionError:
        if os.name != "nt" or Path(command[0]).name.lower() not in {
            "codex",
            "codex.cmd",
            "codex.exe",
        }:
            raise
        return _run_codex_via_powershell(command[1:], timeout)


def _run_codex_via_powershell(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    escaped = " ".join(_quote_powershell_arg(arg) for arg in args)
    executable = _codex_executable()
    command = f"{_quote_powershell_arg(executable)} {escaped}".strip()
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _quote_powershell_arg(value: str) -> str:
    if value.replace("-", "").replace("_", "").isalnum():
        return value
    return "'" + value.replace("'", "''") + "'"


def _doctor_auth_mode() -> tuple[str | None, str | None]:
    try:
        result = _run([_codex_executable(), "doctor", "--json"], timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    if result.returncode != 0:
        return None, (result.stderr or result.stdout).strip()
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, f"invalid codex doctor JSON: {exc}"

    auth = data.get("auth") if isinstance(data, dict) else None
    if isinstance(auth, dict):
        mode = auth.get("mode") or auth.get("auth_mode")
        if isinstance(mode, str):
            return mode, None
    return None, None


def inspect_codex() -> CodexCapabilities:
    errors: list[str] = []
    codex_executable = _codex_executable()
    if not _codex_exists(codex_executable):
        return CodexCapabilities(
            codex_found=False,
            version=None,
            auth_mode=None,
            multi_agent_status="current-session-required",
            inaccessible=False,
            raw_errors=("codex executable not found",),
        )

    version: str | None = None
    try:
        version_result = _run([codex_executable, "--version"])
        if version_result.returncode == 0:
            version = version_result.stdout.strip()
        else:
            errors.append((version_result.stderr or version_result.stdout).strip())
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))

    auth_mode, auth_error = _doctor_auth_mode()
    if auth_error:
        errors.append(auth_error)

    inaccessible = any(
        "Access is denied" in error or "액세스가 거부" in error for error in errors
    )

    return CodexCapabilities(
        codex_found=True,
        version=version,
        auth_mode=auth_mode,
        multi_agent_status="current-session-required",
        inaccessible=inaccessible,
        raw_errors=tuple(error for error in errors if error),
    )


def _codex_executable() -> str:
    return (
        os.environ.get("LOGOS_CODEX_EXECUTABLE")
        or os.environ.get("CODEX_EXECUTABLE")
        or "codex"
    )


def _codex_exists(executable: str) -> bool:
    path = Path(executable)
    if path.is_absolute() or path.parent != Path("."):
        return path.exists()
    return shutil.which(executable) is not None
