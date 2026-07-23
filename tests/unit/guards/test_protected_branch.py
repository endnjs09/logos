from logos_core.guards.events import GuardEvent
from logos_core.guards.protected_branch import evaluate, is_protected_branch


def test_protected_branch_patterns() -> None:
    assert is_protected_branch("main")
    assert is_protected_branch("release/2026.07")
    assert not is_protected_branch("feature/login")


def test_protected_branch_read_only_git_allowed() -> None:
    result = evaluate(event("git status --short"), branch="main")

    assert result.decision == "allow"


def test_protected_branch_git_commit_asks() -> None:
    result = evaluate(event('git commit -m "x"'), branch="main")

    assert result.decision == "ask"


def test_protected_branch_force_push_blocks() -> None:
    result = evaluate(event("git push --force origin main"), branch="main")

    assert result.decision == "block"


def test_protected_branch_git_dash_c_reset_blocks() -> None:
    result = evaluate(event(r"git -C C:\dev\book-service reset --hard HEAD"), branch="main")

    assert result.decision == "block"


def test_unknown_branch_git_commit_asks() -> None:
    result = evaluate(event('git commit -m "x"'), branch=None)

    assert result.decision == "ask"


def event(command: str) -> GuardEvent:
    return GuardEvent(
        schema_version=1,
        target="codex-cli",
        hook_event_name="PreToolUse",
        tool_name="Bash",
        cwd="",
        command=command,
        raw_input={"command": command},
    )
