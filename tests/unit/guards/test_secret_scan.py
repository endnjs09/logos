from logos_core.guards.events import GuardEvent
from logos_core.guards.secret_scan import evaluate, scan_text


def test_scan_text_detects_secret_like_values() -> None:
    findings = scan_text("GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyzABCDE")

    assert findings
    assert findings[0].kind == "github token"
    assert "..." in findings[0].sample


def test_scan_text_allows_placeholders() -> None:
    assert scan_text("OAUTH_CLIENT_SECRET=YOUR_OAUTH_CLIENT_SECRET") == []
    assert scan_text("REDIS_URL=${REDIS_URL}") == []


def test_evaluate_asks_for_secret_like_values() -> None:
    result = evaluate(event({"content": "api_key = abcdefghijklmnopqrstuvwxyz123456"}))

    assert result.decision == "ask"
    assert result.reason == "secret-like value detected"


def test_evaluate_allows_no_secret_values() -> None:
    result = evaluate(event({"content": "api_key = YOUR_API_KEY"}))

    assert result.decision == "allow"


def event(raw: dict[str, object]) -> GuardEvent:
    return GuardEvent(
        schema_version=1,
        target="codex-cli",
        hook_event_name="PreToolUse",
        tool_name="Write",
        cwd="",
        command="",
        raw_input=raw,
    )
