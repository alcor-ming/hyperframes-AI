import json
import os
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import test_work_appearance as fixtures
import appearance
import appearance_rebind

cli = fixtures.cli


class AppearanceRebindTest(unittest.TestCase):
    asset = fixtures.WorkAppearanceTest.asset
    invoke = fixtures.WorkAppearanceTest.invoke

    def setUp(self):
        fixtures.WorkAppearanceTest.setUp(self)
        self.work_id = self.invoke("new", "Rebind", "--workflow", "hyperframes_video", "--account", "a")
        self.work, _ = cli.locate_work(self.root, self.work_id)
        self.variant = self.work / "variants/main"
        (self.variant / "project/index.html").write_text('<div id="S01">Keep approved text</div>')
        self.before = self.contents()

    def contents(self):
        return {p.relative_to(self.variant).as_posix(): p.read_bytes() for p in self.variant.rglob("*")
                if p.is_file() and ".runtime" not in p.relative_to(self.variant).parts}

    def update(self, *args):
        return json.loads(self.invoke("--work", self.work_id, "--variant", "main", "appearance", "rebind",
                                      "--background", "green@v1", *args))

    def test_preview_apply_history_acceptance_and_idempotency(self):
        state = cli.read_json(self.variant / "variant.yaml")
        state.update(accepted_visual_plan="plan-v001", accepted_preview="draft-v001", current_final="final.mp4")
        cli.write_variant(self.variant, state)
        for name in ("previews/plan-v001/source-snapshot/index.html", "previews/draft-v001/source-snapshot/index.html", "final/final.mp4"):
            path = self.variant / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"historical fixture, not generated video")
        before = self.contents()
        self.assertEqual("preview", self.update()["status"])
        self.assertEqual(before, self.contents())
        result = self.update("--apply")
        self.assertEqual("rebound", result["status"])
        after = cli.read_json(self.variant / "variant.yaml")
        self.assertEqual("main", after["id"])
        for field in ("accepted_visual_plan", "accepted_preview", "accepted_plan_revision", "accepted_script_revision", "current_final"):
            self.assertIsNone(after[field])
        self.assertEqual("final.mp4", after["appearance_history"][-1]["current_final"])
        for name, content in before.items():
            if name in ("SCRIPT.md", "project/index.html") or name.startswith(("previews/", "final/")):
                self.assertEqual(content, (self.variant / name).read_bytes())
        self.assertEqual(before["variant.yaml"], (Path(result["history"]) / "variant.yaml").read_bytes())
        appearance.verify(self.variant / "project", after["appearance_lock"])
        stable = self.contents()
        self.assertEqual("unchanged", self.update("--apply")["status"])
        self.assertEqual(stable, self.contents())

    def test_prepare_failure_and_unknown_runtime_do_not_touch_original(self):
        with patch.object(appearance, "materialize", side_effect=appearance.AppearanceError("injected second asset failure")):
            with self.assertRaisesRegex(appearance.AppearanceError, "injected"):
                self.update("--apply")
        self.assertEqual(self.before, self.contents())
        runtime = self.variant / "project/runtime/appearance.js"
        runtime.write_text("user-customized-runtime")
        before = self.contents()
        with self.assertRaisesRegex(appearance.AppearanceError, "user-modified"):
            self.update("--apply", "--upgrade-runtime")
        self.assertEqual(before, self.contents())

    def test_commit_failure_rolls_back_and_interruption_requires_recovery(self):
        plan = self.variant / "ANIMATION_PLAN.md"
        plan.write_bytes(plan.read_bytes().replace(b"\n", b"\r\n"))
        self.before = self.contents()
        write = cli.atomic_write
        count = 0

        def fail_once(path, text):
            nonlocal count
            if path == self.variant / "variant.yaml" and count == 0:
                count += 1
                raise OSError("injected variant write failure")
            return write(path, text)

        with patch.object(cli, "atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "injected"):
                self.update("--apply")
        self.assertEqual(self.before, self.contents())

        def interrupt(path, text):
            if path == self.variant / "variant.yaml":
                raise SystemExit("injected process exit")
            return write(path, text)

        with patch.object(cli, "atomic_write", side_effect=interrupt):
            with self.assertRaises(SystemExit):
                self.update("--apply")
        self.assertTrue(appearance_rebind.journal_path(self.variant).is_file())
        with self.assertRaisesRegex(cli.HarnessError, "recovery pending"):
            self.invoke("--work", self.work_id, "--variant", "main", "status")
        result = json.loads(self.invoke("--work", self.work_id, "--variant", "main", "appearance", "recover"))
        self.assertEqual("restored", result["status"])
        self.assertEqual(self.before, self.contents())

    def test_no_project_and_running_studio(self):
        shutil.rmtree(self.variant / "project")
        self.assertEqual("rebound", self.update("--apply")["status"])
        record = cli.studio_record(self.variant, "current")
        cli.write_json(record, {"pid": os.getpid()})
        with self.assertRaisesRegex(appearance.AppearanceError, "Stop"):
            self.invoke("--work", self.work_id, "--variant", "main", "appearance", "rebind", "--background", "white@v1", "--apply")

    def test_explicit_target_required_and_known_runtime_upgrade(self):
        preview = self.update("--ratio", "9:16")
        self.assertEqual(1080, preview["changes"]["width"]["after"])
        self.assertEqual(1920, preview["changes"]["height"]["after"])
        with self.assertRaisesRegex(appearance.AppearanceError, "explicit"):
            self.invoke("appearance", "rebind", "--background", "green@v1", "--apply")
        runtime = self.variant / "project/runtime/appearance.js"
        runtime.write_text("known-old-fixture")
        with patch.object(appearance_rebind, "KNOWN_RUNTIMES", {cli.file_sha256(runtime)}):
            with self.assertRaisesRegex(appearance.AppearanceError, "upgrade-runtime"):
                self.update("--apply")
            self.assertTrue(self.update("--apply", "--upgrade-runtime")["runtime_upgrade"])
        self.assertEqual((Path(appearance.__file__).parent / "runtime/appearance.js").read_bytes(), runtime.read_bytes())


if __name__ == "__main__":
    unittest.main()
