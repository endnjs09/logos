"""Compatibility shim for the packaged Logos CLI."""

from __future__ import annotations

from logos_installer.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
