"""Validation for Logos Markdown instruction assets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal environments
    yaml = None  # type: ignore[assignment]


ALLOWED_KINDS = {
    "role",
    "implementation-role",
    "skill",
    "command",
    "rule",
    "guard",
    "workflow",
    "rubric",
    "template",
    "hook",
}

ALLOWED_STATUS = {"draft", "active", "deprecated", "experimental"}
HIGH_RISK_GUARDS = {
    "logos.guard.secret-scan",
    "logos.guard.high-risk-override-block",
    "logos.guard.protected-branch-guard",
    "logos.guard.dangerous-command-denylist",
    "logos.guard.file-write-boundary",
    "logos.guard.working-tree-checkpoint",
}


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str


@dataclass(frozen=True)
class Asset:
    path: Path
    frontmatter: dict[str, Any]

    @property
    def asset_id(self) -> str:
        value = self.frontmatter.get("id")
        return value if isinstance(value, str) else ""


def validate_paths(paths: list[Path], *, default_assembly: bool = False) -> list[ValidationIssue]:
    assets: list[Asset] = []
    issues: list[ValidationIssue] = []

    for path in paths:
        if path.suffix.lower() != ".md":
            continue
        asset, path_issues = load_asset(path)
        issues.extend(path_issues)
        if asset is not None:
            assets.append(asset)

    issues.extend(validate_asset_graph(assets))
    if default_assembly:
        issues.extend(validate_default_assembly(assets))
    return issues


def load_asset(path: Path) -> tuple[Asset | None, list[ValidationIssue]]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, [ValidationIssue(path, "missing YAML frontmatter")]

    end = text.find("\n---", 4)
    if end == -1:
        return None, [ValidationIssue(path, "unterminated YAML frontmatter")]

    raw = text[4:end]
    try:
        frontmatter = parse_frontmatter(raw)
    except ValueError as exc:
        return None, [ValidationIssue(path, f"invalid YAML frontmatter: {exc}")]

    if not isinstance(frontmatter, dict):
        return None, [ValidationIssue(path, "frontmatter must be a mapping")]

    asset = Asset(path=path, frontmatter=frontmatter)
    return asset, validate_frontmatter(asset)


def validate_frontmatter(asset: Asset) -> list[ValidationIssue]:
    fm = asset.frontmatter
    issues: list[ValidationIssue] = []

    for field in ("id", "kind", "name", "description", "status", "version"):
        if field not in fm:
            issues.append(ValidationIssue(asset.path, f"missing required field: {field}"))

    kind = fm.get("kind")
    if kind is not None and kind not in ALLOWED_KINDS:
        issues.append(ValidationIssue(asset.path, f"unknown kind: {kind}"))

    status = fm.get("status")
    if status is not None and status not in ALLOWED_STATUS:
        issues.append(ValidationIssue(asset.path, f"unknown status: {status}"))

    if kind == "guard":
        issues.extend(validate_guard(asset))
    elif kind == "rule":
        if fm.get("enforcement") == "hard":
            issues.append(ValidationIssue(asset.path, "rule assets must not use enforcement: hard"))

    if kind == "hook":
        issues.extend(validate_hook(asset))

    return issues


def validate_guard(asset: Asset) -> list[ValidationIssue]:
    fm = asset.frontmatter
    issues: list[ValidationIssue] = []

    if fm.get("enforcement") != "hard":
        issues.append(ValidationIssue(asset.path, "guard assets must use enforcement: hard"))
    if "enforcement_status" not in fm:
        issues.append(ValidationIssue(asset.path, "guard assets require enforcement_status"))

    decision = fm.get("decision")
    risk_level = fm.get("risk_level")
    severity = fm.get("severity")
    asset_id = asset.asset_id

    if decision == "record_only" and (
        asset_id in HIGH_RISK_GUARDS or risk_level == "high" or severity == 3
    ):
        issues.append(ValidationIssue(asset.path, "high-risk or severity 3 guards cannot be record_only"))

    if risk_level == "high" and severity == 0:
        issues.append(ValidationIssue(asset.path, "high-risk guards cannot use severity 0"))

    if risk_level == "low" and severity == 3 and "rationale" not in fm:
        issues.append(
            ValidationIssue(asset.path, "low-risk severity 3 guards require a rationale")
        )

    return issues


def validate_hook(asset: Asset) -> list[ValidationIssue]:
    fm = asset.frontmatter
    issues: list[ValidationIssue] = []

    guards = fm.get("guards")
    if isinstance(guards, list) and len(guards) > 1 and "guard_resolution" not in fm:
        issues.append(ValidationIssue(asset.path, "hooks with multiple guards require guard_resolution"))

    target_support = fm.get("target_support")
    if isinstance(target_support, dict):
        support_status = target_support.get("status")
        if fm.get("status") == "active" and support_status in {"assumed", "unsupported"}:
            issues.append(
                ValidationIssue(
                    asset.path,
                    f"active hooks cannot use target_support.status: {support_status}",
                )
            )

    return issues


def validate_asset_graph(assets: list[Asset]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_id: dict[str, Asset] = {}

    for asset in assets:
        asset_id = asset.asset_id
        if not asset_id:
            continue
        if asset_id in by_id:
            issues.append(ValidationIssue(asset.path, f"duplicate id: {asset_id}"))
        else:
            by_id[asset_id] = asset

    for asset in assets:
        for dependency in iter_string_list(asset.frontmatter.get("depends_on")):
            if dependency not in by_id:
                issues.append(ValidationIssue(asset.path, f"unknown depends_on id: {dependency}"))

    issues.extend(validate_no_cycles(by_id))
    return issues


def validate_no_cycles(by_id: dict[str, Asset]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(asset_id: str, stack: list[str]) -> None:
        if asset_id in visited:
            return
        if asset_id in visiting:
            cycle = " -> ".join([*stack, asset_id])
            issues.append(ValidationIssue(by_id[asset_id].path, f"circular depends_on graph: {cycle}"))
            return

        visiting.add(asset_id)
        asset = by_id[asset_id]
        for dependency in iter_string_list(asset.frontmatter.get("depends_on")):
            if dependency in by_id:
                visit(dependency, [*stack, asset_id])
        visiting.remove(asset_id)
        visited.add(asset_id)

    for asset_id in by_id:
        visit(asset_id, [])

    return issues


def validate_default_assembly(assets: list[Asset]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for asset in assets:
        if asset.frontmatter.get("status") != "active":
            issues.append(ValidationIssue(asset.path, "default assembly may include only active assets"))
    return issues


def iter_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def parse_frontmatter(raw: str) -> dict[str, Any]:
    if yaml is not None:
        loaded = yaml.safe_load(raw) or {}
        if not isinstance(loaded, dict):
            raise ValueError("frontmatter must be a mapping")
        return loaded

    result: dict[str, Any] = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith(" ") or ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line}")

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value:
            result[key] = parse_scalar(value)
            index += 1
            continue

        block, consumed = parse_block(lines, index + 1)
        result[key] = block
        index = consumed

    return result


def parse_block(lines: list[str], start: int) -> tuple[Any, int]:
    items: list[str] = []
    mapping: dict[str, Any] = {}
    index = start

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if not line.startswith(" "):
            break

        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(parse_scalar(stripped[2:]))
            index += 1
            continue

        if ":" in stripped:
            key, value = stripped.split(":", 1)
            mapping[key.strip()] = parse_scalar(value.strip())
            index += 1
            continue

        raise ValueError(f"unsupported nested frontmatter line: {line}")

    if items and mapping:
        raise ValueError("mixed list and mapping blocks are not supported by fallback parser")
    return (items if items else mapping), index


def parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value
