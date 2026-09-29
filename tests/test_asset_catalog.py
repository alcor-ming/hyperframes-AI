"""Classification is selection metadata, never rewritten package content."""
import json
from pathlib import Path
import shutil
import unittest

import test_asset_store as fixtures
import asset_contract as CONTRACT

COMPONENT, STORE = fixtures.COMPONENT, fixtures.STORE


class AssetCatalogTest(unittest.TestCase):
    setUp = fixtures.AssetStoreTest.setUp
    accept = fixtures.AssetStoreTest.accept

    def selection(self, value):
        (self.store / "selection.json").write_text(json.dumps({self.ref: value}))

    def test_reference_hidden_but_accepted_evidence_preserved(self):
        record = self.accept()
        package, _ = STORE.resolve_component(self.harness, self.ref)
        original = (package / "HASHES.json").read_bytes()
        self.selection({"asset_layer": "reference", "recommendation": "historical"})
        self.assertFalse(STORE.discover_components(self.harness)["assets"])
        assets = STORE.discover_components(self.harness, asset_layer="reference")["assets"]
        accepted = next(item for item in assets if item["origin"] == "accepted")
        self.assertEqual(accepted["lifecycle"], "accepted")
        self.assertEqual(accepted["acceptance"], record)
        for value in (self.ref, str(package)):
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Reference assets"):
                STORE.resolve_component(self.harness, value)
        self.assertEqual(original, (package / "HASHES.json").read_bytes())

    def test_invalid_selection_fails_closed_at_use(self):
        self.accept()
        self.selection({"asset_layer": "bogus"})
        with self.assertRaisesRegex(COMPONENT.ComponentError, "asset_layer"):
            STORE.resolve_component(self.harness, self.ref)

    def test_complete_index_does_not_depend_on_filter(self):
        self.accept()
        self.selection({"asset_layer": "building-block", "recommendation": "recommended"})
        self.assertFalse(STORE.discover_components(self.harness, query="not-a-match")["assets"])
        index = json.loads((self.store / ".catalog-index.json").read_text())
        self.assertEqual({self.ref}, {item["component_ref"] for item in index["assets"]})
        self.assertTrue(all(item["asset_layer"] == "building-block" for item in index["assets"]))
        before = (self.store / ".catalog-index.json").read_bytes()
        STORE.discover_components(self.harness, rebuild=True)
        self.assertEqual(before, (self.store / ".catalog-index.json").read_bytes())

    def test_unknown_legacy_not_classified_by_name(self):
        self.accept()
        report = STORE.discover_components(self.harness, audit=True)
        self.assertEqual({"unclassified"}, {item["asset_layer"] for item in report["assets"]})
        self.assertTrue(any(item["code"] == "unclassified_asset" for item in report["audit"]["warnings"]))

    def test_corrupt_derived_index_is_rebuilt(self):
        self.accept()
        index = self.store / ".catalog-index.json"
        index.write_text("{broken")
        result = STORE.discover_components(self.harness, rebuild=True)
        self.assertFalse(result["errors"])
        self.assertTrue(json.loads(index.read_text())["assets"])

    def test_managed_sources_reject_symlink_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        managed = self.store / "sources"
        managed.symlink_to(outside, target_is_directory=True)
        for operation in (lambda: STORE.register_source(self.store, managed),
                          lambda: STORE.authoring_project(self.harness, managed),
                          lambda: STORE.discover_components(self.harness)):
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Linked path"):
                operation()
        managed.unlink()
        managed.mkdir()
        linked = managed / "escape"
        linked.symlink_to(outside, target_is_directory=True)
        for operation in (lambda: STORE.register_source(self.store, linked),
                          lambda: STORE.authoring_project(self.harness, linked)):
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Linked path"):
                operation()

    def test_retirement_and_managed_source(self):
        legacy = self.harness / ".studio/components/example"
        shutil.copytree(self.source, legacy)
        managed = self.store / "sources/new"
        managed.mkdir(parents=True)
        (managed / "asset.json").write_text(json.dumps({"id": "managed", "version": 1, "kind": "module", "asset_layer": "scene-template"}))
        STORE.register_source(self.store, managed)
        self.assertEqual(STORE.authoring_project(self.harness, managed), managed)
        (self.store / "catalog-migration.json").write_text(json.dumps({"schema_version": 1, "retired_roots": [str(legacy.parent), str(managed)]}))
        report = STORE.discover_components(self.harness)
        self.assertEqual(["managed@v1"], [item["component_ref"] for item in report["assets"]])
        self.assertEqual("scene-template", report["assets"][0]["asset_layer"])
        (self.store / "catalog-migration.json").write_text('{"retired_roots":["relative"]}')
        with self.assertRaisesRegex(COMPONENT.ComponentError, "retired_roots"):
            STORE.discover_components(self.harness)

    def test_module_metadata_and_dependency_install_guard(self):
        source = self.store / "sources/module"
        source.mkdir(parents=True)
        metadata = {"schema_version": 1, "id": "module", "version": 1, "kind": "module", "entry": "main.js", "asset_layer": "building-block"}
        (source / "asset.json").write_text(json.dumps(metadata))
        (source / "main.js").write_text("window.example = 1;")
        candidate = STORE.pack_source(self.store, source)
        ref = candidate["component_ref"]
        STORE.accept_component(self.store, ref, candidate["package_sha256"], "synthetic fixture", runtime_root=self.harness)
        reference = {"ref": ref, "kind": "module", "package_sha256": candidate["package_sha256"]}
        self.assertEqual(ref, STORE.resolve_asset_closure(self.harness, [reference])[0]["ref"])
        (self.store / "selection.json").write_text(json.dumps({ref: {"asset_layer": "reference"}}))
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Reference assets"):
            STORE.resolve_asset_closure(self.harness, [reference])
        metadata["asset_layer"] = "wrong"
        (source / "asset.json").write_text(json.dumps(metadata))
        with self.assertRaisesRegex(COMPONENT.ComponentError, "asset_layer"):
            CONTRACT.freeze_source(source, self.root / "bad-package")
