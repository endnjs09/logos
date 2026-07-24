from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParseResult:
    data: dict[str, object] | None
    error: str | None


def parse_result_object(raw: str) -> ParseResult:
    candidates = _candidate_json_strings(raw)
    errors: list[str] = []

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(data, dict):
            errors.append("top-level JSON value is not an object")
            continue
        return ParseResult(data=data, error=None)

    detail = "; ".join(errors) if errors else "no JSON object candidate found"
    return ParseResult(data=None, error=detail)


def _candidate_json_strings(raw: str) -> list[str]:
    stripped = raw.strip()
    candidates: list[str] = []
    if stripped:
        candidates.append(stripped)

    for match in re.finditer(r"```(?:json)?\s*(.*?)```", raw, flags=re.DOTALL | re.IGNORECASE):
        block = match.group(1).strip()
        if block:
            candidates.append(block)

    extracted = _extract_first_json_object(raw)
    if extracted:
        candidates.append(extracted)

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped


def _extract_first_json_object(raw: str) -> str | None:
    start = raw.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(raw)):
        char = raw[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw[start : index + 1]
    return None

