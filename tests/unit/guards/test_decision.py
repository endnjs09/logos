from logos_core.guards.decision import allow, ask, block, merge_most_restrictive, record_only


def test_merge_most_restrictive_uses_expected_order() -> None:
    result = merge_most_restrictive(
        [
            allow("logos.guard.a"),
            record_only("logos.guard.b", "record"),
            ask("logos.guard.c", "ask"),
            block("logos.guard.d", "block"),
        ]
    )

    assert result.decision == "block"
    assert result.guard_id == "logos.guard.d"


def test_merge_empty_decisions_allows() -> None:
    result = merge_most_restrictive([])

    assert result.decision == "allow"
