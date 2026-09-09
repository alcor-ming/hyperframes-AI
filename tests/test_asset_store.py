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
