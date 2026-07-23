from logos_core.guards.dangerous_command import evaluate
from logos_core.guards.events import GuardEvent


def test_git_status_is_allowed() -> None:
    assert decision_for("git status --short") == "allow"


def test_git_add_is_ask() -> None:
    assert decision_for("git add .") == "ask"


def test_git_commit_is_ask() -> None:
    assert decision_for('git commit -m "x"') == "ask"


def test_git_push_is_ask() -> None:
    assert decision_for("git push origin main") == "ask"


def test_git_push_force_is_block() -> None:
    assert decision_for("git push --force origin main") == "block"


def test_git_reset_hard_is_block() -> None:
    assert decision_for("git reset --hard HEAD") == "block"


def test_git_dash_c_reset_hard_is_block() -> None:
    assert decision_for(r"git -C C:\dev\book-service reset --hard HEAD") == "block"


def test_rm_rf_git_is_block() -> None:
    assert decision_for("rm -rf .git") == "block"


def test_npm_install_is_ask() -> None:
    assert decision_for("npm install") == "ask"


def test_npm_test_is_allowed() -> None:
    assert decision_for("npm test") == "allow"


def test_npm_ci_is_ask() -> None:
    assert decision_for("npm ci") == "ask"


def test_uv_pip_install_is_ask() -> None:
    assert decision_for("uv pip install requests") == "ask"


def test_compound_command_detects_destructive_segment() -> None:
    assert decision_for("Get-Content AGENTS.md; rm -rf tmp-logos-rm") == "block"


def test_compound_command_detects_dependency_segment() -> None:
    assert decision_for("git status && npm install") == "ask"


def test_rg_is_allowed() -> None:
    assert decision_for("rg TODO") == "allow"


def decision_for(command: str) -> str:
    event = GuardEvent(
        schema_version=1,
        target="codex-cli",
        hook_event_name="PreToolUse",
        tool_name="Bash",
        cwd="",
        command=command,
        raw_input={"command": command},
    )
    return evaluate(event).decision
