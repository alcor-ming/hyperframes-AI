from pathlib import Path
import tempfile
import unittest
from unittest import mock
import json
import os

from test_work_cli import WORK_CLI
import storage


class StorageTest(unittest.TestCase):
    def test_explicit_closure_excludes_unreferenced_files_and_rejects_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "project-config.json").write_text(json.dumps({"snapshot_dependencies": ["dynamic.js"]}))
            (root / "DESIGN.md").write_text("design")
            (root / "index.html").write_text('<script src="entry.js"></script>')
            (root / "entry.js").write_text("import './shared.js'")
            (root / "shared.js").write_text("// required")
            (root / "dynamic.js").write_text("// explicit dynamic dependency")
            (root / "unused.bin").write_bytes(b"unused")
            self.assertEqual({"project-config.json", "DESIGN.md", "index.html", "entry.js", "shared.js", "dynamic.js"},
                             set(storage.snapshot_files(root)))
            frozen = root / "frozen"
            WORK_CLI.copy_snapshot(root, frozen)
            self.assertTrue(WORK_CLI.validate_snapshot_closure(root, frozen)["closed"])
            self.assertEqual(WORK_CLI.snapshot_digest(root), WORK_CLI.snapshot_digest(frozen))
            self.assertFalse((frozen / "unused.bin").exists())
            (frozen / "dynamic.js").write_text("tampered")
            with self.assertRaises(WORK_CLI.ComponentError):
                WORK_CLI.validate_snapshot_closure(root, frozen)
            (root / "index.html").write_text('<img src="small.png" srcset="large.png 2x">')
            (root / "small.png").write_bytes(b"small")
            (root / "large.png").write_bytes(b"large")
            with self.assertRaisesRegex(storage.StorageError, "srcset"):
                storage.snapshot_files(root)
            (root / "index.html").write_text('<script src="entry.js"></script>')
            (root / "entry.js").write_text("import '../escape.js'")
            with self.assertRaises(storage.StorageError):
                storage.snapshot_files(root)

    def test_reclaim_preserves_active_failed_referenced_unknown_and_external_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "runtime"
            runtime.mkdir()
            records = []
            for name in ("finished", "active", "failed", "referenced", "unknown"):
                (runtime / name).write_text(name)
                records.append({"path": name, "state": "succeeded", "rebuildable": True})
            records[1]["pid"] = os.getpid()
            records[2]["state"] = "failed"
            records[4]["rebuildable"] = False
            self.assertEqual(["finished"], storage.reclaim(runtime, records, {"referenced"}))
            self.assertEqual({"active", "failed", "referenced", "unknown"}, {p.name for p in runtime.iterdir()})
            source = root / "source"
            source.write_text("irreplaceable")
            for name in ("../source", str(source)):
                with self.assertRaises(storage.StorageError):
                    storage.reclaim(runtime, [{"path": name, "state": "succeeded", "rebuildable": True}], set())
            (runtime / "linked").symlink_to(source)
            with self.assertRaises(storage.StorageError):
                storage.reclaim(runtime, [{"path": "linked", "state": "succeeded", "rebuildable": True}], set())
            self.assertEqual("irreplaceable", source.read_text())

    def test_windows_liveness_never_calls_destructive_os_kill(self):
        import ctypes
        kernel = mock.Mock()
        kernel.OpenProcess.return_value = 42
        with mock.patch.object(storage.sys, "platform", "win32"), mock.patch.object(storage.os, "kill") as kill, \
                mock.patch.object(ctypes, "WinDLL", return_value=kernel, create=True), \
                mock.patch.object(ctypes, "get_last_error", return_value=5, create=True) as error:
            for state, stopped in ((258, False), (0, True), (0xFFFFFFFF, False)):
                kernel.WaitForSingleObject.return_value = state
                self.assertEqual(stopped, storage.process_stopped(123))
            kernel.OpenProcess.return_value = None
            self.assertFalse(storage.process_stopped(123))
            error.return_value = 87
            self.assertTrue(storage.process_stopped(123))
            kernel.CloseHandle.assert_called_with(42)
            kill.assert_not_called()


if __name__ == "__main__":
    unittest.main()
