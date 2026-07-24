from pathlib import Path

from logos_installer.doctor import (
    validate_codex_config,
    validate_codex_work_state,
    validate_core_hashes,
    validate_guards_manifest,
    validate_session_state,
    validate_target_provides,
)


def test_validate_core_hashes_reports_changed_missing_and_new(tmp_path: Path) -> None:
    guard_dir = tmp_path / "core" / "guards"
    guard_dir.mkdir(parents=True)
    (guard_dir / "changed.yaml").write_text("new\n", encoding="utf-8")
    (guard_dir / "new.yaml").write_text("new\n", encoding="utf-8")
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_core_hashes(
        tmp_path,
        [
            {"path": "guards/changed.yaml", "sha256": "0" * 64},
            {"path": "guards/missing.yaml", "sha256": "1" * 64},
        ],
        ok,
        warnings,
        errors,
    )

    assert errors == []
    assert "core asset hashes checked" in ok
    assert "Core asset changed since install: guards/changed.yaml" in warnings
    assert "Core asset missing since install: guards/missing.yaml" in warnings
    assert "New core asset not present in install manifest: guards/new.yaml" in warnings


def test_validate_guards_manifest_rejects_count_mismatch() -> None:
    ok: list[str] = []
    errors: list[str] = []

    validate_guards_manifest(
        {
            "schema_version": 1,
            "selection_policy": {
                "default_status": "active",
                "raw_assets_selected": False,
                "target": "gemini-cli",
                "profile": "gemini",
            },
            "guard_count": 2,
            "guards": [],
        },
        ok,
        errors,
    )

    assert "Guards manifest guard_count must equal guards length." in errors


def test_validate_session_state_rejects_legacy_shape(tmp_path: Path) -> None:
    path = tmp_path / ".logos" / "session" / "nous-state.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"nous_mode": false}\n', encoding="utf-8")
    ok: list[str] = []
    errors: list[str] = []

    validate_session_state(tmp_path, ok, errors)

    assert "session state shape" not in ok
    assert "Session state requires schema_version 1." in errors


def test_validate_codex_config_accepts_safe_defaults(tmp_path: Path) -> None:
    write_codex_config(
        tmp_path,
        'approval_policy = "on-request"\n'
        'sandbox_mode = "workspace-write"\n'
        "\n"
        "[sandbox_workspace_write]\n"
        "network_access = false\n",
    )
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_codex_config(tmp_path, ok, warnings, errors)

    assert errors == []
    assert warnings == []
    assert "codex config approval_policy" in ok
    assert "codex config sandbox_mode" in ok
    assert "codex config network_access" in ok


def test_validate_codex_config_rejects_danger_full_access(tmp_path: Path) -> None:
    write_codex_config(
        tmp_path,
        'approval_policy = "on-request"\n'
        'sandbox_mode = "danger-full-access"\n'
        "\n"
        "[sandbox_workspace_write]\n"
        "network_access = false\n",
    )
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_codex_config(tmp_path, ok, warnings, errors)

    assert "Codex sandbox_mode must not be danger-full-access for default Logos target." in errors


def test_validate_codex_config_warns_on_never_approval_and_network(tmp_path: Path) -> None:
    write_codex_config(
        tmp_path,
        'approval_policy = "never"\n'
        'sandbox_mode = "workspace-write"\n'
        "\n"
        "[sandbox_workspace_write]\n"
        "network_access = true\n",
    )
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_codex_config(tmp_path, ok, warnings, errors)

    assert "Codex approval_policy must not be never for default Logos target." in errors
    assert "Codex sandbox_workspace_write.network_access must be false." in errors
    assert warnings == []


def test_validate_codex_config_reports_invalid_toml(tmp_path: Path) -> None:
    write_codex_config(tmp_path, 'approval_policy = "on-request"\nsandbox_mode =\n')
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_codex_config(tmp_path, ok, warnings, errors)

    assert any(error.startswith("Invalid Codex config TOML:") for error in errors)


def test_validate_codex_config_warns_on_missing_keys(tmp_path: Path) -> None:
    write_codex_config(tmp_path, "# empty config\n")
    ok: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    validate_codex_config(tmp_path, ok, warnings, errors)

    assert errors == []
    assert "Codex config is missing approval_policy." in warnings
    assert "Codex config is missing sandbox_mode." in warnings
    assert "Codex config is missing sandbox_workspace_write table." in warnings


