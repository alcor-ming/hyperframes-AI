import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_asset_store as fixtures
STORE = fixtures.STORE


class DiscoveryTest(unittest.TestCase):
    setUp = fixtures.AssetStoreTest.setUp
    accept = fixtures.AssetStoreTest.accept

    def test_incremental_selection_missing_files_and_acceptance(self):
        self.accept()
        first = STORE.discover_components(self.harness)
        self.assertTrue(first["refreshed"])
        self.assertFalse(STORE.discover_components(self.harness)["refreshed"])
        accepted = next(row for row in first["assets"] if row["origin"] == "accepted")
        self.assertEqual("pending", accepted["recommendation"])
        self.assertIn("metadata-only", accepted["check_scope"])
        metadata = self.store / "selection.json"
        metadata.write_text(json.dumps({self.ref: {"aliases": ["章节开场"], "tags": ["title"], "recommendation": "recommended"}}, ensure_ascii=False))
        found = STORE.discover_components(self.harness, "章节开场", tag="title", recommendation="recommended")
        self.assertTrue(found["assets"][0]["available"])
        self.assertEqual([str(metadata)], found["refreshed"])
        self.assertIn("aliases", found["assets"][0]["match_reasons"])
        self.assertFalse(STORE.discover_components(self.harness, ratio="unknown-format")["assets"])
        package = Path(accepted["path"])
        (package / "component.html").unlink()
        broken = STORE.discover_components(self.harness)
        self.assertFalse(any(row["available"] for row in broken["assets"]))
        self.assertTrue(broken["errors"])
        with self.assertRaises(STORE.ComponentError):
            STORE.resolve_component(self.harness, self.ref)

    def test_conflict_even_when_conflicting_package_has_missing_files(self):
        self.accept()
        work = self.root / "work-lock.json"
        work.write_text('{"unchanged":true}')
        before = work.read_bytes()
        candidate = self.store / "candidates" / STORE._relative(self.ref) / "package"
        manifest = candidate / "HASHES.json"
        data = json.loads(manifest.read_text())
        data["package_sha256"] = "0" * 64
        manifest.write_text(json.dumps(data))
        (candidate / "component.html").unlink()
        result = STORE.discover_components(self.harness)
        accepted = next(row for row in result["assets"] if row["origin"] == "accepted")
        self.assertFalse(accepted["available"])
        self.assertIn("conflict", accepted)
        self.assertEqual(result["assets"], STORE.discover_components(self.harness, rebuild=True)["assets"])
        self.assertEqual(before, work.read_bytes())
        acceptance = self.store / "acceptances" / STORE._relative(self.ref) / "acceptance.json"
        acceptance.unlink()
        self.assertFalse(any(row["available"] for row in STORE.discover_components(self.harness)["assets"]))

    def test_selection_states_query_scope_and_cache_failure(self):
        self.accept()
        for state in ("recommended", "historical", "pending"):
            with self.subTest(state=state):
                (self.store / "selection.json").write_text(json.dumps({self.ref: {
                    "aliases": ["中文别名"], "recommendation": state, "replacement": "next@v2"}}))
                rows = STORE.discover_components(self.harness, "中文别名", recommendation=state)["assets"]
                self.assertTrue(rows)
                self.assertTrue(rows[0]["available"])
                self.assertEqual(state, rows[0]["recommendation"])
        for query in (str(self.root), "automated contract tests"):
            self.assertFalse(STORE.discover_components(self.harness, query)["assets"])
        with patch.object(STORE, "_atomic_json", side_effect=OSError("read-only cache")):
            result = STORE.discover_components(self.harness, rebuild=True)
        self.assertTrue(result["assets"][0]["available"])
        self.assertTrue(result["errors"][-1]["unsynchronized"])
        self.assertFalse(STORE.discover_components(self.harness, rebuild=True)["errors"])

    def test_new_registered_sources_and_schema2_ratios(self):
        STORE.discover_components(self.harness)
        source = self.root / "new-source"
        source.mkdir()
        STORE.register_source(self.store, source)
        for ratios in (["16:9", "9:16"], []):
            (source / "asset.json").write_text(json.dumps({"id": "new-source", "version": 1,
                "schema_version": 2, "kind": "theme", "compatibility": {"ratios": ratios}}))
            rows = STORE.discover_components(self.harness, ratio="16:9" if ratios else "unknown")["assets"]
            self.assertEqual(1, len(rows))
            self.assertEqual(ratios, rows[0]["ratios"])
            self.assertEqual("source", rows[0]["group"])
            self.assertFalse(rows[0]["available"])


if __name__ == "__main__":
    unittest.main()
