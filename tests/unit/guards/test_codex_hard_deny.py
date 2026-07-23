from logos_core.guards.codex_hard_deny import build_pre_tool_use_deny_output


def test_build_pre_tool_use_deny_output_uses_reported_codex_shape() -> None:
    output = build_pre_tool_use_deny_output("deny this", "extra context")

    assert output == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "deny this",
            "additionalContext": "extra context",
        }
    }


def test_build_pre_tool_use_deny_output_defaults_context_to_reason() -> None:
    output = build_pre_tool_use_deny_output("deny this")

    hook_output = output["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert hook_output["additionalContext"] == "deny this"
