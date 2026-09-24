import sys
from pathlib import Path
import tempfile
import unittest
import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
import research_catalog as R


class ResearchTest(unittest.TestCase):
    def test_document_truth_revision_rename_links_and_failed_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = R.create(root, kind="tool", title="Tool research")
            identity, path = row["id"], Path(row["path"])
            self.assertEqual(identity, R.register(root, path, kind="asset", title="Duplicate")["id"])
            row = R.update(root, identity, expected_revision=1, changes={"summary": "Original"})
            path.write_text("Updated original", encoding="utf-8")
            current = R.query(root)["documents"][0]
            self.assertTrue(current["unsynchronized"])
            self.assertTrue(current["summary_stale"])
            self.assertIsNone(current["summary"])
            with self.assertRaises(R.ComponentError):
                R.update(root, identity, expected_revision=1, sync=True)
            with patch.object(R, "_atomic_json", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    R.update(root, identity, expected_revision=2, sync=True)
            self.assertEqual("Updated original", path.read_text())
            renamed = path.with_name("renamed.md")
            path.rename(renamed)
            row = R.update(root, identity, expected_revision=2,
                           changes={"path": str(renamed), "links": [{"target": "v34", "path": str(root / "missing-plan")}]},
                           reference="v34")
            self.assertEqual(identity, row["id"])
            self.assertTrue(row["invalid_links"])
            self.assertEqual(row["sha256"], row["references"][0]["sha256"])
            snapshot = Path(row["references"][0]["snapshot_path"])
            renamed.write_text("Later unrelated edit")
            self.assertEqual("Updated original", snapshot.read_text())
            self.assertTrue(row["summary_stale"])
            R.create(root, kind="asset", title="Asset research")
            self.assertEqual(1, len(R.query(root, kind="asset")["documents"]))
            self.assertEqual(identity, R.query(root, related="v34")["documents"][0]["id"])

    def test_invalid_metadata_and_retained_create_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = R.create(root, kind="asset", title="Valid")
            for field, value in (("title", []), ("kind", []), ("topics", "not-list"),
                                 ("summary", {}), ("status", 5), ("path", None),
                                 ("links", [{"target": "plan", "path": 9}])):
                with self.subTest(field=field), self.assertRaises(R.ComponentError):
                    R.update(root, row["id"], expected_revision=1, changes={field: value})
            for invalid in ([], "text", False):
                with self.assertRaises(R.ComponentError):
                    R.update(root, row["id"], expected_revision=1, changes=invalid)
            with self.assertRaises(R.ComponentError):
                R.register(root, Path(row["path"]), kind="asset", title=[])
            with patch.object(R, "_atomic_json", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(R.ComponentError, "document retained at"):
                    R.create(root, kind="tool", title="Retained", text="Only content")
            self.assertEqual("Only content", next((root / "tool").glob("*.md")).read_text())

    def test_real_cli_handler_signature_and_json_error(self):
        import work
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parser = work.build_parser()
            args = parser.parse_args(["research", "--root", str(root), "create", "--kind", "tool", "--title", "CLI"])
            output = io.StringIO()
            with redirect_stdout(output):
                args.handler(root, args)
            row = json.loads(output.getvalue())
            args = parser.parse_args(["research", "--root", str(root), "update", row["id"], "--revision", "1", "--metadata", "{"])
            with self.assertRaises(R.ComponentError):
                args.handler(root, args)


if __name__ == "__main__":
    unittest.main()
