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
    codex_operating_context: str
    codex_nous_skill: str
    codex_codebase_exploration_skill: str
    codex_implementation_planning_skill: str
    codex_risk_review_skill: str
    codex_verification_skill: str

    @property
    def outputs(self) -> list[str]:
        if self.target == "codex-cli":
            return [
                "AGENTS.md",
                ".agents/skills/nous/SKILL.md",
                ".agents/logos/procedures/intake.md",
                ".agents/logos/procedures/exploration.md",
                ".agents/logos/procedures/spec.md",
                ".agents/logos/procedures/planning.md",
                ".agents/logos/procedures/execution.md",
                ".agents/logos/procedures/verification.md",
                ".agents/logos/procedures/review.md",
                ".agents/logos/procedures/resume.md",
                ".agents/logos/roles/orch.md",
                ".agents/logos/roles/intk.md",
                ".agents/logos/roles/exp.md",
                ".agents/logos/roles/sp.md",
                ".agents/logos/roles/pln.md",
                ".agents/logos/roles/exe.md",
                ".agents/logos/roles/bd.md",
                ".agents/logos/roles/fd.md",
                ".agents/logos/roles/db.md",
                ".agents/logos/roles/sys.md",
                ".agents/logos/roles/test.md",
                ".agents/logos/roles/sec.md",
                ".agents/logos/roles/rv.md",
                ".agents/logos/roles/vf.md",
                ".agents/logos/roles/mem.md",
            ]
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
