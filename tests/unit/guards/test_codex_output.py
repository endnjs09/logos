from logos_core.guards.codex_output import decision_to_codex_output
from logos_core.guards.decision import allow, ask, block, record_only


def test_allow_emits_no_codex_output() -> None:
    assert decision_to_codex_output(allow("logos.guard.test")) == {}


def test_ask_emits_approval_note() -> None:
    output = decision_to_codex_output(ask("logos.guard.test", "dependency change"))

    assert output["systemMessage"].startswith("Logos approval note: dependency change.")
    assert "Codex approval and sandbox policy remain authoritative" in output["systemMessage"]


def test_block_emits_warning_not_hard_block_claim() -> None:
    output = decision_to_codex_output(block("logos.guard.test", "destructive action"))

    assert output["systemMessage"].startswith("Logos guard warning: destructive action.")
    assert "does not claim hard block enforcement" in output["systemMessage"]


def test_record_only_emits_note() -> None:
    output = decision_to_codex_output(record_only("logos.guard.test", "record event"))

    assert output == {"systemMessage": "Logos note: record event"}
