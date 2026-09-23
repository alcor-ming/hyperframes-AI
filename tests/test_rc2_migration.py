from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / ".studio"))
from importlib import import_module


WORK = import_module("work")
MIGRATION = import_module("work_migration")


class Rc2MigrationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / ".studio" / ".runtime").mkdir(parents=True)
        for location in ("active", "parked", "archive/2026-09"):
            (self.root / "works" / location).mkdir(parents=True)

    def work(self, location, identifier, title, **metadata):
        path = self.root / "works" / location / identifier
        path.mkdir()
        data = {"id": identifier, "title": title, "workflow": "hyperframes_video", "purpose": "standard",
                "series": "alpha", "created_at": "2026-01-01T00:00:00"} | metadata
        (path / "WORK.md").write_text(
            "---\n" + json.dumps(data, ensure_ascii=False) + "\n---\n\n# " + title + "\n\nBody.\n",
            encoding="utf-8")
        variant = path / "variants" / "main"
        variant.mkdir(parents=True)
        (variant / "variant.yaml").write_text('{"id":"main","status":"active"}\n', encoding="utf-8")
        return path

    def studio_session(self, work, pid, **changes):
        return {"pid": pid, "work": work.name, "variant": "main", "target": "current",
                "project": str(work / "variants/main/project"), "kind": "executable",
                "port": 4321, "cli_sha256": "a" * 64} | changes

    def test_dry_run_apply_and_retry_preserve_frozen_files(self):
        first = self.work("active", "work-hyperframes_video-001", "001-第一期")
        second = self.work("parked", "work-hyperframes_video-002", "002-第二期",
                           source_work="work-hyperframes_video-001")
        third = self.work("archive/2026-09", "work-hyperframes_video-003", "003-第三期")
        deleted = "work-hyperframes_video-004"
        frozen = first / "variants" / "main" / "previews" / "draft-v001" / "source-snapshot"
        frozen.mkdir(parents=True)
        (frozen / "WORK.md").write_text("old frozen identity", encoding="utf-8")
        (first / "variants" / "main" / "final").mkdir(parents=True)
        (first / "variants" / "main" / "final" / "old.mp4").write_bytes(b"final")
        (first / "variants" / "main" / "project" / "vendor").mkdir(parents=True)
        (first / "variants" / "main" / "project" / "vendor" / "asset.js").write_bytes(b"vendor")
        studio = first / "variants" / "main" / ".runtime"
        studio.mkdir(parents=True)
        (studio / "studio-current.json").write_text(json.dumps(
            self.studio_session(first, 99999999, stopped_at="2026-09-01")), encoding="utf-8")
        WORK.write_pointer(self.root, "current-work", first.name)
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertEqual([], plan["blockers"])
        self.assertEqual([1, 2, 3], [row["series_number"] for row in plan["targets"]])
        self.assertTrue(first.is_dir())
        self.assertFalse((self.root / ".studio" / ".runtime" / MIGRATION.JOURNAL).exists())
        actual_write = WORK.atomic_write
        writes = 0

        def interrupted(path, content):
            nonlocal writes
            writes += 1
            if writes == 3:
                raise OSError("simulated interruption")
            return actual_write(path, content)

        with mock.patch.object(WORK, "atomic_write", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "simulated interruption"):
                MIGRATION.apply_plan(self.root, plan, WORK)
        self.assertTrue((self.root / ".studio" / ".runtime" / MIGRATION.JOURNAL).is_file())
        MIGRATION.apply_plan(self.root, plan, WORK)
        self.assertFalse((self.root / ".studio" / ".runtime" / MIGRATION.JOURNAL).exists())
        names = [item["new_id"] for item in plan["targets"]]
        self.assertEqual(names[0], WORK.read_pointer(self.root, "current-work"))
        self.assertEqual(names[0], WORK.locate_work(self.root, "work-hyperframes_video-001")[0].name)
        self.assertEqual(names[0], WORK.read_frontmatter(self.root / "works" / "parked" / names[1] / "WORK.md")["source_work"])
        self.assertEqual("第一期", WORK.read_frontmatter(self.root / "works" / "active" / names[0] / "WORK.md")["title"])
        self.assertEqual("old frozen identity", (self.root / "works" / "active" / names[0] / frozen.relative_to(first) / "WORK.md").read_text())
        self.assertEqual(b"final", (self.root / "works" / "active" / names[0] / "variants/main/final/old.mp4").read_bytes())
        self.assertEqual(b"vendor", (self.root / "works" / "active" / names[0] / "variants/main/project/vendor/asset.js").read_bytes())
        record = WORK.read_json(self.root / "works" / "active" / names[0] / "variants/main/.runtime/studio-current.json")
        self.assertEqual(names[0], record["work"])
        self.assertIn(names[0], record["project"])
        self.assertFalse(any(deleted in item.name for item in (self.root / "works").rglob("*")))
        self.assertEqual([], MIGRATION.build_plan(self.root, WORK)["operations"])
        WORK.write_pointer(self.root, "current-work", names[1])
        self.assertEqual({"migrated": 0, "numbered": 0, "applied": False}, MIGRATION.apply_plan(self.root, plan, WORK))
        self.assertEqual(names[1], WORK.read_pointer(self.root, "current-work"))

    def test_drift_and_unresolved_title_block_before_rename(self):
        work = self.work("active", "work-hyperframes_video-027", "999-自定义")
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("Title number does not match", " ".join(plan["blockers"]))
        with self.assertRaises(MIGRATION.MigrationError):
            MIGRATION.apply_plan(self.root, plan, WORK)
        resolved = MIGRATION.build_plan(self.root, WORK, title_overrides={work.name: "自定义"})
        self.assertEqual([], resolved["blockers"])
        (work / "WORK.md").write_text((work / "WORK.md").read_text() + "edit", encoding="utf-8")
        with self.assertRaisesRegex(MIGRATION.MigrationError, "input changed"):
            MIGRATION.apply_plan(self.root, resolved, WORK)
        self.assertTrue(work.is_dir())

    def test_pending_request_and_live_studio_are_reported(self):
        work = self.work("active", "work-hyperframes_video-001", "001-第一期")
        request = self.root / "requests" / "q1" / "r001"
        request.mkdir(parents=True)
        (request / "request.json").write_text(json.dumps({"work": work.name, "revision": 1}), encoding="utf-8")
        studio = work / "variants" / "main" / ".runtime"
        studio.mkdir(parents=True)
        (studio / "studio-current.json").write_text(json.dumps(
            self.studio_session(work, os.getpid())), encoding="utf-8")
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("request.json", " ".join(plan["blockers"]))
        self.assertIn("studio-current.json", " ".join(plan["blockers"]))
        with self.assertRaises(MIGRATION.MigrationError):
            MIGRATION.apply_plan(self.root, plan, WORK)
        self.assertTrue(work.exists())

    def test_historical_qa_reports_are_not_sessions_or_rewritten(self):
        work = self.work("active", "work-hyperframes_video-019", "019-QA")
        runtime = work / "variants/main/.runtime"
        runtime.mkdir()
        reports = {
            "studio-initial.json": {"url": "http://localhost", "errors": [], "dnt": [],
                                    "frames": [], "buttons": []},
            "studio-qa.json": {"errors": [], "dnt": [], "initial": {}, "samples": [],
                               "emphasis": [], "playing": {}, "paused": {}, "pausedLater": {}, "lint": []},
        }
        originals = {}
        for name, report in reports.items():
            path = runtime / name
            path.write_bytes(json.dumps(report, indent=1).encode("utf-8") + b"\n")
            originals[name] = path.read_bytes()
        source = work / "variants/main/delegation/S05-QA.md"
        source.parent.mkdir()
        source.write_text("../.runtime/studio-qa.json\n", encoding="utf-8")
        before = {path.relative_to(self.root): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertEqual([], plan["blockers"])
        self.assertEqual(before, {path.relative_to(self.root): path.read_bytes()
                                  for path in self.root.rglob("*") if path.is_file()})
        self.assertFalse(any("studio-qa.json" in op["path"] or "studio-initial.json" in op["path"]
                             for op in plan["operations"]))
        MIGRATION.apply_plan(self.root, plan, WORK)
        migrated = self.root / plan["targets"][0]["new_path"]
        for name, original in originals.items():
            self.assertEqual(original, (migrated / "variants/main/.runtime" / name).read_bytes())
        self.assertEqual("../.runtime/studio-qa.json\n", (migrated / source.relative_to(work)).read_text())
        self.assertEqual({"migrated": 0, "numbered": 0, "applied": False},
                         MIGRATION.apply_plan(self.root, plan, WORK))

    def test_incomplete_qa_like_record_still_blocks(self):
        work = self.work("active", "work-hyperframes_video-019", "019-QA")
        runtime = work / "variants/main/.runtime"
        runtime.mkdir()
        path = runtime / "studio-initial.json"
        path.write_text(json.dumps({"url": "http://localhost", "errors": [], "frames": [], "buttons": []}),
                        encoding="utf-8")
        self.assertIn(str(path), " ".join(MIGRATION.build_plan(self.root, WORK)["blockers"]))

    def test_stopped_scene_session_copy_is_preserved_only_when_canonical_matches(self):
        work = self.work("active", "work-hyperframes_video-019", "019-Session")
        runtime = work / "variants/main/.runtime"
        runtime.mkdir()
        session = self.studio_session(work, 43210, target="plan-v008", opened_at="later")
        canonical = runtime / "studio-plan-v008.json"
        canonical.write_text(json.dumps(session), encoding="utf-8")
        copy = runtime / "studio-s05-session.json"
        copy.write_text(json.dumps(session | {"opened_at": "earlier"}, indent=1), encoding="utf-8")
        original = copy.read_bytes()
        with mock.patch.object(WORK.storage, "process_stopped", return_value=True):
            plan = MIGRATION.build_plan(self.root, WORK)
            self.assertEqual([], plan["blockers"])
            self.assertFalse(any(op["path"].endswith("studio-s05-session.json") for op in plan["operations"]))
            actual_write = WORK.atomic_write
            writes = 0

            def interrupted(path, content):
                nonlocal writes
                writes += 1
                if writes == 4:
                    raise OSError("simulated interruption after session rewrite")
                return actual_write(path, content)

            with mock.patch.object(WORK, "atomic_write", side_effect=interrupted):
                with self.assertRaisesRegex(OSError, "simulated interruption"):
                    MIGRATION.apply_plan(self.root, plan, WORK)
            MIGRATION.apply_plan(self.root, plan, WORK)
        migrated = self.root / plan["targets"][0]["new_path"] / "variants/main/.runtime"
        self.assertEqual(original, (migrated / copy.name).read_bytes())
        self.assertEqual(plan["targets"][0]["new_id"], WORK.read_json(migrated / canonical.name)["work"])

    def test_unmatched_scene_session_copy_still_blocks(self):
        work = self.work("active", "work-hyperframes_video-019", "019-Session")
        runtime = work / "variants/main/.runtime"
        runtime.mkdir()
        session = self.studio_session(work, 43210, target="plan-v008", opened_at="later")
        (runtime / "studio-plan-v008.json").write_text(json.dumps(session), encoding="utf-8")
        copy = runtime / "studio-s05-session.json"
        for changes in ({"cli_sha256": "b" * 64}, {"project": str(self.root / "other")},
                        {"work": "work-hyperframes_video-999"}):
            with self.subTest(changes=changes):
                copy.write_text(json.dumps(session | changes), encoding="utf-8")
                with mock.patch.object(WORK.storage, "process_stopped", return_value=True):
                    self.assertIn(str(copy), " ".join(MIGRATION.build_plan(self.root, WORK)["blockers"]))

    def test_only_valid_stopped_sessions_can_be_rewritten(self):
        work = self.work("active", "work-hyperframes_video-019", "019-Session")
        runtime = work / "variants/main/.runtime"
        runtime.mkdir()
        path = runtime / "studio-current.json"
        valid = self.studio_session(work, 43210)
        cases = [
            ("running", valid, False),
            ("missing pid", {key: value for key, value in valid.items() if key != "pid"} | {"stopped_at": "now"}, False),
            ("invalid pid", valid | {"pid": "43210", "stopped_at": "now"}, False),
            ("unknown record", {"unknown": "report"}, False),
            ("incomplete session", {"pid": 43210, "work": work.name, "stopped_at": "now"}, False),
            ("stopped marker", valid | {"stopped_at": "now"}, True),
            ("stopped process", valid, True),
        ]
        for label, record, allowed in cases:
            with self.subTest(label=label):
                path.write_text(json.dumps(record), encoding="utf-8")
                with mock.patch.object(WORK.storage, "process_stopped", return_value=allowed):
                    plan = MIGRATION.build_plan(self.root, WORK)
                self.assertEqual(allowed, not plan["blockers"])
                self.assertEqual(allowed, any(op["kind"] == "studio" for op in plan["operations"]))
        for contents in ("{broken", "[]"):
            path.write_text(contents, encoding="utf-8")
            self.assertIn(str(path), " ".join(MIGRATION.build_plan(self.root, WORK)["blockers"]))
        path.write_text(json.dumps(valid), encoding="utf-8")
        with mock.patch.object(WORK, "read_json", side_effect=OSError("access denied")):
            self.assertIn(str(path), " ".join(MIGRATION._studio_records(work, WORK)[1]))

    def test_accepted_delivery_does_not_hide_another_pending_review(self):
        work = self.work("active", "work-hyperframes_video-001", "001-第一期")
        request = self.root / "requests" / "q1" / "r001"
        request.mkdir(parents=True)
        (request / "request.json").write_text(json.dumps({"work": work.name, "revision": 1}), encoding="utf-8")
        deliveries = request.parent / "deliveries"
        for identity in ("a", "b"):
            path = deliveries / identity
            path.mkdir(parents=True)
            (path / "delivery.json").write_text(json.dumps({"revision": 1, "delivery_id": identity}), encoding="utf-8")
        decisions = request.parent / "decisions"
        decisions.mkdir()
        (decisions / "a.json").write_text(json.dumps({"revision": 1, "delivery_id": "a", "decision": "accepted"}), encoding="utf-8")
        review = self.root / "review" / "q1-r001-b" / ".runtime"
        review.mkdir(parents=True)
        (review / "review.json").write_text(json.dumps({"work": work.name, "request_id": "q1",
                                                       "revision": 1, "delivery_id": "b"}), encoding="utf-8")
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("deliveries/b/delivery.json", " ".join(plan["blockers"]))
        self.assertIn("review.json", " ".join(plan["blockers"]))

    def test_missing_purpose_requires_explicit_override(self):
        work = self.work("active", "work-hyperframes_video-001", "001-第一期")
        metadata = WORK.read_frontmatter(work / "WORK.md")
        metadata.pop("purpose")
        WORK.atomic_write(work / "WORK.md", "---\n" + json.dumps(metadata, ensure_ascii=False)
                          + "\n---\n" + WORK.document_body(work / "WORK.md"))
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("purpose missing", " ".join(plan["blockers"]))
        with self.assertRaises(MIGRATION.MigrationError):
            MIGRATION.apply_plan(self.root, plan, WORK)
        resolved = MIGRATION.build_plan(self.root, WORK, purpose_overrides={work.name: "ip"})
        self.assertEqual([], resolved["blockers"])
        MIGRATION.apply_plan(self.root, resolved, WORK)
        new = self.root / resolved["targets"][0]["new_path"]
        self.assertEqual("ip", WORK.read_frontmatter(new / "WORK.md")["purpose"])

    def test_heading_mismatch_and_occupied_symlink_require_resolution(self):
        work = self.work("active", "work-hyperframes_video-027", "027-旧标题")
        source = (work / "WORK.md").read_text(encoding="utf-8")
        (work / "WORK.md").write_text(source.replace("# 027-旧标题", "# 自定义标题"), encoding="utf-8")
        target = work.with_name("work-hyperframes_video-027-新标题")
        target.symlink_to(self.root / "missing-target", target_is_directory=True)
        plan = MIGRATION.build_plan(self.root, WORK, title_overrides={work.name: "新标题"})
        self.assertIn("Target path already exists", " ".join(plan["blockers"]))
        target.unlink()
        ambiguous = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("H1 differs", " ".join(ambiguous["blockers"]))
        resolved = MIGRATION.build_plan(self.root, WORK, title_overrides={work.name: "新标题"})
        self.assertEqual([], resolved["blockers"])
        MIGRATION.apply_plan(self.root, resolved, WORK)
        self.assertIn("# 新标题", (target / "WORK.md").read_text(encoding="utf-8"))

    def test_unrelated_series_can_migrate_while_one_work_is_blocked(self):
        blocked = self.work("active", "work-hyperframes_video-001", "999-含糊")
        safe = self.work("active", "work-hyperframes_video-002", "002-可迁移", series="beta")
        full = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("Title number does not match", " ".join(full["blockers"]))
        partial = MIGRATION.build_plan(self.root, WORK, only_ids=[safe.name])
        self.assertEqual([], partial["blockers"])
        MIGRATION.apply_plan(self.root, partial, WORK)
        self.assertTrue(blocked.is_dir())
        self.assertEqual(1, WORK.read_frontmatter(WORK.locate_work(self.root, safe.name)[0] / "WORK.md")["series_number"])
        fixed = MIGRATION.build_plan(self.root, WORK, only_ids=[blocked.name],
                                     title_overrides={blocked.name: "含糊"})
        self.assertEqual([], fixed["blockers"])
        MIGRATION.apply_plan(self.root, fixed, WORK)
        self.assertEqual(1, WORK.read_frontmatter(WORK.locate_work(self.root, blocked.name)[0] / "WORK.md")["series_number"])

    def test_partial_migration_keeps_series_order(self):
        first = self.work("active", "work-hyperframes_video-001", "001-第一期")
        later = self.work("active", "work-hyperframes_video-002", "002-第二期")
        out_of_order = MIGRATION.build_plan(self.root, WORK, only_ids=[later.name])
        self.assertIn("Earlier unselected Work", " ".join(out_of_order["blockers"]))
        first_plan = MIGRATION.build_plan(self.root, WORK, only_ids=[first.name])
        MIGRATION.apply_plan(self.root, first_plan, WORK)
        second_plan = MIGRATION.build_plan(self.root, WORK, only_ids=[later.name])
        self.assertEqual([], second_plan["blockers"])
        MIGRATION.apply_plan(self.root, second_plan, WORK)
        self.assertEqual(2, WORK.read_frontmatter(WORK.locate_work(self.root, later.name)[0] / "WORK.md")["series_number"])


if __name__ == "__main__":
    unittest.main()
