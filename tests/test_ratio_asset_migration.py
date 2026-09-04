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
    "chapter-intro",
    "opening-weave-core",
    "topic-radar-core",
    "viral-breakdown-core",
    "script-draft-core",
    "storyboard-plan-core",
    "tone-rewrite-core",
    "cover-title-core",
    "graphic-card-core",
    "material-archive-core",
    "data-review-core",
    "weekly-report-core",
    "production-loop-core",
)
ARTIFACT_SHA256_4X3 = {
    "rich-skill-explanation": "e8f83fa5de3112d2ebd1daadc36d2d9afb9f05c5c68ce33bc4735124b3a2a75a",
    "capability-convergence": "99d200386efa34611aef8ac38ee896e2602d00a701fe52cceeac7cc90093f858",
    "gap-first-selection": "79b62c02d06ddf7ba12872e7471282ad5431376e1f04b71300bf8a2a3fde1c6d",
    "rse-input-transform": "b32e03c0b33d8aa89e51059e6af0ddc77f55405e979d9adda5b08c3dc1aa34f7",
    "rse-retrieve-distill": "bb334fea0bdbed5c990d36b9b72b76f86aebc2380dccb5e5679a3691a3e1327b",
    "rse-knowledge-roundtrip": "444af67eb9a6d2cfbfd34e41ef71356b8a1b92b31513fa48989a23bd9e1c3a88",
    "rse-persist-reuse": "5cb25650a8e1ff9c94a8ad401ccd88d6777d3f7f2dc7d97e6e9acdc350d62e53",
    "chapter-intro": "dd6249a19268f59ca0f3c6ad70012d10aefbc5717e00f61cc94cbfc6d4ed2405",
    "opening-weave-core": "5112a4f12bfa76bea4e1204cce25581117e8a0dd74000127b214f26ace0f5b77",
    "topic-radar-core": "13480f9e715e7dc29ade2aaa344232646df1e2163736474e8353247f1cb08f55",
    "viral-breakdown-core": "53ca6fe6cf2c7fb4a1d9134430e8d3694170e396b5d0083612635b39ce00d9e1",
    "script-draft-core": "c3e5e51ff0ff1df4b1c08a0fd389293457416188229f319a5bbe47669c228baa",
    "storyboard-plan-core": "0308690ad125a18837bac513e2421f95d99f603fe2b2769e182522323b1c72de",
    "tone-rewrite-core": "c26ca4a701c2b03d9be4624d1593ba2701b953abe5a704fcb48d567ce1a941e5",
    "cover-title-core": "b2ecc38fe9657042ffd5ccc68a83fcfe82716926115e657d4364d24e6c7f055d",
    "graphic-card-core": "7f0021fecc8ebd7fb065caceac1c4be9cbe2e76f565cc727336690f39654a0d3",
    "material-archive-core": "a0e23aec7edb8644f6bc0c3699a107e28af7b86478fe36888a0f8f567ac32677",
    "data-review-core": "cba5f446163e339af3445630514adcd35ea5ad91aa016eb4c1236278d7186c8a",
    "weekly-report-core": "ef3592b6f27421891728d8b0077b5e93554dde13bbca6d8a41ad05998af5541b",
    "production-loop-core": "6fe27d40f1b23cf5f0bfc65297a1287e3a5f7c955dbd4c55d3572864d9d4514f",
}
ARTIFACT_SHA256_16X9 = {
    "rich-skill-explanation": "ce258483b7c11ce7c576e45fe571f19e14b1a832cb3600dd8d8981de548aad09",
    "capability-convergence": "7a5b7a5d426bdefd3558a36877914925ec5bf9c9a7c87101811c6dae8c1b4806",
    "gap-first-selection": "fda3fcd063731a5d08fc530e1ea6a0228e389fe0c2c0d91e78815b907b5c4770",
    "rse-input-transform": "22ae0a2afd03214ca084073e2df418e5dc6326ea65ca9beb8586b72b1c79d375",
    "rse-retrieve-distill": "1e048034b1343ff51e33b78d9ee9c3f9b1d073b053d059a7fb75270e081a5f47",
    "rse-knowledge-roundtrip": "06bb48fb540ab52fb45400ee67c6e9fb515da637c5a2d43c5bbd3318dbbb46b2",
    "rse-persist-reuse": "c00cd88be5da88fbcb1a7a4698347c3850bebc4abf1027dd395c7e06c7a57ea8",
    "chapter-intro": "c21dadacd17e2fa9f82835cd46c10e65ee2907ee3fe1890d46976f7a10d53424",
    "opening-weave-core": "95a2fa3d2b56988d4b045f9a9ed22f04124478bfe488c051a28c16a443cb4723",
    "topic-radar-core": "296d4c8eba1a9aa1167f4d9166b096e88d046b5ffca50eed3c30985664daa3c2",
    "viral-breakdown-core": "2a744499d42d7b62e987c2f857541769eacb925262d45b50f8a5b1bf2884224c",
    "script-draft-core": "072e7af07150e06e6e6a494af30b5f5d5000d27a3a82fcd7d3d6ac9893a49352",
    "storyboard-plan-core": "f35450dc78e73628c4286c2d6332349ad999e7e624d97b42ac22e733300870ab",
    "tone-rewrite-core": "03be7818e9ef5ca7c2b1863c9ed05d08486e4f1ec3508a8c3a48c11aa4bde09d",
    "cover-title-core": "7e1353fe4b50494cd3cd83d435609894bd186e1207c06da7fd9b4c3acec6580c",
    "graphic-card-core": "e7a1650242dde5d2c19f06cfdc5ef46cd5058daa88442e090cd4bd861f71221c",
    "material-archive-core": "ae36dcd2ff503a3180d670efe5d587df3925bdc9ddd757b8e9facce7d6afe9a3",
    "data-review-core": "96dfe0a500ee79d0742b45308fe63d946ca0cddecd86b9b311ea72f2b699b05e",
    "weekly-report-core": "3e7399d3559df459a15d6d498c9b46ecd23b880900e4262459a64a6a160ff257",
    "production-loop-core": "79d5967773ec4fa647d5f477c82bb7b0c980a928bdca3a1d9d5e11d851dced8b",
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
    def test_migrated_assets_are_closed_and_ratio_accurate(self) -> None:
        roots = []
        for component_id in COMPONENTS:
            slots = None
            for ratio, width, hashes in (
                ("4x3", "1440", ARTIFACT_SHA256_4X3),
                ("16x9", "1920", ARTIFACT_SHA256_16X9),
            ):
                root = REPO / ".studio" / "components" / component_id / ratio / "v1"
                metadata = frontmatter(root / "COMPONENT.md")
                self.assertEqual("component-contract-v2", metadata["contract"])
                self.assertEqual(ratio, metadata["ratio"])
                self.assertEqual("migration-ready", metadata["status"])
                self.assertNotIn("profile", metadata)
                self.assertNotIn("subtemplate", metadata)
                self.assertEqual(hashes[component_id], metadata["artifact"]["sha256"])
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

        for ratio, width, artifact_hash in (
            ("4x3", "1440", "e4bdf553ac9fce0edce62834a2ef218aeba2928d728b59e29b017a649134235a"),
            ("16x9", "1920", "4e3c88e82e1c66a0915dedcd5c3792994a5f24983ffccb2d12fc24e56b7d24dc"),
        ):
            background = REPO / ".studio" / "backgrounds" / "rse-functional-background" / ratio / "v1"
            metadata = frontmatter(background / "BACKGROUND.md")
            self.assertEqual("background-contract-v1", metadata["contract"])
            self.assertEqual(ratio, metadata["ratio"])
            self.assertEqual("default", metadata["default_state"])
            self.assertEqual(artifact_hash, metadata["artifact"]["sha256"])
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


if __name__ == "__main__":
    unittest.main()
