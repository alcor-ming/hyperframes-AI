#!/usr/bin/env python3
"""Validate the thin Skill and repository Harness; profiles are legacy data."""

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
]
REQUIRED_HARNESS = [
    "AGENTS.md",
    "work",
    ".studio/spec/visual-design.md",
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

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: {ROOT.name} v{(ROOT / 'VERSION').read_text().strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
