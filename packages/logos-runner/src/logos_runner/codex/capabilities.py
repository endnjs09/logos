from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CodexCapabilities:
    codex_found: bool
    version: str | None
    auth_mode: str | None
    exec_supported: bool
    output_schema_supported: bool
    output_last_message_supported: bool
    sandbox_supported: bool
    json_events_supported: bool
    resume_supported: bool
    multi_agent_status: str
    inaccessible: bool = False
    raw_errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "codex_found": self.codex_found,
            "version": self.version,
            "auth_mode": self.auth_mode,
            "exec_supported": self.exec_supported,
            "output_schema_supported": self.output_schema_supported,
            "output_last_message_supported": self.output_last_message_supported,
            "sandbox_supported": self.sandbox_supported,
            "json_events_supported": self.json_events_supported,
            "resume_supported": self.resume_supported,
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
        if os.name != "nt" or command[0] != "codex":
            raise
        return _run_codex_via_powershell(command[1:], timeout)


def _run_codex_via_powershell(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    escaped = " ".join(_quote_powershell_arg(arg) for arg in args)
    command = f"codex {escaped}".strip()
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
        result = _run(["codex", "doctor", "--json"], timeout=30)
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


def _feature_status(feature_name: str) -> str:
    try:
        result = _run(["codex", "features", "list"], timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unknown ({exc})"
    if result.returncode != 0:
        return "unknown"
    for line in result.stdout.splitlines():
        if feature_name in line:
            fields = line.split()
            if len(fields) >= 3:
                return f"{fields[-2]} enabled={fields[-1]}"
            return line.strip()
    return "unknown"


def inspect_codex() -> CodexCapabilities:
    errors: list[str] = []
    if shutil.which("codex") is None:
        return CodexCapabilities(
            codex_found=False,
            version=None,
            auth_mode=None,
            exec_supported=False,
            output_schema_supported=False,
            output_last_message_supported=False,
            sandbox_supported=False,
            json_events_supported=False,
            resume_supported=False,
            multi_agent_status="unknown",
            inaccessible=False,
            raw_errors=("codex executable not found",),
        )

    version: str | None = None
    try:
        version_result = _run(["codex", "--version"])
        if version_result.returncode == 0:
            version = version_result.stdout.strip()
        else:
            errors.append((version_result.stderr or version_result.stdout).strip())
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))

    exec_help = ""
    try:
        help_result = _run(["codex", "exec", "--help"])
        exec_help = help_result.stdout + help_result.stderr
        if help_result.returncode != 0:
            errors.append(exec_help.strip())
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
        exec_supported="Usage:" in exec_help and "codex exec" in exec_help,
        output_schema_supported="--output-schema" in exec_help,
        output_last_message_supported="--output-last-message" in exec_help,
        sandbox_supported="--sandbox" in exec_help,
        json_events_supported="--json" in exec_help,
        resume_supported="resume" in exec_help,
        multi_agent_status=_feature_status("multi_agent"),
        inaccessible=inaccessible,
        raw_errors=tuple(error for error in errors if error),
    )
