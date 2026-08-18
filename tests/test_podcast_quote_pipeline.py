from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from PIL import Image


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / ".agents" / "skills" / "podcast-quote-image" / "scripts" / "podcast_quote_pipeline.py"
SPEC = importlib.util.spec_from_file_location("podcast_quote_pipeline", SCRIPT)
assert SPEC and SPEC.loader
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class PodcastQuotePipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, *arguments: str, expected: int = 0) -> str:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = PIPELINE.main(list(arguments))
        self.assertEqual(expected, result, stderr.getvalue())
        return stdout.getvalue().strip() or stderr.getvalue().strip()

    def write_json(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def test_resolve_uses_subtitle_wording_and_flags_clear_conflict(self) -> None:
        transcript = self.write_json(
            "source.json",
            {
                "language": "en",
                "segments": [
                    {"start": 0, "end": 1, "text": "hello world"},
                    {"start": 1, "end": 2, "text": "second idea"},
                ],
            },
        )
        subtitle = self.root / "source.srt"
        subtitle.write_text(
            "1\n00:00,000 --> 00:01,000\nhello world\n\n"
            "2\n00:01,000 --> 00:02,000\nsecond idea\n",
            encoding="utf-8",
        )
        resolved = self.root / "resolved.json"
        self.invoke("resolve", "--transcript", str(transcript), "--subtitle", str(subtitle), "--out", str(resolved))
        value = json.loads(resolved.read_text(encoding="utf-8"))
        self.assertEqual("ready", value["status"])
        self.assertEqual(["subtitle", "subtitle"], [item["source"] for item in value["segments"]])

        subtitle_json = self.write_json(
            "subtitle.json",
            {"language": "en", "segments": [{"start": 0, "end": 1, "text": "json subtitle"}]},
        )
        self.invoke("resolve", "--subtitle", str(subtitle_json), "--out", str(resolved))
        self.assertEqual("json subtitle", json.loads(resolved.read_text())["segments"][0]["text"])

        transcript.write_text(
            json.dumps({"language": "en", "segments": [{"start": 0, "end": 1, "text": "aaaaaaaaaaaa"}]})
            + "\n",
            encoding="utf-8",
        )
        subtitle.write_text("1\n00:00,000 --> 00:01,000\nzzzzzzzzzzzz\n", encoding="utf-8")
        self.invoke("resolve", "--transcript", str(transcript), "--subtitle", str(subtitle), "--out", str(resolved))
        self.assertEqual("needs_review", json.loads(resolved.read_text())["status"])

    def test_approved_quotes_flow_through_frames_render_and_qa(self) -> None:
        transcript = self.write_json(
            "transcript.json",
            {
                "schema_version": 1,
                "workflow": "podcast_quote_image",
                "status": "ready",
                "segments": [
                    {"id": f"s{index:06d}", "start": index - 1, "end": index, "text": f"line {index}"}
                    for index in range(1, 31)
                ],
            },
        )
        candidates = self.write_json(
            "quote-candidates.json",
            {
                "schema_version": 1,
                "workflow": "podcast_quote_image",
                "transcript_sha256": PIPELINE.sha256(transcript),
                "candidates": [
                    {
                        "id": f"q{group:02d}",
                        "rank": group,
                        "rationale": "useful",
                        "units": [
                            {
                                "id": f"u{unit:02d}",
                                "original": f"Original {group}-{unit}",
                                "translation_zh": f"中文 {group}-{unit}",
                                "source_segment_ids": [f"s{((group - 1) * 5 + unit):06d}"],
                            }
                            for unit in range(1, 6)
                        ],
                    }
                    for group in range(1, 7)
                ],
            },
        )
        self.invoke("validate-candidates", "--transcript", str(transcript), "--candidates", str(candidates))
        selection = self.root / "quote-selection.json"
        self.invoke(
            "approve",
            "--transcript",
            str(transcript),
            "--candidates",
            str(candidates),
            "--select",
            "q04",
            "--select",
            "q01",
            "--select",
            "q06",
            "--out",
            str(selection),
        )
        self.assertEqual(["q01", "q04", "q06"], json.loads(selection.read_text())["selected_ids"])

        aligned = self.root / "aligned-quotes.json"
        self.invoke("align", "--transcript", str(transcript), "--selection", str(selection), "--out", str(aligned))
        video = self.root / "video.mp4"
        video.write_bytes(b"fixture")
        frames_dir = self.root / "frames"

        def fake_extract(_video: Path, seconds: float, output: Path) -> None:
            output.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (640, 360), (int(seconds * 7) % 255, 80, 120)).save(output)

        with mock.patch.object(PIPELINE, "extract_frame", side_effect=fake_extract):
            self.invoke("extract", str(video), "--aligned", str(aligned), "--out-dir", str(frames_dir))
        frame_candidates = frames_dir / "frame-candidates.json"
        frame_value = json.loads(frame_candidates.read_text())
        self.assertEqual([0.25, 0.5, 0.75], [item["time"] for item in frame_value["groups"][0]["units"][0]["candidates"]])

        choices = [
            candidate["id"]
            for group in frame_value["groups"]
            for unit in group["units"]
            for candidate in unit["candidates"]
            if candidate["id"].endswith("f02")
        ]
        frame_selection = self.root / "frame-selection.json"
        arguments = ["choose-frames", "--candidates", str(frame_candidates), "--out", str(frame_selection)]
        for choice in choices:
            arguments.extend(("--choice", choice))
        self.invoke(*arguments)

        package = self.root / "PACKAGE.md"
        package.write_text(
            "# Package\n\n## 标题\n测试\n\n## 正文\n正文\n\n## 播客信息\n\n"
            "- 频道：Test Channel\n- 节目：Test Podcast\n- 嘉宾：\n- 期数：\n"
            "- 来源 URL：https://example.com/watch\n\n## 话题标签\n#测试\n",
            encoding="utf-8",
        )
        font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        if not font.is_file():
            self.skipTest("DejaVu Sans is unavailable")
        render = self.root / "render"
        self.invoke(
            "render",
            "--aligned",
            str(aligned),
            "--frames",
            str(frame_selection),
            "--package",
            str(package),
            "--font",
            str(font),
            "--out-dir",
            str(render),
        )
        self.assertEqual("pending_visual_review", self.invoke("verify", "--render-dir", str(render)))
        self.assertEqual("passed", self.invoke("verify", "--render-dir", str(render), "--visual-passed"))
        manifest = json.loads((render / "manifest.json").read_text())
        self.assertEqual(3, manifest["image_count"])
        with Image.open(next(render.glob("[0-9][0-9]_*.jpg"))) as image:
            self.assertEqual((1440, 1920), image.size)


if __name__ == "__main__":
    unittest.main()
