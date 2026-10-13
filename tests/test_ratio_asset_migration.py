from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "ratio-migration"
COMPONENTS = ("capability-convergence", "chapter-intro")
RATIO_WIDTH = {"4x3": "1440", "16x9": "1920"}


def frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    end = lines.index("---", 1)
    return json.loads("\n".join(lines[1:end]))


def declared_artifact_sha256(root: Path, metadata: dict) -> str:
    """Digest the bytes of the artifact file the fixture declares in metadata."""

    return hashlib.sha256((root / metadata["artifact"]["file"]).read_bytes()).hexdigest()


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
    def test_migrated_assets_are_closed_and_ratio_accurate(self) -> None:
        roots = []
        for component_id in COMPONENTS:
            slots = None
            for ratio, width in RATIO_WIDTH.items():
                root = FIXTURES / "components" / component_id / ratio / "v1"
                metadata = frontmatter(root / "COMPONENT.md")
                self.assertEqual("component-contract-v2", metadata["contract"])
                self.assertEqual(ratio, metadata["ratio"])
                self.assertEqual("migration-ready", metadata["status"])
                self.assertNotIn("profile", metadata)
                self.assertNotIn("subtemplate", metadata)
                self.assertEqual(metadata["artifact"]["sha256"], declared_artifact_sha256(root, metadata))
                contract = json.loads((root / "contract.schema.json").read_text(encoding="utf-8"))
                if slots is None:
                    slots = contract["slots"]
                else:
                    self.assertEqual(slots, contract["slots"])
                source = (root / "component.html").read_text(encoding="utf-8")
                self.assertRegex(source, r"background:\s*transparent")
                self.assertNotRegex(source, r"#[0-9A-Fa-f]{6}|oklch\(")
                self.assertNotRegex(source, r"(?:src|href)=[\"']https?://|url\([\"']?https?://")
                self.assertRegex(source, r"gsap\.timeline\(\{\s*paused:\s*true")
                parser = TemplateParser()
                parser.feed(source)
                composition = next(
                    item for item in parser.compositions if item["data-composition-id"] == component_id
                )
                self.assertEqual(width, composition["data-width"])
                self.assertEqual("1080", composition["data-height"])
                self.assertIn("time_scale", composition["data-composition-variables"])
                fixture = json.loads((root / "preview.fixture.json").read_text(encoding="utf-8"))
                duration = float(composition["data-duration"])
                key_times = fixture.get("key_times_seconds")
                if key_times is None:
                    key_times = metadata["preview"]["key_times_seconds"]
                self.assertTrue(all(0 <= key_time <= duration for key_time in key_times))
                roots.append(root)

        for ratio, width in RATIO_WIDTH.items():
            background = FIXTURES / "backgrounds" / "rse-functional-background" / ratio / "v1"
            metadata = frontmatter(background / "BACKGROUND.md")
            self.assertEqual("background-contract-v1", metadata["contract"])
            self.assertEqual(ratio, metadata["ratio"])
            self.assertEqual("default", metadata["default_state"])
            self.assertEqual(
                metadata["artifact"]["sha256"], declared_artifact_sha256(background, metadata)
            )
            source = (background / "background.html").read_text(encoding="utf-8")
            self.assertNotRegex(source, r"#[0-9A-Fa-f]{6}|oklch\(")
            self.assertNotRegex(source, r"(?:src|href)=[\"']https?://|url\([\"']?https?://")
            parser = TemplateParser()
            parser.feed(source)
            composition = next(
                item
                for item in parser.compositions
                if item["data-composition-id"] == "rse-functional-background"
            )
            self.assertEqual(width, composition["data-width"])
            self.assertEqual("1080", composition["data-height"])
            self.assertIn("time_scale", composition["data-composition-variables"])
            roots.append(background)

        for root in roots:
            verify_hashes(root)

    def test_capability_convergence_16x9_applies_declared_slots(self) -> None:
        source = (
            FIXTURES / "components" / "capability-convergence" / "16x9" / "v1" / "component.html"
        ).read_text(encoding="utf-8")
        for marker in (
            'textSlot("context"',
            "RUNTIME_VALUES.items",
            'textSlot("proposition"',
            'textSlot("core_name"',
            'textSlot("summary_emphasis"',
            'textSlot("summary_suffix"',
            'textSlot("handoff_label"',
            'data-visual-surface="convergence_field"',
        ):
            self.assertIn(marker, source)


if __name__ == "__main__":
    unittest.main()
