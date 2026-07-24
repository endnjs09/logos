"""Identifiers for Logos work-state records."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import uuid4


def new_run_id(now: datetime | None = None) -> str:
    return _id("run", now)


def new_plan_id(label: str | None = None, now: datetime | None = None) -> str:
    suffix = _slug(label) if label else ""
    base = _id("plan", now)
    return f"{base}-{suffix}" if suffix else base


def _id(prefix: str, now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    stamp = current.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}-{stamp}-{uuid4().hex[:8]}"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:40] or "work"
