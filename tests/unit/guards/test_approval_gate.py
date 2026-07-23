from logos_core.guards.approval_gate import evaluate
from logos_core.guards.events import GuardEvent


def test_danger_full_access_blocks() -> None:
    result = evaluate(event({"sandbox_mode": "danger-full-access"}))

    assert result.decision == "block"


def test_network_access_asks() -> None:
    result = evaluate(event({"request": "network access"}))

    assert result.decision == "ask"


def test_unknown_permission_allows_silence() -> None:
    result = evaluate(event({"request": "unknown"}))

    assert result.decision == "allow"


def event(raw: dict[str, object]) -> GuardEvent:
    return GuardEvent(
        schema_version=1,
        target="codex-cli",
        hook_event_name="PermissionRequest",
        tool_name="",
        cwd="",
        command="",
        raw_input=raw,
    )
