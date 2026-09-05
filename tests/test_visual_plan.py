"""Focused lifecycle checks; real browser/render exercise is visual-mixed.mjs."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from test_work_cli import WORK_CLI
from visual_plan import scene_projection, validate_dependencies, VisualPlanError


class VisualPlanTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        repo = Path(__file__).resolve().parents[1]
        shutil.copytree(repo / ".studio" / "templates", self.root / ".studio" / "templates")
        self.run_cli("new", "Visual test", "--workflow", "hyperframes_video")
        self.variant = next((self.root / "works" / "active").iterdir()) / "variants" / "main"
        self.project = self.variant / "project"
        self.update("RESEARCH.md", status="ready")
        (self.project / "compositions").mkdir(exist_ok=True)
        (self.project / "index.html").write_text('<div id="S01" data-start="0" data-duration="4" data-composition-src="compositions/S01.html"></div>')
        (self.project / "compositions" / "S01.html").write_text('<p>Complete conditions remain visible.</p>')
        (self.project / "DESIGN.md").write_text("Test design")
        (self.project / "project-config.json").write_text("{}")

    def run_cli(self, *args):
        parsed = WORK_CLI.build_parser().parse_args(args)
        return parsed.handler(self.root, parsed)

    def update(self, name, **fields):
        path = self.variant / name
        text = path.read_text()
        end = text.index("\n---", 3)
        data = WORK_CLI.read_frontmatter(path)
        data.update(fields)
        path.write_text("---\n" + json.dumps(data) + text[end:])

    def test_plan_to_same_source_draft_and_local_diff(self):
        with (self.project / "index.html").open("a") as stream:
            stream.write('<div id="S02" data-start="4" data-duration="4" data-composition-src="compositions/S02.html"></div>')
        with (self.variant / "ANIMATION_PLAN.md").open("a") as stream:
            stream.write("\n| S02 | P001 |\n")
        untouched = self.project / "compositions" / "S02.html"
        untouched.write_text("<p>Unchanged explanation.</p>")
        self.run_cli("preview", "register", "--purpose", "plan")
        preview = self.variant / "previews" / "plan-v001"
        original = (preview / "source-snapshot" / "compositions" / "S01.html").read_bytes()
        self.run_cli("preview", "accept", "plan-v001")
        state = WORK_CLI.read_json(self.variant / "variant.yaml")
        self.assertIsNone(state["accepted_preview"])
        self.assertEqual("plan-v001", state["accepted_visual_plan"])
        movie = self.root / "draft.mp4"
        movie.write_bytes(b"test-only, not a render")
        with self.assertRaisesRegex(WORK_CLI.HarnessError, "No accepted preview"):
            self.run_cli("finalize", str(movie), "--qa-passed")
        (self.project / "compositions" / "S01.html").write_text("<p>Same meaning; adjusted line break.</p>")
        self.run_cli("preview", "diff", "plan-v001")
        self.run_cli("preview", "diff", "plan-v001", "--scene", "S01", "--range", "1", "3", "--note", "Adjust focus only")
        feedback = WORK_CLI.read_json(self.variant / ".runtime" / "feedback.json")["entries"]
        self.assertEqual(["S01"], feedback[0]["requested_scenes"])
        self.assertEqual(["compositions/S01.html"], feedback[0]["changed_files"])
        self.assertEqual(untouched.read_bytes(), (preview / "source-snapshot" / "compositions" / "S02.html").read_bytes())
        with self.assertRaisesRegex(WORK_CLI.HarnessError, "range"):
            self.run_cli("preview", "diff", "plan-v001", "--scene", "S01", "--range", "5", "7", "--note", "Invalid range")
        self.run_cli("preview", "register", str(movie))
        metadata = WORK_CLI.preview_metadata(self.variant / "previews" / "draft-v001")
        self.assertEqual(["compositions/S01.html"], metadata["changed_files"])
        self.assertEqual("plan-v001", metadata["source_plan"])
        self.assertEqual(original, (preview / "source-snapshot" / "compositions" / "S01.html").read_bytes())
        self.run_cli("preview", "accept", "draft-v001")
        with self.assertRaises(WORK_CLI.HarnessError):
            self.run_cli("finalize", str(movie), "--qa-passed")

    def test_changed_plan_source_and_stale_research_cannot_be_accepted(self):
        self.run_cli("preview", "register", "--purpose", "plan")
        self.update("RESEARCH.md", status="pending")
        with self.assertRaisesRegex(WORK_CLI.HarnessError, "not ready"):
            self.run_cli("preview", "accept", "plan-v001")
        self.update("RESEARCH.md", status="ready")
        (self.project / "compositions" / "S01.html").write_text("changed")
        with self.assertRaisesRegex(WORK_CLI.HarnessError, "Project changed"):
            self.run_cli("preview", "accept", "plan-v001")
        self.run_cli("preview", "register", "--purpose", "plan")
        self.run_cli("preview", "accept", "plan-v002")
        self.run_cli("preview", "accept", "plan-v002")
        self.update("ANIMATION_PLAN.md", revision=2)
        state = WORK_CLI.read_json(self.variant / "variant.yaml")
        state["plan_revision"] = 2
        WORK_CLI.write_variant(self.variant, state)
        with self.assertRaisesRegex(WORK_CLI.HarnessError, "stale"):
            self.run_cli("preview", "accept", "plan-v002")

    def test_scene_coverage_and_dependency_closure(self):
        plan = (self.variant / "ANIMATION_PLAN.md").read_text()
        scenes = scene_projection(self.project, plan)
        self.assertEqual(2, scenes[0]["reading"])
        with self.assertRaisesRegex(VisualPlanError, "match exactly"):
            scene_projection(self.project, plan + "\n| S02 | P002 |\n")
        self.assertEqual(["compositions/S01.html", "index.html"], validate_dependencies(self.project))
        (self.project / "compositions" / "S01.html").write_text('<script src="https://example.com/live.js"></script>')
        with self.assertRaisesRegex(VisualPlanError, "Non-local"):
            validate_dependencies(self.project)
        (self.project / "compositions" / "S01.html").write_text('<script src="../../escape.js"></script>')
        with self.assertRaisesRegex(VisualPlanError, "outside snapshot"):
            validate_dependencies(self.project)

    def test_missing_pinned_browser_fails_before_invoking_hyperframes(self):
        self.run_cli("preview", "register", "--purpose", "plan")
        self.run_cli("preview", "accept", "plan-v001")
        cli = self.root / "cli.js"
        cli.write_text("// unreachable")
        with patch.dict(os.environ, {"HYPERFRAMES_BROWSER_PATH": str(self.root / "missing.exe")}):
            with patch.object(WORK_CLI.subprocess, "run") as launch:
                with self.assertRaisesRegex(WORK_CLI.HarnessError, "Pinned render dependency"):
                    self.run_cli("preview", "render", "plan-v001", "--hyperframes-cli", str(cli), "--output", str(self.root / "test.mp4"))
                launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
