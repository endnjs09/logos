"""Prompt assembly models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssemblyInput:
    id: str
    path: str
    kind: str
    status: str
    version: str | None
    sha256: str


@dataclass(frozen=True)
class AssemblyBundle:
    target: str
    profile: str
    mode: str
    inputs: list[AssemblyInput]
    gemini_bootstrap_context: str
    agents_operating_rules: str
    nous_skill_directive: str

    @property
    def outputs(self) -> list[str]:
        return [
            ".gemini/GEMINI.md",
            ".agents/AGENTS.md",
            ".agents/skills/nous/SKILL.md",
        ]


@dataclass(frozen=True)
class AssemblySource:
    path: Path
    relative_path: Path
    asset_id: str
    kind: str
    status: str
    version: str | None
    sha256: str
    body: str
