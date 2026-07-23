from logos_core.guards.events import codex_input_to_guard_event


def test_codex_input_to_guard_event_extracts_command_and_cwd() -> None:
    event = codex_input_to_guard_event(
        {
            "tool_name": "Bash",
            "cwd": "C:/dev/project",
            "tool_input": {"command": "git push --force"},
        },
        hook_event_name="PreToolUse",
    )

    assert event.target == "codex-cli"
    assert event.hook_event_name == "PreToolUse"
    assert event.tool_name == "Bash"
    assert event.cwd == "C:/dev/project"
    assert event.command == "git push --force"
    assert event.raw_input["tool_name"] == "Bash"
