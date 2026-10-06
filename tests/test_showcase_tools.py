"""Isolated art generation and source/output protection; no production Work required."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


STUDIO = Path(__file__).resolve().parents[1] / ".studio"
sys.path.insert(0, str(STUDIO))
import showcase_tools

HAS_IMAGE_DEPS = all(importlib.util.find_spec(name) for name in ("numpy", "scipy", "PIL"))


class ShowcaseToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_lazy_import_missing_dependencies_and_unsafe_paths(self):
        result = subprocess.run([sys.executable, "-S", "-c",
                                 f"import sys; sys.path.insert(0, {str(STUDIO)!r}); import showcase_tools; "
                                 "assert 'numpy' not in sys.modules and 'PIL' not in sys.modules"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with mock.patch.object(showcase_tools, "import_module", side_effect=ImportError("missing")):
            with self.assertRaisesRegex(ValueError, "require numpy"):
                showcase_tools.stage(self.root / "missing-deps")
        existing = self.root / "unowned"
        existing.mkdir()
        sentinel = existing / "keep.txt"
        sentinel.write_text("user data")
        with self.assertRaises(FileExistsError):
            showcase_tools.stage(existing)
        with self.assertRaisesRegex(ValueError, "intact output"):
            showcase_tools.stage(existing, overwrite=True)
        self.assertEqual(sentinel.read_text(), "user data")
        linked = self.root / "linked"
        linked.symlink_to(existing, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            showcase_tools.stage(linked / "stage")
        for invalid in (self.root / "missing", self.root / "empty"):
            if invalid.name == "empty":
                invalid.touch()
            with self.assertRaisesRegex(ValueError, "nonempty"):
                showcase_tools.cast(invalid, self.root / "invalid")

    @unittest.skipUnless(HAS_IMAGE_DEPS, "requires managed numpy, scipy and Pillow dependencies")
    def test_synthetic_sheet_pose_and_invalid_layout_preserve_sources(self):
        from PIL import Image, ImageDraw
        sheet = self.root / "sheet.png"
        image = Image.new("RGB", (300, 150), "white")
        draw = ImageDraw.Draw(image)
        for x, color in ((20, "#cd4848"), (120, "#4673b5"), (220, "#329156")):
            draw.rounded_rectangle((x, 15, x + 55, 135), radius=12, fill=color)
        image.save(sheet)
        original = sheet.read_bytes()
        result = showcase_tools.cast(sheet, self.root / "cast", target_height=96, border=3)
        self.assertEqual(result["input"]["sha256"], sha256(original).hexdigest())
        self.assertEqual({item["path"] for item in result["files"]},
                         {"front.png", "side.png", "back.png", "kraft.png", "silhouette.png", "gray.png"})
        self.assertEqual(result["parameters"], {"kind": "sheet", "border": 3, "target_height": 96, "seed": 7})
        for item in result["files"]:
            with Image.open(Path(result["output"]) / item["path"]) as rendered:
                low, high = rendered.getchannel("A").getextrema()
                self.assertEqual((low, high), (0, 255))
        self.assertEqual(sheet.read_bytes(), original)
        stored = json.loads(Path(result["manifest"]).read_text())
        self.assertEqual(stored["tool_version"], showcase_tools.VERSION)
        self.assertIn("cast_art.py", stored["implementation"])
        repeated = showcase_tools.cast(sheet, self.root / "cast", target_height=96, border=3, overwrite=True)
        self.assertEqual(result["files"], repeated["files"])
        with self.assertRaises(FileExistsError):
            showcase_tools.cast(sheet, self.root / "cast")
        (self.root / "cast" / "user.txt").write_text("keep")
        with self.assertRaisesRegex(ValueError, "intact output"):
            showcase_tools.cast(sheet, self.root / "cast", overwrite=True)

        pose = self.root / "pose.png"
        alpha = Image.new("RGBA", (90, 120))
        ImageDraw.Draw(alpha).ellipse((15, 10, 75, 110), fill=(30, 110, 180, 255))
        alpha.save(pose)
        pose_bytes = pose.read_bytes()
        posed = showcase_tools.cast(pose, self.root / "pose-art", kind="pose", pose_scale=1)
        self.assertEqual([item["path"] for item in posed["files"]], ["pose.png"])
        self.assertEqual(pose.read_bytes(), pose_bytes)
        with self.assertRaisesRegex(ValueError, "source image"):
            # An explicit overwrite must never turn an output directory into an input deletion.
            showcase_tools.cast(self.root / "pose-art" / "pose.png", self.root / "pose-art", kind="pose", overwrite=True)
        link = self.root / "source-link.png"
        link.symlink_to(pose)
        with self.assertRaisesRegex(ValueError, "symlink"):
            showcase_tools.cast(link, self.root / "linked-pose", kind="pose")

        invalid = self.root / "invalid.png"
        for image, kind in ((Image.new("RGB", (100, 100), "white"), "sheet"),
                            (Image.new("RGB", (100, 100), "black"), "sheet"),
                            (Image.new("RGBA", (100, 100)), "pose"),
                            (Image.new("RGB", (100, 100), "red"), "pose")):
            image.save(invalid)
            with self.subTest(kind=kind, mode=image.mode), self.assertRaises(ValueError):
                showcase_tools.cast(invalid, self.root / "rejected", kind=kind)
            self.assertFalse((self.root / "rejected").exists())
        single = Image.new("RGB", (100, 150), "white")
        ImageDraw.Draw(single).rectangle((20, 15, 80, 135), fill="red")
        single.save(invalid)
        with self.assertRaisesRegex(ValueError, "unsupported"):
            showcase_tools.cast(invalid, self.root / "single")
        tiny = Image.new("RGBA", (16, 16))
        tiny.putpixel((8, 8), (20, 50, 100, 255))
        tiny.save(invalid)
        with self.assertRaisesRegex(ValueError, "disappears"):
            showcase_tools.cast(invalid, self.root / "vanishing", kind="pose", pose_scale=0.05)

        before = {path.name: path.read_bytes() for path in (self.root / "pose-art").iterdir()}
        with mock.patch("cast_art.diecut", side_effect=ValueError("injected render failure")):
            with self.assertRaisesRegex(ValueError, "injected"):
                showcase_tools.cast(pose, self.root / "pose-art", kind="pose", overwrite=True)
        self.assertEqual(before, {path.name: path.read_bytes() for path in (self.root / "pose-art").iterdir()})
        rename = Path.rename

        def fail_install(path, target):
            if path.name == "generated":
                raise OSError("injected install failure")
            return rename(path, target)

        with mock.patch.object(Path, "rename", fail_install):
            with self.assertRaisesRegex(OSError, "injected install"):
                showcase_tools.cast(pose, self.root / "pose-art", kind="pose", overwrite=True)
        self.assertEqual(before, {path.name: path.read_bytes() for path in (self.root / "pose-art").iterdir()})

    @unittest.skipUnless(HAS_IMAGE_DEPS, "requires managed numpy, scipy and Pillow dependencies")
    def test_stage_generates_loadable_media_without_source_work(self):
        from PIL import Image
        result = showcase_tools.stage(self.root / "project" / "assets" / "stage")
        self.assertEqual(result["parameters"]["ratio"], "16:9")
        self.assertGreater(len(result["files"]), 15)
        self.assertIn("bd-clouds.jpg", {item["path"] for item in result["files"]})
        frame = Path(result["output"]) / "frame.png"
        with Image.open(frame) as image:
            self.assertEqual(image.size, (1920, 1080))
            self.assertEqual(image.getchannel("A").getextrema(), (0, 255))
        project = self.root / "project"
        references = [f'assets/stage/{item["path"]}' for item in result["files"]]
        (project / "index.html").write_text("\n".join(f'<img src="{path}">' for path in references))
        for path in references:
            with Image.open(project / path) as image:
                image.verify()
        self.assertTrue(Path(result["manifest"]).is_file())


if __name__ == "__main__":
    unittest.main()
