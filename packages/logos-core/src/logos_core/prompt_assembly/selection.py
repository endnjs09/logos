"""Select the minimal core assets used for prompt assembly."""

from __future__ import annotations

from pathlib import Path

from logos_core.assets.loader import load_core_asset
from logos_core.assets.scanner import CoreAssetScan
from logos_core.prompt_assembly.model import AssemblySource


MINIMAL_ASSEMBLY_PATHS = {
    "prompts/base-system.md",
    "prompts/response-style.md",
    "prompts/target-adapter.md",
    "rules/verification.md",
    "rules/context-handoff.md",
    "rules/user-approval.md",
    "rules/command-execution.md",
    "rules/filesystem.md",
    "rules/git.md",
    "rules/secrets.md",
    "rules/security.md",
}

WORKFLOW_SUPPORT_PATHS = {
    "workflows/planning.yaml",
    "workflows/execution.yaml",
    "workflows/review.yaml",
}


def select_prompt_assembly_sources(
    root: Path,
    scan: CoreAssetScan,
    *,
    profile: str = "gemini",
) -> list[AssemblySource]:
    core_root = root / "core"
    by_path = {asset.relative_path.as_posix(): asset for asset in scan.assets}
    sources: list[AssemblySource] = []

    for relative in sorted(MINIMAL_ASSEMBLY_PATHS):
        asset = by_path.get(relative)
        if asset is None or asset.status != "active" or not asset.has_frontmatter:
            continue
        sources.append(
            AssemblySource(
                path=asset.path,
                relative_path=asset.relative_path,
                asset_id=asset.asset_id,
                kind=asset.kind,
                status=asset.status,
                version=asset.frontmatter.get("version")
                if isinstance(asset.frontmatter.get("version"), str)
                else None,
                sha256=asset.sha256,
                body=read_markdown_body(asset.path),
            )
        )

    structured_paths = {f"profiles/{profile}.yaml", *WORKFLOW_SUPPORT_PATHS}
    for relative in sorted(structured_paths):
        path = core_root / relative
        if not path.exists():
            continue
        asset = load_core_asset(core_root, path)
        sources.append(
            AssemblySource(
                path=asset.path,
                relative_path=asset.relative_path,
                asset_id=asset.asset_id,
                kind=asset.kind,
                status="structured",
                version=None,
                sha256=asset.sha256,
                body=asset.path.read_text(encoding="utf-8").strip(),
            )
        )

    return sources


def read_markdown_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :]).strip()
    return text.strip()
