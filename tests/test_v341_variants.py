from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_work_cli import REPO, WORK_CLI as cli


class PeerVariantTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(REPO / ".studio/templates", self.root / ".studio/templates")
        cli.account_service(self.root).put("series", "one", {"name": "One"})
        for account in ("a", "b"):
            cli.account_service(self.root).put("account", account, {"name": account, "ratio": "16:9"})

    def run_cli(self, *arguments, expected=0):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            result = cli.main(["--json", *arguments], root=self.root)
        self.assertEqual(expected, result, error.getvalue())
        return output.getvalue().strip() or error.getvalue().strip()

    def new(self, title="Content", *options):
        identity = self.run_cli("new", title, "--workflow", "hyperframes_video", "--purpose", "standard",
                                "--series", "one", *options)
        return cli.locate_work(self.root, identity)[0]

    def test_zero_variant_content_lifecycle_and_production_guard(self):
        self.new("Previous", "--account", "a")
        work = self.new()
        self.assertEqual([], cli.variant_paths(work))
        self.assertNotIn("required_variants", cli.read_frontmatter(work / "WORK.md"))
        self.assertEqual("active", cli.locate_work(self.root, work.name)[1])
        self.assertIsNone(json.loads(self.run_cli("current"))["variant"])
        self.assertEqual("尚未创建制作版本", json.loads(self.run_cli("status"))["message"])
        self.assertEqual(1, cli.read_frontmatter(work / "shared/RESEARCH.md")["script_revision"])
        self.run_cli("script", "text")
        self.assertIn("No current variant", self.run_cli("wait", "script_approval", expected=2))
        self.assertIn("requires --account", self.run_cli("variant", "add", "b", expected=2))
        self.assertIn("requires --account", self.run_cli(
            "new", "Invalid", "--workflow", "hyperframes_video", "--purpose", "standard", "--series", "one",
            "--variant-id", "b", expected=2))
        self.run_cli("park")
        self.run_cli("resume")
        self.run_cli("archive", "--outcome", "stored")
        self.run_cli("reopen", work.name)
        self.run_cli("use", work.name)
        self.assertIsNone(json.loads(self.run_cli("current"))["variant"])
        self.assertEqual("standard", json.loads(self.run_cli("list"))[0]["purpose"])

    def test_peer_selection_never_prefers_main_or_another_work_current(self):
        work = self.new("Peers", "--account", "a")
        self.run_cli("variant", "add", "b", "--account", "b")
        other = self.new("Other", "--account", "a", "--variant-id", "b")
        self.run_cli("use", work.name)
        self.assertIsNone(json.loads(self.run_cli("current"))["variant"])
        self.assertIsNone(json.loads(self.run_cli("status"))["variant"])
        self.run_cli("script", "text")
        self.assertIn("Available: b, main", self.run_cli("wait", "script_approval", expected=2))
        self.run_cli("--variant", "b", "use", work.name)
        self.assertEqual("b", json.loads(self.run_cli("--work", work.name, "status"))["variant"]["id"])
        self.run_cli("use", other.name)
        self.run_cli("--work", work.name, "variant", "use", "main")
        self.assertEqual(work.name, json.loads(self.run_cli("current"))["work"])
        self.assertEqual("main", json.loads(self.run_cli("current"))["variant"])
        self.assertIn("Unknown variant", self.run_cli("--variant", "missing", "use", other.name, expected=2))
        self.assertEqual(work.name, json.loads(self.run_cli("current"))["work"])
        self.assertIn("Select --variant-id", self.run_cli("archive", "--outcome", "stored", expected=2))
        self.run_cli("archive", "--outcome", "stored", "--variant-id", "main")
        self.run_cli("use", other.name)
        self.run_cli("reopen", work.name, "--variant-id", "main")
        self.assertEqual("main", json.loads(self.run_cli("current"))["variant"])
        self.assertEqual("active", cli.read_json(work / "variants/main/variant.yaml")["lifecycle"])
        self.assertEqual("active", cli.read_json(work / "variants/b/variant.yaml")["lifecycle"])

    def test_shared_source_explicit_branch_and_frozen_accounts(self):
        work = self.new("Shared", "--account", "a", "--variant-id", "first")
        first = work / "variants/first"
        frozen = (first / "variant.yaml").read_bytes()
        (work / "shared/SCRIPT.md").write_text("---\n{\"revision\":7}\n---\nShared content\n", encoding="utf-8")
        cli.account_service(self.root).put("account", "a", {"name": "Updated", "ratio": "9:16"})
        self.run_cli("variant", "add", "second", "--account", "a")
        second = work / "variants/second"
        self.assertEqual(work / "shared/SCRIPT.md", cli.input_path(second, "SCRIPT.md"))
        self.assertEqual("9:16", cli.read_json(second / "variant.yaml")["ratio"])
        self.assertEqual(7, cli.read_json(second / "variant.yaml")["script_revision"])
        self.assertEqual(frozen, (first / "variant.yaml").read_bytes())
        self.run_cli("variant", "add", "branch", "--account", "b", "--from", "first")
        branch = work / "variants/branch"
        self.assertEqual("first", cli.read_json(branch / "variant.yaml")["content_branch"]["source_variant"])
        self.assertEqual(7, cli.read_frontmatter(branch / "SCRIPT.md")["revision"])
        self.assertNotEqual(work / "shared/SCRIPT.md", cli.input_path(branch, "SCRIPT.md"))

    def test_final_metadata_alone_does_not_archive_and_single_variant_is_selected(self):
        work = self.new("Delivery", "--account", "a")
        variant = work / "variants/main"
        state = cli.read_json(variant / "variant.yaml")
        state["current_final"] = "final.mp4"
        cli.write_variant(variant, state)
        (variant / "final").mkdir(exist_ok=True)
        (variant / "final/final.mp4").write_bytes(b"fixture")
        self.assertEqual("active", cli.locate_work(self.root, work.name)[1])
        self.assertEqual("active", cli.read_json(variant / "variant.yaml")["lifecycle"])
        cli.clear_pointer(self.root, "current-variant")
        self.assertEqual("main", json.loads(self.run_cli("status"))["variant"]["id"])


if __name__ == "__main__":
    unittest.main()
