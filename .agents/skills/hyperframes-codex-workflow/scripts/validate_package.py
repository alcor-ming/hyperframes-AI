#!/usr/bin/env python3
"""Validate the thin Skill, Profile registry, and repository Harness."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
REQUIRED_PACKAGE = [
    "README.md",
    "SKILL.md",
    "CHANGELOG.md",
    "VERSION",
    "profile-registry.json",
]
REQUIRED_HARNESS = [
    "AGENTS.md",
    "work",
    ".studio/work.py",
    ".studio/workflow.md",
    ".studio/capabilities.yaml",
    ".studio/spec/creative.md",
    ".studio/spec/hyperframes.md",
    ".studio/spec/privacy.md",
    ".studio/recipes/talking-head.md",
    ".studio/recipes/pure-hyperframes.md",
    ".studio/templates/RESEARCH.template.md",
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_PACKAGE:
        if not (ROOT / relative).is_file():
            errors.append(f"missing package file: {relative}")
    for relative in REQUIRED_HARNESS:
        if not (REPO / relative).is_file():
            errors.append(f"missing harness file: {relative}")

    for path in sorted(ROOT.rglob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid json: {path.relative_to(ROOT)}: {exc}")

    registry_path = ROOT / "profile-registry.json"
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for profile in registry.get("profiles", []):
            for key in ("profile_path", "tokens_path"):
                if not (ROOT / profile[key]).is_file():
                    errors.append(f"missing profile asset: {profile[key]}")
            tokens_path = ROOT / profile["tokens_path"]
            if tokens_path.is_file():
                tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
                if tokens.get("profile_id") != profile.get("id"):
                    errors.append(f"profile id mismatch: {profile.get('id')}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: {ROOT.name} v{(ROOT / 'VERSION').read_text().strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
