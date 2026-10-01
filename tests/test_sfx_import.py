import json
from pathlib import Path
import sys
import tempfile
import shutil
import subprocess
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
import sfx_import
from component_harness import ComponentError


class SfxImportTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "local ffmpeg required")
    def test_synthetic_mp3_import_freeze_and_validate(self):
        import asset_contract
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundled = root / "package/dist/skills/media-use/audio/assets/sfx"
            bundled.mkdir(parents=True)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=0.2", "-af", "adelay=100:all=1",
                            str(bundled / "click.mp3")], check=True)
            (bundled / "manifest.json").write_text(json.dumps({"click": {"file": "click.mp3", "description": "Synthetic click"}}))
            (bundled / "CREDITS.md").write_text("Synthetic test")
            sfx_import.import_sfx(root / "package", root / "source")
            report = asset_contract.freeze_source(root / "source/click", root / "frozen")
            self.assertEqual(report, asset_contract.validate_asset(root / "frozen"))
            self.assertTrue(report["metadata"]["hit_offset_estimated"])
            self.assertGreater(report["metadata"]["hit_offset"], 0.08)
            self.assertLess(report["metadata"]["hit_offset"], 0.15)

    def test_import_local_manifest_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundled = root / "package/dist/skills/media-use/audio/assets/sfx"
            bundled.mkdir(parents=True)
            (bundled / "manifest.json").write_text(json.dumps({"click": {"file": "click.mp3", "description": "A click"}}))
            (bundled / "CREDITS.md").write_text("Synthetic license")
            (bundled / "click.mp3").write_bytes(b"synthetic")
            with patch.object(sfx_import, "hit_offset", return_value=(0.12, True)):
                report = sfx_import.import_sfx(root / "package", root / "source")
            self.assertFalse(report["accepted"])
            metadata = json.loads((root / "source/click/asset.json").read_text())
            self.assertEqual(metadata["hit_offset"], 0.12)
            self.assertEqual(metadata["tags"], ["click"])
            self.assertEqual(metadata["license"], "CREDITS.md")
            with self.assertRaisesRegex(ComponentError, "already exists"):
                sfx_import.import_sfx(root / "package", root / "source")
            (bundled / "manifest.json").write_text(json.dumps({"pop": {"file": "../escape.mp3", "description": "Bad"}}))
            with self.assertRaises(ComponentError):
                sfx_import.import_sfx(root / "package", root / "other")
            self.assertFalse((root / "other").exists())

    def test_offset_and_failure_fallback(self):
        from subprocess import CompletedProcess
        for stderr, code, expected in (("silence_start: 0\nsilence_end: 0.125", 0, (0.125, True)),
                                       ("", 0, (0, True)), ("error", 1, (0, False))):
            with patch.object(sfx_import.subprocess, "run", return_value=CompletedProcess([], code, "", stderr)):
                self.assertEqual(sfx_import.hit_offset(Path("synthetic.mp3")), expected)
        with patch.object(sfx_import.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(sfx_import.hit_offset(Path("synthetic.mp3")), (0, False))


if __name__ == "__main__":
    unittest.main()
