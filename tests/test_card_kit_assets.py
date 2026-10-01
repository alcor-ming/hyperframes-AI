from pathlib import Path
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / ".studio"))
import asset_contract as CONTRACT
import asset_store as STORE
import card_kit_assets as CARDS
import component_harness as COMPONENT


class CardKitAssetsTest(unittest.TestCase):
    def test_export_pack_accept_install_and_offline_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "sources/card-kit"
            result = CARDS.export_card_kit(REPO, source)
            self.assertEqual(result, CARDS.export_card_kit(REPO, source))
            self.assertEqual("source", result["status"])
            self.assertEqual({"asset.json", "card-kit.js", "card-kit.css", "USAGE.md"},
                             {path.name for path in source.iterdir()})
            self.assertFalse((source / "HASHES.json").exists())
            store = root / "store"
            candidate = STORE.pack_source(store, source)
            ref = candidate["component_ref"]
            package = Path(candidate["path"]) / "package"
            CONTRACT.validate_asset(package, expected_ref=ref)
            self.assertFalse((store / "packages/card-kit/v1").exists())
            record = STORE.accept_component(store, ref, candidate["package_sha256"],
                                            "Isolated runtime packaging test only", runtime_root=REPO)
            project = root / "project"
            project.mkdir()
            COMPONENT.install_component(store / "packages/card-kit/v1", project, {
                "schema_version": 3, "component_ref": ref, "scene": "S01",
                "usage": {"role": "subject", "required": True}}, acceptance=record)
            vendor = project / "vendor/components/card-kit/v1"
            self.assertEqual((source / "card-kit.css").read_bytes(), (vendor / "card-kit.css").read_bytes())
            (project / "index.html").write_text(
                '<link rel="stylesheet" href="vendor/components/card-kit/v1/card-kit.css">'
                '<script src="vendor/components/card-kit/v1/card-kit.js"></script>', encoding="utf-8")
            lock = json.loads((project / "COMPONENT_LOCK.json").read_text())
            self.assertEqual(2, lock["schema_version"])
            shutil.rmtree(store)
            COMPONENT.verify_installation(project, public_root=REPO)
            (source / "card-kit.js").write_text("changed editable source", encoding="utf-8")
            with self.assertRaisesRegex(COMPONENT.ComponentError, "different content"):
                CARDS.export_card_kit(REPO, source)
            self.assertEqual("changed editable source", (source / "card-kit.js").read_text())
            (vendor / "card-kit.css").write_text("changed frozen CSS", encoding="utf-8")
            with self.assertRaises(COMPONENT.ComponentError):
                COMPONENT.verify_installation(project, public_root=REPO)

    def test_export_rejects_links_and_missing_inputs_without_partial_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            linked = root / "linked"
            linked.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(COMPONENT.ComponentError, "links"):
                CARDS.export_card_kit(REPO, linked / "source")
            harness = root / "harness"
            (harness / ".studio/runtime").mkdir(parents=True)
            with self.assertRaises(COMPONENT.ComponentError):
                CARDS.export_card_kit(harness, source)
            self.assertFalse(source.exists())

    def test_review_export_stays_inside_isolated_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            review = root / 'review'
            with patch.dict(os.environ, {'HYPERFRAMES_AI_REVIEW': '1',
                                        'HYPERFRAMES_AI_ASSET_REVIEW_ROOT': str(review),
                                        'HYPERFRAMES_AI_WORK_ROOT': str(root / 'review-work')}):
                forbidden = root / 'outside-source'
                with self.assertRaisesRegex(COMPONENT.ComponentError, 'Review source'):
                    CARDS.export_card_kit(REPO, forbidden)
                self.assertFalse(forbidden.exists())
                result = CARDS.export_card_kit(REPO, review / 'sources/card-kit')
                self.assertEqual('source', result['status'])

    def test_export_rejects_runtime_and_frozen_ancestors(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            harness = root / 'harness'
            (harness / '.studio').mkdir(parents=True)
            for target in (harness, harness / '.studio/new', harness / 'runtime/new'):
                with self.subTest(target=target), self.assertRaisesRegex(COMPONENT.ComponentError, 'Harness runtime'):
                    CARDS.export_card_kit(harness, target)
            for index, name in enumerate(('COMPONENT_LOCK.json', 'HASHES.json', 'acceptance.json')):
                frozen = root / f'frozen-{index}'
                frozen.mkdir()
                (frozen / name).write_text('{}', encoding='utf-8')
                target = frozen / 'nested/new-source'
                with self.subTest(marker=name), self.assertRaisesRegex(COMPONENT.ComponentError, 'frozen packages'):
                    CARDS.export_card_kit(harness, target)
                self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
