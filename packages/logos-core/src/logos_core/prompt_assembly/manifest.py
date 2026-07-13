"""Prompt assembly manifest generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from logos_core import __version__
from logos_core.prompt_assembly.model import AssemblyBundle


def build_prompt_assembly_manifest(bundle: AssemblyBundle) -> dict[str, object]:
    return {
        "schema_version": 1,
        "logos_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": bundle.target,
        "profile": bundle.profile,
        "mode": bundle.mode,
        "input_count": len(bundle.inputs),
        "inputs": [
            {
                "id": item.id,
                "path": item.path,
                "kind": item.kind,
                "status": item.status,
                "version": item.version,
                "sha256": item.sha256,
            }
            for item in bundle.inputs
        ],
        "outputs": bundle.outputs,
        "markers": [
            "logos-assembly: gemini-bootstrap",
            "logos-assembly: agents-operating-rules",
            "logos-assembly: nous-skill-directive",
        ],
    }


def write_prompt_assembly_manifest(root: Path, bundle: AssemblyBundle) -> None:
    path = root / ".logos/generated/prompt-assembly-manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_prompt_assembly_manifest(bundle)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
