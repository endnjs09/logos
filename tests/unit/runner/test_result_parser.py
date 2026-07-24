from __future__ import annotations

from logos_runner.stages.result_parser import parse_result_object


def test_parse_plain_json_object() -> None:
    result = parse_result_object('{"schema_version": 1, "value": "ok"}')

    assert result.error is None
    assert result.data == {"schema_version": 1, "value": "ok"}


def test_parse_fenced_json_object() -> None:
    result = parse_result_object('```json\n{"schema_version": 1}\n```')

    assert result.error is None
    assert result.data == {"schema_version": 1}


def test_parse_embedded_json_object() -> None:
    result = parse_result_object('before\n{"schema_version": 1, "items": []}\nafter')

    assert result.error is None
    assert result.data == {"schema_version": 1, "items": []}


def test_parse_invalid_json() -> None:
    result = parse_result_object("not json")

    assert result.data is None
    assert result.error is not None

