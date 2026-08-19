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

    def test_package_uses_original_video_title_without_url(self) -> None:
        package = self.root / "PACKAGE.md"
        text = "# 测试标题\n\n开篇。\n\n## 小标题\n\n正文。\n\n原视频：Original Title\n\n#测试\n"
        package.write_text(text, encoding="utf-8")
        PIPELINE.validate_package(package, ["g01"])
        package.write_text(text.replace("\n\n#测试", "\n\nhttps://youtu.be/example\n\n#测试"), encoding="utf-8")
        with self.assertRaises(PIPELINE.PipelineError):
            PIPELINE.validate_package(package, ["g01"])

    def test_acquire_adopts_only_verified_trendradar_media(self) -> None:
        profile = self.write_json("media-profile.json", {"schema_version": "2.0"})
        materials = self.root / "variant" / "materials"
        materials.mkdir(parents=True)
        downloaded = self.root / "external-run" / "asset.mp4"
        downloaded.parent.mkdir()
        downloaded.write_bytes(b"verified-video")
        manifest = self.root / "external-run" / "media-manifest.private.jsonl"
        manifest.write_text(
            json.dumps(
                {
                    "source_id": "podcast-source",
                    "source_url": "https://youtu.be/example",
                    "platform": "youtube",
                    "media_type": "video",
                    "local_media_path": str(downloaded.resolve()),
                    "media_size_bytes": downloaded.stat().st_size,
                    "media_hash": f"sha256:{PIPELINE.sha256(downloaded)}",
                    "download_status": "succeeded",
                    "error_code": "",
                    "retryable": False,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        def fake_run(command: list[str], **_kwargs: object) -> object:
            request = json.loads(Path(command[-1]).read_text(encoding="utf-8"))
            self.assertEqual("2.0", request["schema_version"])
            self.assertEqual("youtube", request["sources"][0]["platform"])
            envelope = {
                "schema_version": "2.0",
                "job_id": request["job_id"],
                "status": "succeeded",
                "manifest_ref": str(manifest.resolve()),
                "completed_at": "2026-08-18T12:00:00Z",
                "expires_at": "2026-08-25T12:00:00Z",
                "succeeded": 1,
                "failed": 0,
                "exit_code": 0,
                "error": None,
            }
            return PIPELINE.subprocess.CompletedProcess(command, 0, json.dumps(envelope), "")

        arguments = (
            "acquire",
            "--url",
            "https://youtu.be/example",
            "--profile",
            str(profile),
            "--job-id",
            "work-20260818-播客",
            "--platform",
            "youtube",
            "--materials-dir",
            str(materials),
        )
        with mock.patch.object(PIPELINE.shutil, "which", return_value="/usr/local/bin/trendradar-media"), mock.patch.object(
            PIPELINE.subprocess, "run", side_effect=fake_run
        ):
            adopted = Path(self.invoke(*arguments))
            self.assertEqual(str(adopted), self.invoke(*arguments))
        self.assertEqual(b"verified-video", adopted.read_bytes())
        receipt_text = (materials / "acquisition.json").read_text(encoding="utf-8")
        receipt = json.loads(receipt_text)
        self.assertEqual("trendradar-media", receipt["provider"])
        self.assertTrue(receipt["job_id"].startswith("hf-"))
        self.assertEqual(PIPELINE.sha256(adopted), receipt["media"]["sha256"])
        self.assertNotIn("manifest_ref", receipt_text)
        self.assertNotIn(str(downloaded), receipt_text)

        failed = PIPELINE.subprocess.CompletedProcess(
            ["trendradar-media"],
            3,
            json.dumps(
                {
                    "schema_version": "2.0",
                    "job_id": "work-20260818-failed",
                    "status": "failed",
                    "succeeded": 0,
                    "failed": 0,
                    "error": {"code": "backend_unavailable", "retryable": True},
                }
            ),
            "",
        )
        failed_arguments = list(arguments)
        failed_arguments[failed_arguments.index("work-20260818-播客")] = "work-20260818-failed"
        with mock.patch.object(PIPELINE.shutil, "which", return_value="/usr/local/bin/trendradar-media"), mock.patch.object(
            PIPELINE.subprocess, "run", return_value=failed
        ):
            message = self.invoke(*failed_arguments, expected=2)
        self.assertIn("backend_unavailable", message)

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

        duration_json = self.write_json(
            "duration.json",
            {"language_code": "en", "segments": [{"start": 2, "duration": 1.5, "text": "duration timing"}]},
        )
        self.invoke("resolve", "--transcript", str(duration_json), "--out", str(resolved))
        duration_value = json.loads(resolved.read_text())
        self.assertEqual("en", duration_value["language"])
        self.assertEqual(3.5, duration_value["segments"][0]["end"])

        transcript.write_text(
            json.dumps({"language": "en", "segments": [{"start": 0, "end": 1, "text": "aaaaaaaaaaaa"}]})
            + "\n",
            encoding="utf-8",
        )
        subtitle.write_text("1\n00:00,000 --> 00:01,000\nzzzzzzzzzzzz\n", encoding="utf-8")
        self.invoke("resolve", "--transcript", str(transcript), "--subtitle", str(subtitle), "--out", str(resolved))
        self.assertEqual("needs_review", json.loads(resolved.read_text())["status"])

    def test_youtube_transcript_preserves_structured_timing_and_url_forms(self) -> None:
        video_id = "dQw4w9WgXcQ"
        for value in (
            video_id,
            f"https://youtu.be/{video_id}",
            f"https://www.youtube.com/watch?v={video_id}",
            f"https://youtube.com/shorts/{video_id}",
            f"https://youtube.com/embed/{video_id}",
            f"https://youtube.com/live/{video_id}",
        ):
            self.assertEqual(video_id, PIPELINE.extract_youtube_video_id(value))

        class FakeTranscript(list):
            language_code = "en"
            is_generated = True

        transcript = FakeTranscript(
            [
                mock.Mock(start=0.0, duration=1.25, text="First line"),
                mock.Mock(start=1.25, duration=2.0, text="Second line"),
            ]
        )
        output = self.root / "youtube-transcript.json"
        with mock.patch.object(PIPELINE, "fetch_youtube_transcript", return_value=transcript):
            self.invoke(
                "youtube-transcript",
                "--url",
                f"https://youtu.be/{video_id}",
                "--language",
                "zh-Hans,en",
                "--out",
                str(output),
            )
        value = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("youtube-transcript-api", value["provider"])
        self.assertEqual([0.0, 1.25], [item["start"] for item in value["segments"]])
        self.assertEqual([1.25, 3.25], [item["end"] for item in value["segments"]])
        self.assertFalse(value["used_language_fallback"])

    def test_approved_article_flows_through_frames_render_and_qa(self) -> None:
        transcript = self.write_json(
            "transcript.json",
            {
                "schema_version": 1,
                "workflow": "podcast_quote_image",
                "status": "ready",
                "segments": [
                    {"id": f"s{index:06d}", "start": index - 1, "end": index, "text": f"line {index}"}
                    for index in range(1, 121)
                ],
            },
        )
        image_counts = [4, 6, 8]
        candidates = self.write_json(
            "article-candidates.json",
            {
                "schema_version": 1,
                "workflow": "podcast_quote_image",
                "transcript_sha256": PIPELINE.sha256(transcript),
                "candidates": [
                    {
                        "id": f"a{article:02d}",
                        "rank": article,
                        "core_viewpoint": f"Core viewpoint {article}",
                        "audience_tension": f"Audience tension {article}",
                        "rationale": "useful",
                        "images": [
                            {
                                "id": f"g{image:02d}",
                                "structural_role": "argument beat",
                                "focus": f"Image focus {article}-{image}",
                                "units": [
                                    {
                                        "id": f"u{unit:02d}",
                                        "original": f"Original {article}-{image}-{unit}",
                                        "translation_zh": f"中文 {article}-{image}-{unit}",
                                        "source_segment_ids": [
                                            f"s{((article - 1) * 40 + (image - 1) * 5 + unit):06d}"
                                        ],
                                    }
                                    for unit in range(1, 5 + image % 2)
                                ],
                            }
                            for image in range(1, image_counts[article - 1] + 1)
                        ],
                    }
                    for article in range(1, 4)
                ],
            },
        )
        self.invoke("validate-candidates", "--transcript", str(transcript), "--candidates", str(candidates))
        invalid_value = json.loads(candidates.read_text(encoding="utf-8"))
        invalid_value["candidates"][0]["images"][0]["units"] = invalid_value["candidates"][0]["images"][0][
            "units"
        ][:3]
        invalid = self.write_json("invalid-candidates.json", invalid_value)
        message = self.invoke(
            "validate-candidates",
            "--transcript",
            str(transcript),
            "--candidates",
            str(invalid),
            expected=2,
        )
        self.assertIn("1 Hero and 3 or 4 supports", message)
        selection = self.root / "article-selection.json"
        self.invoke(
            "approve",
            "--transcript",
            str(transcript),
            "--candidates",
            str(candidates),
            "--select",
            "a02",
            "--out",
            str(selection),
        )
        self.assertEqual("a02", json.loads(selection.read_text())["selected_id"])

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
        self.assertEqual(
            [40.25, 40.5, 40.75],
            [item["time"] for item in frame_value["groups"][0]["units"][0]["candidates"]],
        )

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
        image_copy = "\n\n".join(
            f"## 小标题 {index}\n\n第三人称正文 {index}。" for index in range(1, 7)
        )
        package.write_text(
            "# 测试标题\n\n她的核心观点是测试。\n\n"
            f"{image_copy}\n\nTest Channel · Test Podcast\n\n"
            "原视频：Test Video Original Title\n\n#测试\n",
            encoding="utf-8",
        )
        font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        if not font.is_file():
            self.skipTest("DejaVu Sans is unavailable")
        render = self.root / "render"
        real_text_layout = PIPELINE.text_layout

        def require_tighter_padding(*args, **kwargs):
            max_width = args[3]
            hero = args[4]
            if not hero and max_width < 1300:
                raise PIPELINE.PipelineError("fixture requires tighter padding")
            return real_text_layout(*args, **kwargs)

        with mock.patch.object(PIPELINE, "text_layout", side_effect=require_tighter_padding):
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
        self.assertEqual(6, manifest["image_count"])
        self.assertEqual("podcast_drawn_subtitle_stack_v1", manifest["style"])
        self.assertEqual("frame_bottom", manifest["crop_anchor"])
        self.assertEqual("fixed_hero_dynamic_support", manifest["layout"]["mode"])
        self.assertEqual(0.52, manifest["layout"]["hero_fraction"])
        self.assertEqual(185, manifest["layout"]["text_backdrop_alpha"])
        self.assertEqual(6, len(manifest["layout"]["groups"]))
        self.assertTrue(
            all(group["hero_fraction"] == 0.52 for group in manifest["layout"]["groups"])
        )
        self.assertTrue(
            all(
                group["hero_height"] + sum(group["support_heights"]) == 1920
                for group in manifest["layout"]["groups"]
            )
        )
        self.assertTrue(
            all(0.03 <= group["horizontal_padding_fraction"] <= 0.06 for group in manifest["layout"]["groups"])
        )
        self.assertTrue(
            all(group["horizontal_padding_fraction"] == 0.04 for group in manifest["layout"]["groups"])
        )
        self.assertEqual("zh_only", manifest["font"]["mode"])
        self.assertEqual(42, manifest["font"]["zh_size"])
        self.assertNotIn("original_size", manifest["font"])
        with Image.open(next(render.glob("[0-9][0-9]_*.jpg"))) as image:
            self.assertEqual((1440, 1920), image.size)


if __name__ == "__main__":
    unittest.main()
