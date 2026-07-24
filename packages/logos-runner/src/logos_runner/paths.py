from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunnerPaths:
    project_root: Path

    @property
    def logos_dir(self) -> Path:
        return self.project_root / ".logos"

    @property
    def plans_dir(self) -> Path:
        return self.logos_dir / "plans"

    @property
    def runs_dir(self) -> Path:
        return self.logos_dir / "runs"

    @property
    def memory_dir(self) -> Path:
        return self.logos_dir / "memory"

    @property
    def agents_dir(self) -> Path:
        return self.project_root / ".agents"

    @property
    def procedures_dir(self) -> Path:
        return self.agents_dir / "logos" / "procedures"

    @property
    def roles_dir(self) -> Path:
        return self.agents_dir / "logos" / "roles"

    @property
    def nous_skill(self) -> Path:
        return self.agents_dir / "skills" / "nous" / "SKILL.md"

    @property
    def root_agents(self) -> Path:
        return self.project_root / "AGENTS.md"

