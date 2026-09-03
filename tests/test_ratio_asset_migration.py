from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
COMPONENTS = (
    "rich-skill-explanation",
    "capability-convergence",
    "gap-first-selection",
    "rse-input-transform",
    "rse-retrieve-distill",
    "rse-knowledge-roundtrip",
    "rse-persist-reuse",
)
ARTIFACT_SHA256 = {
    "rich-skill-explanation": "e8f83fa5de3112d2ebd1daadc36d2d9afb9f05c5c68ce33bc4735124b3a2a75a",
    "capability-convergence": "99d200386efa34611aef8ac38ee896e2602d00a701fe52cceeac7cc90093f858",
    "gap-first-selection": "79b62c02d06ddf7ba12872e7471282ad5431376e1f04b71300bf8a2a3fde1c6d",
    "rse-input-transform": "b32e03c0b33d8aa89e51059e6af0ddc77f55405e979d9adda5b08c3dc1aa34f7",
    "rse-retrieve-distill": "bb334fea0bdbed5c990d36b9b72b76f86aebc2380dccb5e5679a3691a3e1327b",
    "rse-knowledge-roundtrip": "444af67eb9a6d2cfbfd34e41ef71356b8a1b92b31513fa48989a23bd9e1c3a88",
    "rse-persist-reuse": "5cb25650a8e1ff9c94a8ad401ccd88d6777d3f7f2dc7d97e6e9acdc350d62e53",
}


def frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    end = lines.index("---", 1)
    return json.loads("\n".join(lines[1:end]))


def verify_hashes(root: Path) -> None:
    manifest = json.loads((root / "HASHES.json").read_text(encoding="utf-8"))
    entries = []
    for path in sorted(
        (item for item in root.rglob("*") if item.is_file() and item.name != "HASHES.json"),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    lines = "".join(f"{item['sha256']}  {item['path']}\n" for item in entries)
    assert manifest["algorithm"] == "asset-package-sha256-v1"
    assert manifest["files"] == entries
    assert manifest["package_sha256"] == hashlib.sha256(lines.encode()).hexdigest()


class TemplateParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.template_depth = 0
        self.compositions: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "template":
            self.template_depth += 1
        values = dict(attrs)
        if values.get("data-composition-id"):
            assert self.template_depth > 0
            self.compositions.append(values)

    def handle_endtag(self, tag: str) -> None:
        if tag == "template":
            self.template_depth -= 1


class RatioAssetMigrationTest(unittest.TestCase):
    def test_migrated_4x3_assets_are_closed_and_ratio_accurate(self) -> None:
        roots = []
        for component_id in COMPONENTS:
            root = REPO / ".studio" / "components" / component_id / "4x3" / "v1"
            metadata = frontmatter(root / "COMPONENT.md")
            self.assertEqual("component-contract-v2", metadata["contract"])
            self.assertEqual("4x3", metadata["ratio"])
            self.assertEqual("migration-ready", metadata["status"])
            self.assertNotIn("profile", metadata)
            self.assertNotIn("subtemplate", metadata)
            self.assertEqual(ARTIFACT_SHA256[component_id], metadata["artifact"]["sha256"])
            source = (root / "component.html").read_text(encoding="utf-8")
            self.assertRegex(source, r"background:\s*transparent")
            self.assertNotRegex(source, r"#[0-9A-Fa-f]{6}")
            self.assertRegex(source, r"gsap\.timeline\(\{\s*paused:\s*true")
            parser = TemplateParser()
            parser.feed(source)
            composition = next(
                item for item in parser.compositions if item["data-composition-id"] == component_id
            )
            self.assertEqual("1440", composition["data-width"])
            self.assertEqual("1080", composition["data-height"])
            roots.append(root)

        background = REPO / ".studio" / "backgrounds" / "rse-functional-background" / "4x3" / "v1"
        metadata = frontmatter(background / "BACKGROUND.md")
        self.assertEqual("background-contract-v1", metadata["contract"])
        self.assertEqual("default", metadata["default_state"])
        self.assertEqual(
            "f02bc892f8ef5c0ba0c1705e19c6075a01a77d0bf0ecc6264824050a102ce8d6",
            metadata["artifact"]["sha256"],
        )
        source = (background / "background.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"#[0-9A-Fa-f]{6}")
        self.assertNotRegex(source, r"(?:src|href)=[\"']https?://|url\([\"']?https?://")
        roots.append(background)

        for root in roots:
            verify_hashes(root)


if __name__ == "__main__":
    unittest.main()
