from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / ".agents" / "skills" / "native-subtitle-quote-image" / "scripts" / "native_subtitle_stitch.py"
SPEC = importlib.util.spec_from_file_location("native_subtitle_stitch", SCRIPT)
assert SPEC and SPEC.loader
STITCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STITCH)


class NativeSubtitleStitchTest(unittest.TestCase):
    def test_render_rejects_nonempty_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"images": [{"title": "test", "times": [1, 2]}]}))
            output = root / "output"
            output.mkdir()
            (output / "delivered.jpg").write_bytes(b"keep")
            args = SimpleNamespace(manifest=manifest, out_dir=output)

            with self.assertRaisesRegex(SystemExit, "输出目录必须为空"):
                STITCH.command_render(args)
            self.assertEqual(b"keep", (output / "delivered.jpg").read_bytes())


if __name__ == "__main__":
    unittest.main()
