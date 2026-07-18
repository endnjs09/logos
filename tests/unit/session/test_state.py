from pathlib import Path

from logos_core.session.state import (
    activate_nous,
    deactivate_nous,
    default_session_state,
    is_nous_active,
    read_session_state,
    validate_session_state_payload,
)


def test_default_session_state_uses_schema_version() -> None:
    state = default_session_state(now="2026-07-16T00:00:00+00:00")

    assert state["schema_version"] == 1
    assert state["nous_mode"] is False
    assert state["target"] == "gemini-cli"
    assert state["profile"] == "gemini"
    assert state["last_updated_at"] == "2026-07-16T00:00:00+00:00"


def test_activate_and_deactivate_nous(tmp_path: Path) -> None:
    activated = activate_nous(tmp_path, activated_by="test")

    assert activated["nous_mode"] is True
    assert activated["activated_by"] == "test"
    assert is_nous_active(tmp_path) is True

    deactivated = deactivate_nous(tmp_path, activated_by="test-off")

    assert deactivated["nous_mode"] is False
    assert deactivated["activated_by"] == "test-off"
    assert deactivated["activated_at"] is None
    assert read_session_state(tmp_path)["nous_mode"] is False


def test_validate_session_state_payload_rejects_missing_schema() -> None:
    issues = validate_session_state_payload({"nous_mode": False})

    assert [issue.message for issue in issues] == [
        "Session state requires schema_version 1.",
        "Session state requires string target.",
        "Session state requires string profile.",
        "Session state requires ISO datetime last_updated_at.",
    ]
