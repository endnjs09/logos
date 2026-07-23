from pathlib import Path

from logos_core.guards.checkpoint import capture_checkpoint


def test_capture_checkpoint_handles_non_git_directory(tmp_path: Path) -> None:
    checkpoint = capture_checkpoint(tmp_path, "risky operation")

    assert checkpoint.schema_version == 1
    assert checkpoint.cwd == str(tmp_path)
    assert checkpoint.reason == "risky operation"
    assert checkpoint.head is None
    assert checkpoint.branch is None
    assert checkpoint.status_short == ""
    assert checkpoint.dirty is False
