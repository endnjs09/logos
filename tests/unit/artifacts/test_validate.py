from pathlib import Path

from logos_core.assets.validate import validate_paths


def write_asset(path: Path, frontmatter: str) -> Path:
    path.write_text(f"---\n{frontmatter}---\n\n# Test\n", encoding="utf-8")
    return path


def messages_for(path: Path) -> list[str]:
    return [issue.message for issue in validate_paths([path])]


def test_rejects_missing_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "asset.md"
    path.write_text("# No frontmatter\n", encoding="utf-8")

    assert messages_for(path) == ["missing YAML frontmatter"]


def test_rejects_high_risk_record_only_guard(tmp_path: Path) -> None:
    path = write_asset(
        tmp_path / "guard.md",
        """
id: logos.guard.secret-scan
kind: guard
name: secret-scan
description: Detect secrets in diffs.
status: active
version: 0.1.0
enforcement: hard
enforcement_status: implemented
decision: record_only
risk_level: high
severity: 3
""",
    )

    assert "high-risk or severity 3 guards cannot be record_only" in messages_for(path)


def test_rejects_unknown_dependency(tmp_path: Path) -> None:
    path = write_asset(
        tmp_path / "role.md",
        """
id: logos.role.planner
kind: role
name: planner
description: Plan work.
status: active
version: 0.1.0
depends_on:
  - logos.workflow.missing
""",
    )

    assert "unknown depends_on id: logos.workflow.missing" in messages_for(path)


def test_rejects_circular_dependency(tmp_path: Path) -> None:
    first = write_asset(
        tmp_path / "first.md",
        """
id: logos.role.first
kind: role
name: first
description: First role.
status: active
version: 0.1.0
depends_on:
  - logos.role.second
""",
    )
    second = write_asset(
        tmp_path / "second.md",
        """
id: logos.role.second
kind: role
name: second
description: Second role.
status: active
version: 0.1.0
depends_on:
  - logos.role.first
""",
    )

    messages = [issue.message for issue in validate_paths([first, second])]
    assert any(message.startswith("circular depends_on graph:") for message in messages)
