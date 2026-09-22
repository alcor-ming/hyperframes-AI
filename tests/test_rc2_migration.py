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
        (studio / "studio-current.json").write_text(json.dumps({
            "pid": 99999999, "stopped_at": "2026-09-01", "work": first.name,
            "project": str(first / "variants" / "main" / "project")}), encoding="utf-8")
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
        (studio / "studio-current.json").write_text(json.dumps({"pid": os.getpid(), "work": work.name}), encoding="utf-8")
        plan = MIGRATION.build_plan(self.root, WORK)
        self.assertIn("request.json", " ".join(plan["blockers"]))
        self.assertIn("studio-current.json", " ".join(plan["blockers"]))
        with self.assertRaises(MIGRATION.MigrationError):
            MIGRATION.apply_plan(self.root, plan, WORK)
        self.assertTrue(work.exists())

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