def test_validate_target_provides_accepts_codex_paths(tmp_path: Path) -> None:
    write_target_toml(
        tmp_path,
        "[target]\n"
        'name = "codex-cli"\n'
        "\n"
        "[provides]\n"
        'instructions = "AGENTS.md"\n'
        'skills = ".agents/skills"\n'
        'procedures = ".agents/logos/procedures"\n'
        'roles = ".agents/logos/roles"\n'
        'config = ".codex/config.toml"\n'
        'hooks = ".codex/hooks.json"\n',
    )
    ok: list[str] = []
    errors: list[str] = []

    validate_target_provides(tmp_path, "codex-cli", ok, errors)

    assert errors == []
    assert "target provides instructions" in ok
    assert "target provides skills" in ok
    assert "target provides procedures" in ok
    assert "target provides roles" in ok
    assert "target provides codex config" in ok
    assert "target provides hooks" in ok


def test_validate_target_provides_rejects_missing_table(tmp_path: Path) -> None:
    write_target_toml(tmp_path, "[target]\nname = \"codex-cli\"\n")
    ok: list[str] = []
    errors: list[str] = []

    validate_target_provides(tmp_path, "codex-cli", ok, errors)

    assert "Target metadata requires provides table." in errors


def test_validate_target_provides_rejects_wrong_codex_paths(tmp_path: Path) -> None:
    write_target_toml(
        tmp_path,
        "[target]\n"
        'name = "codex-cli"\n'
        "\n"
        "[provides]\n"
        'instructions = ".agents/AGENTS.md"\n'
        'skills = "skills"\n'
        'procedures = ".agents/procedures"\n'
        'roles = ".agents/roles"\n'
        'config = ".codex/settings.json"\n'
        'hooks = ".codex/hooks.yml"\n',
    )
    ok: list[str] = []
    errors: list[str] = []

    validate_target_provides(tmp_path, "codex-cli", ok, errors)

    assert "Target provides.instructions must be AGENTS.md." in errors
    assert "Target provides.skills must be .agents/skills." in errors
    assert "Target provides.procedures must be .agents/logos/procedures." in errors
    assert "Target provides.roles must be .agents/logos/roles." in errors
    assert "Target provides.config must be .codex/config.toml." in errors
    assert "Target provides.hooks must be .codex/hooks.json." in errors


def test_validate_target_provides_reports_invalid_toml(tmp_path: Path) -> None:
    write_target_toml(tmp_path, "[provides]\nconfig =\n")
    ok: list[str] = []
    errors: list[str] = []

    validate_target_provides(tmp_path, "codex-cli", ok, errors)

    assert any(error.startswith("Invalid target TOML:") for error in errors)


def test_validate_codex_work_state_rejects_bad_jsonl(tmp_path: Path) -> None:
    memory = tmp_path / ".logos" / "memory"
    memory.mkdir(parents=True)
    (memory / "active-work.json").write_text(
        '{"schema_version":1,"status":"idle","active_plan_id":null,'
        '"active_run_id":null,"updated_at":"now"}\n',
        encoding="utf-8",
    )
    (memory / "run-index.json").write_text(
        '{"schema_version":1,"runs":[],"updated_at":"now"}\n',
        encoding="utf-8",
    )
    (memory / "open-items.json").write_text(
        '{"schema_version":1,"items":[],"updated_at":"now"}\n',
        encoding="utf-8",
    )
    (memory / "resume-snapshot.md").write_text("# Snapshot\n", encoding="utf-8")
    evidence = tmp_path / ".logos" / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "hook-events.jsonl").write_text("{bad\n", encoding="utf-8")
    (tmp_path / ".logos" / "runs").mkdir(parents=True)

    ok: list[str] = []
    errors: list[str] = []

    validate_codex_work_state(tmp_path, ok, errors)

    assert "active-work shape" in ok
    assert any("invalid JSONL" in error for error in errors)


def write_codex_config(root: Path, content: str) -> None:
    path = root / ".codex/config.toml"
    path.parent.mkdir(parents=True)
    path.write_text(content, encoding="utf-8")


def write_target_toml(root: Path, content: str) -> None:
    path = root / ".logos/target.toml"
    path.parent.mkdir(parents=True)
    path.write_text(content, encoding="utf-8")
