from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("work_cli", REPO / ".studio" / "work.py")
assert SPEC and SPEC.loader
WORK_CLI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORK_CLI)


class WorkCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / ".studio").mkdir()
        shutil.copytree(REPO / ".studio" / "templates", self.root / ".studio" / "templates")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, *arguments: str, expected: int = 0) -> str:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = WORK_CLI.main(list(arguments), root=self.root)
        self.assertEqual(expected, result, stderr.getvalue())
        return stdout.getvalue().strip() or stderr.getvalue().strip()

    def new_work(self, title: str = "Test Work", workflow: str = "hyperframes_video") -> tuple[str, Path]:
        work_id = self.invoke("new", title, "--workflow", workflow)
        return work_id, self.root / "works" / "active" / work_id

    def prepare_package_final(self, name: str = "quote-final", marker: bytes = b"one") -> Path:
        directory = self.root / name
        directory.mkdir()
        artifacts = []
        for index in range(1, 4):
            path = directory / f"{index:02d}.jpg"
            path.write_bytes(marker + str(index).encode())
            artifacts.append({"path": path.name, "role": "image", "sha256": WORK_CLI.file_sha256(path)})
        contact = directory / "final_contact_sheet.jpg"
        contact.write_bytes(b"contact-" + marker)
        artifacts.append({"path": contact.name, "role": "contact_sheet", "sha256": WORK_CLI.file_sha256(contact)})
        package = directory / "PACKAGE.md"
        package.write_text("# Package\n", encoding="utf-8")
        artifacts.append({"path": package.name, "role": "package", "sha256": WORK_CLI.file_sha256(package)})
        (directory / "manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "workflow": "podcast_quote_image",
                    "qa": "passed",
                    "artifacts": artifacts,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return directory

    @staticmethod
    def update_frontmatter(path: Path, **updates: object) -> None:
        lines = path.read_text(encoding="utf-8").splitlines()
        end = lines.index("---", 1)
        data = json.loads("\n".join(lines[1:end]))
        data.update(updates)
        path.write_text(
            "---\n" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n---\n" + "\n".join(lines[end + 1 :]) + "\n",
            encoding="utf-8",
        )

    def prepare_preview(self, work: Path, variant_id: str = "main", content: bytes = b"draft") -> Path:
        variant = work / "variants" / variant_id
        self.update_frontmatter(variant / "ANIMATION_PLAN.md", status="approved")
        self.update_frontmatter(variant / "RESEARCH.md", status="ready")
        project = variant / "project"
        (project / "index.html").write_text("<html></html>", encoding="utf-8")
        (project / "compositions").mkdir(exist_ok=True)
        (project / "compositions" / "main.html").write_text("<section id='S01'></section>", encoding="utf-8")
        (project / "DESIGN.md").write_text("# Design\n", encoding="utf-8")
        (project / "project-config.json").write_text("{}\n", encoding="utf-8")
        (project / "node_modules").mkdir(exist_ok=True)
        (project / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
        draft = self.root / f"{variant_id}-draft.mp4"
        draft.write_bytes(content)
        return draft

    def test_new_variant_and_status(self) -> None:
        work_id, work = self.new_work("中文标题")
        self.assertTrue((work / "variants" / "main" / "SCRIPT.md").is_file())
        self.assertTrue((work / "variants" / "main" / "RESEARCH.md").is_file())
        self.assertEqual("9:16", json.loads((work / "variants" / "main" / "variant.yaml").read_text())["ratio"])
        package = (work / "variants" / "main" / "PACKAGE.md").read_text(encoding="utf-8")
        self.assertIn("## 标题", package)
        self.assertIn("## 封面文字", package)
        self.assertIn("## 一句话", package)
        self.assertEqual(work_id, (self.root / ".studio" / ".runtime" / "current-work").read_text().strip())
        self.assertEqual("hyperframes_video", WORK_CLI.read_frontmatter(work / "WORK.md")["workflow"])

        script = work / "variants" / "main" / "SCRIPT.md"
        script.write_text(script.read_text(encoding="utf-8") + "正文\n", encoding="utf-8")
        self.update_frontmatter(script, revision=2)
        self.update_frontmatter(work / "variants" / "main" / "RESEARCH.md", status="ready", revision=3, script_revision=2)
        self.invoke("variant", "add", "douyin-9x16", "--from", "main", "--profile", "kami_editorial")
        copied_variant = work / "variants" / "douyin-9x16"
        copied = copied_variant / "SCRIPT.md"
        self.assertIn("正文", copied.read_text(encoding="utf-8"))
        self.assertEqual(2, json.loads((copied_variant / "variant.yaml").read_text())["script_revision"])
        self.assertEqual(3, WORK_CLI.read_frontmatter(copied_variant / "ANIMATION_PLAN.md")["research_revision"])
        self.assertEqual("ready", WORK_CLI.read_frontmatter(copied_variant / "RESEARCH.md")["status"])
        status = json.loads(self.invoke("status"))
        self.assertEqual("douyin-9x16", status["variant"]["id"])

    def test_workflow_is_required_and_podcast_init_is_content_specific(self) -> None:
        with self.assertRaises(SystemExit):
            WORK_CLI.main(["new", "Missing workflow"], root=self.root)

        work_id, work = self.new_work("Podcast quotes", "podcast_quote_image")
        variant = work / "variants" / "main"
        self.assertEqual("podcast_quote_image", WORK_CLI.read_frontmatter(work / "WORK.md")["workflow"])
        self.assertEqual("3:4", json.loads((variant / "variant.yaml").read_text())["ratio"])
        self.assertTrue((variant / "materials").is_dir())
        self.assertTrue((variant / "artifacts").is_dir())
        self.assertTrue((variant / "frames").is_dir())
        self.assertTrue((variant / "render").is_dir())
        self.assertTrue((variant / "PACKAGE.md").is_file())
        self.assertFalse((variant / "SCRIPT.md").exists())
        self.assertFalse((variant / "ANIMATION_PLAN.md").exists())
        self.assertEqual(work_id, json.loads(self.invoke("list"))[0]["id"])

        result = self.invoke("preview", "register", str(self.root / "missing.mp4"), expected=2)
        self.assertIn("requires workflow hyperframes_video", result)

    def test_podcast_workflow_rejects_video_options_before_creation(self) -> None:
        result = self.invoke(
            "new",
            "Wrong options",
            "--workflow",
            "podcast_quote_image",
            "--ratio",
            "9:16",
            expected=2,
        )
        self.assertIn("does not accept video", result)
        self.assertFalse((self.root / "works").exists())

    def test_legacy_archive_directory_is_ignored(self) -> None:
        (self.root / "works" / "archive" / "tasks" / "001-legacy").mkdir(parents=True)
        self.assertEqual([], json.loads(self.invoke("list")))
        self.new_work()

    def test_wait_park_resume_archive_and_reopen(self) -> None:
        work_id, work = self.new_work()
        self.invoke("wait", "voiceover")
        state = json.loads((work / "variants" / "main" / "variant.yaml").read_text())
        self.assertEqual("waiting_asset", state["status"])

        self.invoke("park")
        parked = self.root / "works" / "parked" / work_id
        self.assertTrue(parked.is_dir())
        self.invoke("resume")
        self.assertTrue(work.is_dir())
        state = json.loads((work / "variants" / "main" / "variant.yaml").read_text())
        self.assertEqual("waiting_asset", state["status"])

        archived_path = Path(self.invoke("archive", "--outcome", "abandoned"))
        self.assertTrue(archived_path.is_dir())
        reopened_path = Path(self.invoke("reopen", work_id))
        self.assertEqual(work, reopened_path)
        self.assertTrue((work / ".runtime" / "archive-history.json").is_file())

    def test_preview_registration_is_approved_snapshot_and_idempotent(self) -> None:
        _, work = self.new_work()
        draft = self.prepare_preview(work)
        variant = work / "variants" / "main"

        draft_id = self.invoke("preview", "register", str(draft))
        self.assertEqual("draft-v001", draft_id)
        self.assertEqual(draft_id, self.invoke("preview", "register", str(draft)))
        snapshot = variant / "previews" / draft_id / "source-snapshot"
        self.assertTrue((snapshot / "compositions" / "main.html").is_file())
        self.assertFalse((snapshot / "node_modules").exists())

        self.invoke("preview", "accept", draft_id)
        state = json.loads((variant / "variant.yaml").read_text())
        self.assertEqual(draft_id, state["accepted_preview"])
        self.assertEqual(1, state["accepted_plan_revision"])

        state["plan_revision"] = 2
        (variant / "variant.yaml").write_text(json.dumps(state), encoding="utf-8")
        result = self.invoke("preview", "accept", draft_id, expected=2)
        self.assertIn("different Plan revision", result)

    def test_preview_rejects_unapproved_plan(self) -> None:
        _, work = self.new_work()
        variant = work / "variants" / "main"
        draft = self.root / "draft.mp4"
        draft.write_bytes(b"draft")
        result = self.invoke("preview", "register", str(draft), expected=2)
        self.assertIn("not approved", result)
        self.assertFalse((variant / "previews" / "draft-v001").exists())

    def test_preview_rejects_stale_research(self) -> None:
        _, work = self.new_work()
        variant = work / "variants" / "main"
        self.update_frontmatter(variant / "ANIMATION_PLAN.md", status="approved")
        draft = self.root / "draft.mp4"
        draft.write_bytes(b"draft")
        result = self.invoke("preview", "register", str(draft), expected=2)
        self.assertIn("RESEARCH.md is not ready", result)
        self.assertFalse((variant / "previews" / "draft-v001").exists())

    def test_finalize_recovers_archive_and_rotates_history(self) -> None:
        work_id, work = self.new_work()
        draft = self.prepare_preview(work)
        self.invoke("preview", "register", str(draft))
        self.invoke("preview", "accept", "draft-v001")
        final_one = self.root / "final-one.mp4"
        final_one.write_bytes(b"final-one")

        with mock.patch.object(WORK_CLI, "move_to_archive", side_effect=OSError("simulated")):
            result = self.invoke("finalize", str(final_one), "--qa-passed", expected=2)
        self.assertIn("archive is pending", result)
        self.assertEqual(b"final-one", (work / "variants" / "main" / "final" / "final.mp4").read_bytes())
        manifest_path = work / "variants" / "main" / "final" / "manifest.json"
        first_manifest = manifest_path.read_bytes()

        archived_final = Path(self.invoke("finalize", str(final_one), "--qa-passed"))
        self.assertTrue(archived_final.is_file())
        self.assertIn("/archive/", archived_final.as_posix())
        self.assertEqual(first_manifest, (archived_final.parent / "manifest.json").read_bytes())
        self.assertEqual(str(archived_final), self.invoke("--work", work_id, "finalize", str(final_one), "--qa-passed"))

        self.invoke("reopen", work_id)
        final_two = self.root / "final-two.mp4"
        final_two.write_bytes(b"final-two")
        second = Path(self.invoke("finalize", str(final_two), "--qa-passed"))
        history = second.parent / "history" / "final-v001.mp4"
        self.assertEqual(b"final-one", history.read_bytes())
        self.assertEqual(b"final-two", second.read_bytes())

    def test_required_variants_delay_auto_archive(self) -> None:
        work_id, work = self.new_work()
        self.invoke("variant", "add", "bilibili-16x9", "--from", "main", "--ratio", "16:9")
        self.update_frontmatter(work / "WORK.md", required_variants=["main", "bilibili-16x9"])

        for variant_id in ("main", "bilibili-16x9"):
            self.invoke("variant", "use", variant_id)
            draft = self.prepare_preview(work, variant_id, content=variant_id.encode())
            self.invoke("preview", "register", str(draft))
            self.invoke("preview", "accept", "draft-v001")
            final = self.root / f"{variant_id}-final.mp4"
            final.write_bytes((variant_id + "-final").encode())
            output = Path(self.invoke("finalize", str(final), "--qa-passed"))
            if variant_id == "main":
                self.assertIn("/active/", output.as_posix())
            else:
                self.assertIn("/archive/", output.as_posix())

        archived, location = WORK_CLI.locate_work(self.root, work_id)
        self.assertEqual("archive", location)
        self.assertTrue((archived / "variants" / "main" / "final" / "final.mp4").is_file())

    def test_podcast_final_promotes_manifest_directory_and_archives(self) -> None:
        work_id, _ = self.new_work("Podcast quotes", "podcast_quote_image")
        candidate = self.prepare_package_final()
        result = self.invoke("finalize", str(candidate), expected=2)
        self.assertIn("Final QA must pass", result)

        archived_final = Path(self.invoke("finalize", str(candidate), "--qa-passed"))
        self.assertTrue((archived_final / "manifest.json").is_file())
        self.assertIn("/archive/", archived_final.as_posix())
        self.assertEqual(
            "manifest.json",
            json.loads((archived_final.parent / "variant.yaml").read_text(encoding="utf-8"))["current_final"],
        )
        self.assertEqual(str(archived_final), self.invoke("--work", work_id, "finalize", str(candidate), "--qa-passed"))

        self.invoke("reopen", work_id)
        replacement = self.prepare_package_final("quote-final-two", b"two")
        replaced_final = Path(self.invoke("finalize", str(replacement), "--qa-passed"))
        self.assertEqual(b"two1", (replaced_final / "01.jpg").read_bytes())
        self.assertEqual(b"one1", (replaced_final / "history" / "final-v001" / "01.jpg").read_bytes())


if __name__ == "__main__":
    unittest.main()
