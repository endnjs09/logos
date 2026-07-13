"""Assemble Logos core assets into host instruction sections."""

from __future__ import annotations

from logos_core.assets.scanner import CoreAssetScan
from logos_core.prompt_assembly.formatting import bullet_list, source_section
from logos_core.prompt_assembly.model import AssemblyBundle, AssemblyInput, AssemblySource
from logos_core.prompt_assembly.selection import select_prompt_assembly_sources


def assemble_prompt_bundle(
    root,
    scan: CoreAssetScan,
    *,
    target: str = "gemini-cli",
    profile: str = "gemini",
    mode: str = "nous",
) -> AssemblyBundle:
    sources = select_prompt_assembly_sources(root, scan)
    prompt_sources = [source for source in sources if source.kind == "template"]
    rule_sources = [source for source in sources if source.kind == "rule"]
    workflow_sources = [source for source in sources if source.kind == "workflow"]
    profile_sources = [source for source in sources if source.kind == "profile"]

    return AssemblyBundle(
        target=target,
        profile=profile,
        mode=mode,
        inputs=[to_input(source) for source in sources],
        gemini_bootstrap_context=build_gemini_bootstrap(prompt_sources, profile_sources),
        agents_operating_rules=build_agents_rules(rule_sources),
        nous_skill_directive=build_nous_directive(rule_sources, workflow_sources, profile_sources),
    )


def to_input(source: AssemblySource) -> AssemblyInput:
    return AssemblyInput(
        id=source.asset_id,
        path=source.relative_path.as_posix(),
        kind=source.kind,
        status=source.status,
        version=source.version,
        sha256=source.sha256,
    )


def build_gemini_bootstrap(
    prompt_sources: list[AssemblySource],
    profile_sources: list[AssemblySource],
) -> str:
    sections = [
        "<!-- logos-assembly: gemini-bootstrap -->",
        "## Logos Gemini Bootstrap",
        "When Logos Nous Mode is active, use the assembled Logos instructions below as the project operating context.",
        source_section("Prompt Material", prompt_sources),
    ]
    if profile_sources:
        sections.append(source_section("Gemini Profile", profile_sources))
    return "\n\n".join(sections)


def build_agents_rules(rule_sources: list[AssemblySource]) -> str:
    return "\n\n".join(
        [
            "<!-- logos-assembly: agents-operating-rules -->",
            "## Logos Operating Rules",
            "Apply these rules when Logos Nous Mode is active.",
            source_section("Rules", rule_sources),
        ]
    )


def build_nous_directive(
    rule_sources: list[AssemblySource],
    workflow_sources: list[AssemblySource],
    profile_sources: list[AssemblySource],
) -> str:
    parts = [
        "<!-- logos-assembly: nous-skill-directive -->",
        "## Assembled Nous Directive",
        "Use this directive after Logos Nous Mode has been activated for the project session.",
        "### Required Operating Loop",
        bullet_list(
            [
                "Clarify only when required information is missing.",
                "Inspect the codebase before making non-trivial edits.",
                "Plan the smallest sufficient change.",
                "Implement within the requested scope.",
                "Verify with concrete evidence before final response.",
            ]
        ),
        source_section("Workflow Material", workflow_sources),
        source_section("Rule Material", rule_sources),
    ]
    if profile_sources:
        parts.append(source_section("Target Profile", profile_sources))
    return "\n\n".join(part for part in parts if part.strip())
