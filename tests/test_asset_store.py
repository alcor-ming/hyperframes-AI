from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / ".studio"))
import asset_store as STORE
import component_harness as COMPONENT


class AssetStoreTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.harness = self.root / "harness"
        self.harness.mkdir()
        shutil.copyfile(REPO / "windows-runtime.lock.json", self.harness / "windows-runtime.lock.json")
        self.store = self.root / "assets"
        self.environment = patch.dict(os.environ, {
            "HYPERFRAMES_AI_ASSET_CONFIG": str(self.root / "local.json"),
            "HYPERFRAMES_AI_ASSET_ROOT": "", "HYPERFRAMES_AI_ROOT": str(self.harness),
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        STORE.configure_asset_store(self.harness, self.store)
        self.source = self.root / "source"
        shutil.copytree(REPO / ".studio/components/chapter-intro/4x3/v1", self.source)
        # A new local identity proves that discovery has no Harness asset-name list.
        for name in ("COMPONENT.md", "component.html", "contract.schema.json", "preview.fixture.json"):
            path = self.source / name
            path.write_text(path.read_text(encoding="utf-8").replace("chapter-intro", "external-example"), encoding="utf-8")
        COMPONENT.write_hashes(self.source)
        self.ref = "external-example/4x3@v1"

    def accept(self):
        candidate = STORE.import_component(self.store, self.source)
        return STORE.accept_component(self.store, self.ref, candidate["package_sha256"],
                                      "Synthetic fixture acceptance for automated contract tests", runtime_root=self.harness)

    def test_root_library_is_separate_from_work_data_and_installed_code(self):
        work = self.root / "workspace"
        store = work / "asset-library/store"
        source = work / "asset-library/sources"
        source.mkdir(parents=True)
        with patch.dict(os.environ, {"HYPERFRAMES_AI_WORK_ROOT": str(work)}):
            STORE.configure_asset_store(self.harness, store)
            STORE.register_source(store, source)
            project = source / "sample"
            project.mkdir()
            self.assertEqual(STORE.authoring_project(self.harness, project), project)
            for forbidden in (work, work / "works/active", work / ".runtime", work / "assets"):
                forbidden.mkdir(parents=True, exist_ok=True)
                with self.assertRaises(COMPONENT.ComponentError):
                    STORE.configure_asset_store(self.harness, forbidden)
                with self.assertRaises(COMPONENT.ComponentError):
                    STORE.register_source(store, forbidden)

    def test_module_media_pack_install_and_offline_lock(self):
        from PIL import Image
        project = self.root / "project"
        project.mkdir()
        entries = []
        for kind, entry in (("module", "move.js"), ("media", "image.png")):
            source = self.root / kind
            source.mkdir()
            metadata = {"schema_version": 1, "id": f"local-{kind}", "version": 1, "kind": kind,
                        "entry": entry, "source_url": "https://example.invalid/source", "rights": "test-owned"}
            (source / "asset.json").write_text(json.dumps(metadata))
            if kind == "module":
                (source / entry).write_text("window.localMove = (timeline, target) => timeline.to(target, {x: 40});")
            else:
                Image.new("RGB", (12, 8), "red").save(source / entry)
            candidate = STORE.pack_source(self.store, source)
            self.assertFalse((source / "HASHES.json").exists())
            ref = candidate["component_ref"]
            record = STORE.accept_component(self.store, ref, candidate["package_sha256"], "synthetic fixture", runtime_root=self.harness)
            package, _ = STORE.resolve_component(self.harness, ref)
            with patch.object(STORE, "file_sha256", side_effect=AssertionError("Inventory must not hash package bytes")):
                self.assertTrue(any(row["component_ref"] == ref for row in STORE.discover_components(self.harness)["assets"]))
            binding = {"schema_version": 3, "component_ref": ref, "scene": "S01",
                       "usage": {"role": "subject", "required": True}}
            COMPONENT.install_component(package, project, binding, acceptance=record)
            relative = f"vendor/components/local-{kind}/v1/{entry}"
            entries.append(f'<script src="{relative}"></script>' if kind == "module" else f'<img src="{relative}">')
            (source / "asset.json").write_text("changed source")
        (project / "index.html").write_text("<html><body>" + "".join(entries) + "</body></html>")
        lock = (project / "COMPONENT_LOCK.json").read_bytes()
        self.assertEqual(2, json.loads(lock)["schema_version"])
        shutil.rmtree(self.store)
        self.assertEqual(2, len(COMPONENT.verify_installation(project)["components"]))
        self.assertEqual(lock, (project / "COMPONENT_LOCK.json").read_bytes())
        (project / "index.html").write_text("<html></html>")
        with self.assertRaisesRegex(COMPONENT.ComponentError, "not referenced"):
            COMPONENT.verify_installation(project)

    def test_review_asset_writes_and_acceptance_do_not_escape(self):
        import work_requests
        production = self.root / "production"
        for name in ("active", "parked", "archive"):
            (production / "works" / name).mkdir(parents=True)
        review_work = work_requests.init_review(production, "test")
        review = self.root / "asset-review"
        source = review / "sources/module"
        source.mkdir(parents=True)
        (source / "asset.json").write_text(json.dumps({"schema_version": 1, "id": "isolated-module",
                                                     "version": 1, "kind": "module", "entry": "move.js"}))
        (source / "move.js").write_text("window.move = () => 1;")
        store = review / "store"
        config = self.root / "session.json"
        config.write_text(json.dumps({"asset_root": str(store), "work_root": str(review_work),
                                      "asset_source_roots": [str(review / "sources")]}))
        with patch.dict(os.environ, {"HYPERFRAMES_AI_REVIEW": "1", "HYPERFRAMES_AI_WORK_ROOT": str(review_work),
                                     "HYPERFRAMES_AI_ASSET_REVIEW_ROOT": str(review),
                                     "HYPERFRAMES_AI_REVIEW_PROTECTED_ROOTS": json.dumps([str(production), str(self.store)]),
                                     "HYPERFRAMES_AI_ASSET_CONFIG": str(config)}):
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Review"):
                STORE.configure_asset_store(self.harness, self.store)
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Review"):
                STORE.pack_source(self.store, source)
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Review source"):
                STORE.register_source(store, self.source)
            candidate = STORE.pack_source(store, source)
            record = STORE.accept_component(store, candidate["component_ref"], candidate["package_sha256"],
                                            "Review simulation only", runtime_root=self.harness)
            package = store / "packages/isolated-module/v1"
            release = STORE._validate_package(package)
            project = review / "sources/sample"
            project.mkdir()
            COMPONENT.install_component(package, project, {
                "schema_version": 3, "component_ref": candidate["component_ref"], "scene": "S01",
                "usage": {"role": "auxiliary", "required": True}}, acceptance=record)
            (project / "index.html").write_text('<script src="vendor/components/isolated-module/v1/move.js"></script>')
            COMPONENT.verify_installation(project)
            (store / "acceptances/escape").symlink_to(self.store, target_is_directory=True)
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Linked"):
                STORE._target(store, "acceptances/escape/record.json")
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Review asset acceptance"):
            COMPONENT.validate_component_acceptance(record, release, runtime_root=self.harness)
        self.assertFalse((self.store / "record.json").exists())

    def test_session_roots_and_sources_are_defaults_only(self):
        pinned = self.root / "pinned.json"
        default = self.root / "defaults.json"
        initial = {"asset_root": str(self.store), "asset_source_roots": [str(self.source)]}
        pinned.write_text(json.dumps(initial))
        default.write_text(json.dumps(initial))
        with patch.dict(os.environ, {"HYPERFRAMES_AI_ASSET_CONFIG": str(pinned),
                                     "HYPERFRAMES_AI_DEFAULT_CONFIG": str(default)}):
            STORE.configure_asset_store(self.harness, self.root / "later-store")
            self.assertEqual(self.store, STORE.asset_store_root(self.harness))
            other = self.root / "other-source"
            other.mkdir()
            STORE.register_source(self.store, other)
            self.assertEqual([str(self.source)], STORE._configured_sources(self.harness, self.store))
            self.assertEqual(initial, json.loads(pinned.read_text()))

    def test_asset_writer_lock_releases_without_stale_owner(self):
        path = self.store / ".asset-write.lock"
        with COMPONENT.package_write_lock(path):
            with self.assertRaisesRegex(COMPONENT.ComponentError, "Another asset writer"):
                with COMPONENT.package_write_lock(path):
                    self.fail("Concurrent writer acquired the lock")
        with COMPONENT.package_write_lock(path):
            self.assertTrue(path.is_file())

    def metadata(self, **changes):
        path = self.source / "COMPONENT.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        end = lines.index("---", 1)
        data = json.loads("\n".join(lines[1:end]))
        data.update(changes)
        path.write_text("---\n" + json.dumps(data) + "\n---\n" + "\n".join(lines[end + 1:]) + "\n", encoding="utf-8")
        COMPONENT.write_hashes(self.source)

    def binding(self):
        fixture = json.loads((self.source / "preview.fixture.json").read_text())
        return {"schema_version": 2, "component_ref": self.ref, "scene": "S01",
                "slots": fixture["slots"], "placement": {"width": 1440, "height": 1080},
                "timing": {"offset": 0, "time_scale": 1, "hero_hold": 0, "handoff_hold": 0},
                "surfaces": fixture.get("surfaces", {}), "assets": {}}

    def test_independent_acceptance_and_offline_work_copy(self):
        harness_hashes = {path.name: COMPONENT.file_sha256(path) for path in (
            REPO / ".studio/component_harness.py", REPO / ".studio/asset_store.py", REPO / "windows-runtime.lock.json")}
        source_hash = COMPONENT.package_sha256(self.source)
        STORE.register_source(self.store, self.source)
        source = STORE.discover_components(self.harness)["assets"][0]
        self.assertEqual((self.ref, False, "source"), (source["component_ref"], source["available"], source["origin"]))
        with self.assertRaisesRegex(COMPONENT.ComponentError, "not accepted"):
            STORE.resolve_component(self.harness, self.ref)
        acceptance = self.accept()
        selected, record = STORE.resolve_component(self.harness, self.ref)
        self.assertEqual(acceptance, record)
        self.assertEqual(source_hash, COMPONENT.package_sha256(selected))
        self.assertEqual("migration-ready", COMPONENT._read_frontmatter(selected / "COMPONENT.md")["status"])
        project = self.root / "project"
        project.mkdir()
        COMPONENT.install_component(selected, project, self.binding(), acceptance=record)
        frozen_lock = (project / "COMPONENT_LOCK.json").read_bytes()
        vendor = project / "vendor/components/external-example/4x3/v1"
        self.assertEqual(source_hash, COMPONENT.package_sha256(vendor))
        runtime_path = self.harness / "windows-runtime.lock.json"
        runtime = json.loads(runtime_path.read_text())
        runtime["versions"]["three"] = "999.0.0"
        runtime_path.write_text(json.dumps(runtime))
        shutil.rmtree(self.store)
        COMPONENT.verify_installation(project, public_root=self.harness)
        self.assertEqual(frozen_lock, (project / "COMPONENT_LOCK.json").read_bytes())
        for name, digest in harness_hashes.items():
            path = REPO / ("windows-runtime.lock.json" if name == "windows-runtime.lock.json" else f".studio/{name}")
            self.assertEqual(digest, COMPONENT.file_sha256(path))

    def test_conflicting_identity_is_not_overwritten_and_review_is_isolated(self):
        candidate = STORE.import_component(self.store, self.source)
        with self.assertRaisesRegex(COMPONENT.ComponentError, "exact candidate"):
            STORE.accept_component(self.store, self.ref, "0" * 64, "reviewed", runtime_root=self.harness)
        package = Path(candidate["path"]) / "package"
        review_html = Path(candidate["review"]) / "component.html"
        original = (package / "component.html").read_bytes()
        review_html.write_bytes(original + b"\n")
        self.assertEqual(original, (package / "component.html").read_bytes())
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Review copy changed"):
            STORE.accept_component(self.store, self.ref, candidate["package_sha256"], "reviewed", runtime_root=self.harness)
        review_html.write_bytes(original)
        self.accept()
        self.metadata(communication_goal="Different implementation with the same identity")
        with self.assertRaisesRegex(COMPONENT.ComponentError, "different content"):
            STORE.import_component(self.store, self.source)
        STORE.register_source(self.store, self.source)
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Conflicting identity"):
            STORE.resolve_component(self.harness, self.ref)

    def test_runtime_and_dependency_checks_are_asset_local(self):
        self.metadata(runtime={"versions": {"hyperframes": "999.0.0"}})
        candidate = STORE.import_component(self.store, self.source)
        with self.assertRaisesRegex(COMPONENT.ComponentError, "runtime version is incompatible"):
            STORE.accept_component(self.store, self.ref, candidate["package_sha256"], "reviewed", runtime_root=self.harness)
        shutil.rmtree(self.store / "candidates")
        self.metadata(runtime={})
        html = self.source / "component.html"
        html.write_text(html.read_text(encoding="utf-8") + '\n<script src="assets/missing.js"></script>', encoding="utf-8")
        COMPONENT.write_hashes(self.source)
        candidate = STORE.import_component(self.store, self.source)
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Dependency is missing"):
            STORE.accept_component(self.store, self.ref, candidate["package_sha256"], "reviewed", runtime_root=self.harness)

    def test_unaccepted_external_approved_label_and_unsupported_types_fail_closed(self):
        self.metadata(status="library-approved")
        STORE.register_source(self.store, self.source)
        self.assertFalse(STORE.discover_components(self.harness)["assets"][0]["available"])
        with self.assertRaisesRegex(COMPONENT.ComponentError, "not accepted"):
            STORE.resolve_component(self.harness, str(self.source))
        self.metadata(asset_type="background")
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Unsupported asset type"):
            STORE.import_component(self.store, self.source)
        with self.assertRaisesRegex(COMPONENT.ComponentError, "Unsupported asset contract"):
            STORE.import_component(self.store, REPO / ".studio/backgrounds/rse-functional-background/4x3/v1")

    def test_acceptance_digest_and_runtime_are_verified_from_lock(self):
        acceptance = self.accept()
        source, _ = STORE.resolve_component(self.harness, self.ref)
        project = self.root / "project"
        project.mkdir()
        COMPONENT.install_component(source, project, self.binding(), acceptance=acceptance)
        path = project / "COMPONENT_LOCK.json"
        lock = json.loads(path.read_text())
        lock["components"][0]["acceptance"]["package_sha256"] = "0" * 64
        path.write_text(json.dumps(lock))
        with self.assertRaisesRegex(COMPONENT.ComponentError, "exact package"):
            COMPONENT.verify_installation(project)

    def test_cli_discovery_import_and_acceptance_do_not_require_current_work(self):
        import work as WORK
        environment = {"HYPERFRAMES_AI_CONFIG": "", "HYPERFRAMES_AI_WORK_ROOT": "", "HYPERFRAMES_AI_REVIEW": "0"}

        def command(*arguments, expected=0):
            output, errors = io.StringIO(), io.StringIO()
            with patch.dict(os.environ, environment), redirect_stdout(output), redirect_stderr(errors):
                self.assertEqual(expected, WORK.main(["component", *arguments], root=self.harness), errors.getvalue())
            return json.loads(output.getvalue()) if output.getvalue() else errors.getvalue()

        self.assertEqual(str(self.store), command("root")["asset_root"])
        command("source-add", str(self.source))
        command("validate", str(self.source), "--candidate")
        command("validate", self.ref, expected=2)
        candidate = command("import", str(self.source))
        command("accept", self.ref, "--sha256", candidate["package_sha256"],
                "--note", "Synthetic acceptance for CLI regression test")
        assets = command("list", "--query", "external-example")["assets"]
        self.assertTrue(any(asset["available"] for asset in assets))
        self.assertEqual(self.ref, command("validate", self.ref)["component_ref"])
        self.assertFalse((self.harness / "works").exists())


if __name__ == "__main__":
    unittest.main()
