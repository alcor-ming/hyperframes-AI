from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from test_work_cli import REPO, WORK_CLI as cli
import appearance
import asset_store


class WorkAppearanceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "harness"
        self.store = self.base / "store"
        shutil.copytree(REPO / ".studio/templates", self.root / ".studio/templates")
        environment = mock.patch.dict(os.environ, {"HYPERFRAMES_AI_ASSET_ROOT": str(self.store),
            "HYPERFRAMES_AI_ASSET_CONFIG": str(self.base / "assets.json"), "HYPERFRAMES_AI_REVIEW": "0"})
        environment.start()
        self.addCleanup(environment.stop)
        self.theme = self.asset("paper", "theme", {"tokens": {"colors": {"text": "#121212"}}})
        self.white = self.asset("white", "background", {"renderer": "solid", "parameters": {"color": "#ffffff"}})
        self.green = self.asset("green", "background", {"renderer": "solid", "parameters": {"color": "#c0e0d0"}})
        self.account = {"name": "Fixture", "theme": self.theme, "background": self.white}
        cli.account_service(self.root).put("account", "a", self.account)

    def asset(self, identity, kind, payload):
        source = self.base / identity
        source.mkdir()
        (source / "asset.json").write_text(json.dumps({"schema_version": 2, "contract_version": 1,
            "id": identity, "kind": kind, "version": 1, "entry": "preset.json", "parameters": {}, "compatibility": {}}))
        (source / "preset.json").write_text(json.dumps(payload))
        candidate = asset_store.pack_source(self.store, source)
        asset_store.accept_component(self.store, candidate["component_ref"], candidate["package_sha256"],
                                     "Synthetic isolated test", runtime_root=self.root)
        return {"ref": candidate["component_ref"], "kind": kind, "package_sha256": candidate["package_sha256"]}

    def invoke(self, *arguments):
        args = cli.build_parser().parse_args(arguments)
        with redirect_stdout(io.StringIO()) as output:
            args.handler(self.root, args)
        return output.getvalue().strip()

    def test_independent_selection_freezes_and_replays_without_store(self):
        resolved = json.loads(self.invoke("appearance", "resolve", "--account", "a", "--background", "green@v1",
                                         "--mode", "animation-led", "--seed", "0"))
        self.assertEqual(resolved["selection"]["theme"], self.theme)
        self.assertEqual(resolved["selection"]["background"], self.green)
        self.assertFalse((self.root / "works").exists())
        work_id = self.invoke("new", "Fixture", "--workflow", "hyperframes_video", "--account", "a")
        work, _ = cli.locate_work(self.root, work_id)
        variant = work / "variants/main"
        state = cli.read_json(variant / "variant.yaml")
        original = (variant / "variant.yaml").read_bytes()
        cli.account_service(self.root).put("account", "a", {**self.account, "background": self.green, "mode": "animation-led"})
        self.assertEqual(original, (variant / "variant.yaml").read_bytes())
        self.assertEqual(1, state["account_revision"])
        self.assertEqual("main", state["id"])
        shutil.rmtree(self.store)
        appearance.verify(variant / "project", state["appearance_lock"])

    def test_creation_failure_preserves_current_and_has_no_half_variant(self):
        work_id = self.invoke("new", "Good", "--workflow", "hyperframes_video", "--account", "a")
        before = self.invoke("current")
        work, _ = cli.locate_work(self.root, work_id)
        cli.account_service(self.root).put("account", "b", self.account)
        with mock.patch.object(appearance, "materialize", side_effect=appearance.AppearanceError("changed while freezing")):
            with self.assertRaisesRegex(appearance.AppearanceError, "changed while freezing"):
                self.invoke("new", "Bad", "--workflow", "hyperframes_video", "--account", "b")
            with self.assertRaisesRegex(appearance.AppearanceError, "changed while freezing"):
                self.invoke("variant", "add", "bad", "--account", "b")
        self.assertEqual(before, self.invoke("current"))
        self.assertEqual(["main"], [path.name for path in cli.variant_paths(work)])
        self.assertEqual([work_id], [row["id"] for row in cli.list_work_rows(self.root)])
        self.assertFalse(list(work.parent.glob(".pending-*")))
        self.assertFalse(list((work / "variants").glob(".pending-*")))

    def test_source_ratio_freezes_concrete_dimensions(self):
        choices = self.base / "appearance.json"
        choices.write_text(json.dumps({"ratio": "source", "width": 1200, "height": 1200}))
        identity = self.invoke("new", "Square", "--workflow", "hyperframes_video", "--account", "a",
                               "--appearance-file", str(choices))
        work, _ = cli.locate_work(self.root, identity)
        state = cli.read_json(work / "variants/main/variant.yaml")
        self.assertEqual("1:1", state["ratio"])
        self.assertEqual(1200, state["appearance_lock"]["width"])

    def test_explicit_snapshot_closure_keeps_appearance_and_detects_changes(self):
        identity = self.invoke("new", "Snapshot", "--workflow", "hyperframes_video", "--account", "a")
        work, _ = cli.locate_work(self.root, identity)
        variant = work / "variants/main"
        project = variant / "project"
        state = cli.read_json(variant / "variant.yaml")
        (project / "index.html").write_text("<html><body>Card</body></html>")
        (project / "DESIGN.md").write_text("Synthetic card")
        (project / "project-config.json").write_text('{"snapshot_dependencies":[]}')
        before = cli.snapshot_digest(project)
        snapshot = self.base / "snapshot"
        cli.copy_snapshot(project, snapshot)
        cli.validate_snapshot_closure(project, snapshot)
        appearance.verify(snapshot, state["appearance_lock"])
        self.assertIn("appearance-lock.json", cli.snapshot_items(project))
        self.assertTrue(any(name.startswith("vendor/components/") for name in cli.snapshot_items(project)))
        (project / "appearance-lock.json").write_text("{}")
        self.assertNotEqual(before, cli.snapshot_digest(project))
        with self.assertRaises(appearance.AppearanceError):
            appearance.verify(project, state["appearance_lock"])


if __name__ == "__main__":
    unittest.main()
