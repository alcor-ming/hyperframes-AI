#!/usr/bin/env python3
"""Validate package structure and JSON syntax without third-party dependencies."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "SKILL.md",
    "AGENTS.md",
    "CODEX_TASK.md",
    "DECISIONS.md",
    "WORKFLOW.md",
    "profile-registry.json",
    "docs/animation-plan-contract.md",
    "docs/discussion-protocol.md",
    "docs/template-talking-head.md",
    "docs/template-pure-hyperframes.md",
    "docs/profile-integration.md",
    "docs/image-assets.md",
    "docs/voiceover.md",
    "docs/implementation-contract.md",
    "docs/quiet-qa.md",
    "docs/migration-from-existing-prompts.md",
    "templates/ANIMATION_PLAN.template.md",
    "prompts/CODEX_INTEGRATION_PROMPT.md",
    "prompts/CODEX_VIDEO_PROMPT.md",
]


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")

    for path in sorted(ROOT.rglob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid json: {path.relative_to(ROOT)}: {exc}")

    registry = json.loads((ROOT / "profile-registry.json").read_text(encoding="utf-8"))
    for profile in registry["profiles"]:
        for key in ("profile_path", "tokens_path"):
            if not (ROOT / profile[key]).is_file():
                errors.append(f"missing profile asset: {profile[key]}")
        tokens_path = ROOT / profile["tokens_path"]
        if tokens_path.is_file():
            tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
            if tokens.get("profile_id") != profile["id"]:
                errors.append(f"profile id mismatch: {profile['id']}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"OK: {ROOT.name} ({sum(1 for p in ROOT.rglob('*') if p.is_file())} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
