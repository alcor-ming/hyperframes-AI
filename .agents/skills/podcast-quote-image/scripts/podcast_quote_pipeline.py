#!/usr/bin/env python3
"""Deterministic transcript, timing, frame, render, and QA pipeline for podcast quote images."""

from __future__ import annotations

import argparse
from datetime import datetime
from difflib import SequenceMatcher
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any
from urllib.parse import parse_qs, urlparse

from PIL import Image, ImageDraw, ImageFont, ImageOps


SCHEMA_VERSION = 1
WORKFLOW = "podcast_quote_image"
ASR_SCRIPT = Path("/home/jym/workspace/_external/scripts/asr.sh")
FONT_CANDIDATES = (
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Bold.otf"),
    Path("/mnt/c/Windows/Fonts/msyhbd.ttc"),
    Path("/mnt/c/Windows/Fonts/msyh.ttc"),
)
ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
MEDIA_JOB_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class PipelineError(RuntimeError):
    pass


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PipelineError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def validate_segment_times(start: Any, end: Any, label: str) -> tuple[float, float]:
    if not finite_number(start) or not finite_number(end):
        raise PipelineError(f"{label} requires finite start/end times")
    first, last = float(start), float(end)
    if first < 0 or last <= first:
        raise PipelineError(f"{label} requires 0 <= start < end")
    return round(first, 3), round(last, 3)


def extract_youtube_video_id(value: str) -> str:
    candidate = value.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        return candidate
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not host or parsed.username or parsed.password:
        raise PipelineError("YouTube source must be a video URL or 11-character video id")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif host == "youtube.com" or host.endswith(".youtube.com"):
        parts = [item for item in parsed.path.split("/") if item]
        if parsed.path.rstrip("/") == "/watch":
            video_id = (parse_qs(parsed.query).get("v") or [""])[0]
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            video_id = parts[1]
        else:
            video_id = ""
    elif host == "youtube-nocookie.com" or host.endswith(".youtube-nocookie.com"):
        parts = [item for item in parsed.path.split("/") if item]
        video_id = parts[1] if len(parts) >= 2 and parts[0] == "embed" else ""
    else:
        video_id = ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise PipelineError("Cannot extract an 11-character YouTube video id")
    return video_id


def fetch_youtube_transcript(video_id: str, languages: list[str]) -> Any:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise PipelineError(
            "youtube-transcript-api is unavailable; install it with 'uv pip install youtube-transcript-api'"
        ) from exc
    try:
        transcripts = list(YouTubeTranscriptApi().list(video_id))
    except Exception as exc:
        raise PipelineError(f"YouTube transcript lookup failed: {exc}") from exc
    if not transcripts:
        raise PipelineError("YouTube returned no transcripts for this video")
    selected = next(
        (item for language in languages for item in transcripts if item.language_code == language),
        next((item for item in transcripts if not item.is_generated), transcripts[0]),
    )
    try:
        return selected.fetch()
    except Exception as exc:
        raise PipelineError(f"YouTube transcript fetch failed: {exc}") from exc


def command_youtube_transcript(args: argparse.Namespace) -> None:
    video_id = extract_youtube_video_id(args.url)
    languages = [code.strip() for value in args.language for code in value.split(",") if code.strip()]
    transcript = fetch_youtube_transcript(video_id, languages)
    segments = []
    for index, snippet in enumerate(transcript, 1):
        start, end = validate_segment_times(
            snippet.start,
            snippet.start + snippet.duration,
            f"YouTube transcript segment {index}",
        )
        text = clean_text(snippet.text)
        if text:
            segments.append({"start": start, "end": end, "text": text})
    if not segments:
        raise PipelineError("YouTube transcript contains no usable text")
    language_code = clean_text(getattr(transcript, "language_code", ""))
    write_json(
        Path(args.out).expanduser().resolve(),
        {
            "schema_version": SCHEMA_VERSION,
            "provider": "youtube-transcript-api",
            "source_url": args.url,
            "video_id": video_id,
            "language": language_code,
            "is_generated": bool(getattr(transcript, "is_generated", False)),
            "used_language_fallback": bool(languages and language_code not in languages),
            "segments": segments,
        },
    )
    print(Path(args.out).expanduser().resolve())


def parse_json_segments(path: Path) -> tuple[list[dict[str, Any]], str]:
    value = read_json(path)
    raw_segments = value.get("segments")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise PipelineError(f"Transcript JSON requires a non-empty segments array: {path}")
    segments = []
    for index, item in enumerate(raw_segments, 1):
        if not isinstance(item, dict):
            raise PipelineError(f"Transcript segment {index} must be an object")
        start_value = item.get("start")
        end_value = item.get("end")
        if end_value is None and finite_number(start_value) and finite_number(item.get("duration")):
            end_value = float(start_value) + float(item["duration"])
        start, end = validate_segment_times(start_value, end_value, f"Transcript segment {index}")
        text = clean_text(item.get("text"))
        if not text:
            continue
        segments.append({"start": start, "end": end, "text": text})
    if not segments:
        raise PipelineError(f"Transcript contains no usable text: {path}")
    return segments, clean_text(value.get("language") or value.get("language_code"))


def parse_timestamp(value: str) -> float:
    match = re.fullmatch(r"(?:(\d{1,2}):)?([0-5]?\d):([0-5]\d)[,.](\d{3})", value.strip())
    if not match:
        raise PipelineError(f"Invalid subtitle timestamp: {value!r}")
    hours = int(match.group(1) or 0)
    minutes, seconds, milliseconds = (int(part) for part in match.groups()[1:])
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def parse_subtitle_segments(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    text = re.sub(r"^WEBVTT[^\n]*\n+", "", text)
    blocks = re.split(r"\n{2,}", text.strip())
    segments = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((index for index, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        start_raw, end_raw = (part.strip().split()[0] for part in lines[timing_index].split("-->", 1))
        start = parse_timestamp(start_raw)
        end = parse_timestamp(end_raw)
        content = clean_text(" ".join(re.sub(r"<[^>]+>", "", line) for line in lines[timing_index + 1 :]))
        if content:
            start, end = validate_segment_times(start, end, f"Subtitle cue {len(segments) + 1}")
            segments.append({"start": start, "end": end, "text": content})
    if not segments:
        raise PipelineError(f"Subtitle contains no usable cues: {path}")
    return segments


def normalized_comparison_text(text: str) -> str:
    return "".join(character.lower() for character in text if character.isalnum())


def dominant_script(text: str) -> str:
    cjk = sum("\u3400" <= character <= "\u9fff" for character in text)
    latin = sum(character.isascii() and character.isalpha() for character in text)
    if cjk > latin:
        return "cjk"
    if latin > cjk:
        return "latin"
    return "mixed"


def temporal_overlap(first: dict[str, Any], second: dict[str, Any]) -> float:
    return max(0.0, min(float(first["end"]), float(second["end"])) - max(float(first["start"]), float(second["start"])))


def resolve_segments(
    transcript: list[dict[str, Any]] | None,
    subtitles: list[dict[str, Any]] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if subtitles is None:
        resolved = [dict(item, source="transcript") for item in transcript or []]
        return resolved, []
    resolved = [dict(item, source="subtitle") for item in subtitles]
    conflicts = []
    for transcript_item in transcript or []:
        overlaps = [item for item in subtitles if temporal_overlap(transcript_item, item) > 0]
        if not overlaps:
            resolved.append(dict(transcript_item, source="transcript_fill"))
            continue
        subtitle_text = clean_text(" ".join(item["text"] for item in overlaps))
        if dominant_script(subtitle_text) != dominant_script(transcript_item["text"]):
            continue
        left = normalized_comparison_text(transcript_item["text"])
        right = normalized_comparison_text(subtitle_text)
        if left and right and SequenceMatcher(None, left, right).ratio() < 0.25:
            conflicts.append(
                {
                    "start": transcript_item["start"],
                    "end": transcript_item["end"],
                    "transcript": transcript_item["text"],
                    "subtitle": subtitle_text,
                }
            )
    resolved.sort(key=lambda item: (float(item["start"]), float(item["end"]), item["source"]))
    return resolved, conflicts


def run_asr(video: Path, output_dir: Path, language: str, asr_script: Path) -> Path:
    if not video.is_file():
        raise PipelineError(f"Video is missing: {video}")
    if not asr_script.is_file() or not os.access(asr_script, os.X_OK):
        raise PipelineError(f"Shared ASR dispatcher is unavailable: {asr_script}")
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(asr_script),
        "transcribe-faster",
        str(video),
        "--output-dir",
        str(output_dir),
    ]
    if language and language != "auto":
        command.extend(("--language", language))
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        raise PipelineError(f"Shared ASR failed with exit code {exc.returncode}; request a fallback decision") from exc
    result = output_dir / f"{video.stem}.transcript.json"
    if not result.is_file():
        raise PipelineError(f"Shared ASR did not create {result}")
    return result


def media_job_id(value: str) -> str:
    if MEDIA_JOB_ID_RE.fullmatch(value):
        return value
    if not value.strip():
        raise PipelineError("--job-id cannot be empty")
    return "hf-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]


def command_acquire(args: argparse.Namespace) -> None:
    profile = Path(args.profile).expanduser() if args.profile else None
    materials_arg = Path(args.materials_dir).expanduser()
    if profile is None or profile.is_symlink() or not profile.is_file():
        raise PipelineError("Provide a regular trendradar-media profile with --profile or TRENDRADAR_MEDIA_PROFILE")
    if materials_arg.is_symlink() or not materials_arg.is_dir():
        raise PipelineError(f"Materials directory is missing or a symlink: {materials_arg}")
    job_id = media_job_id(args.job_id)
    if not MEDIA_JOB_ID_RE.fullmatch(args.source_id):
        raise PipelineError("--source-id must use 1-64 safe characters")
    parsed_url = urlparse(args.url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc or parsed_url.username or parsed_url.password:
        raise PipelineError("--url must be a credential-free HTTP(S) URL")
    downloader = shutil.which(args.downloader)
    if not downloader:
        raise PipelineError(f"trendradar-media executable is unavailable: {args.downloader}")
    if args.timeout <= 0:
        raise PipelineError("--timeout must be positive")

    materials = materials_arg.resolve()
    request = {
        "schema_version": "2.0",
        "job_id": job_id,
        "sources": [{"source_id": args.source_id, "url": args.url}],
    }
    if args.platform:
        request["sources"][0]["platform"] = args.platform
    fd, request_name = tempfile.mkstemp(prefix=".trendradar-request.", suffix=".json", dir=materials)
    os.close(fd)
    request_path = Path(request_name)
    try:
        write_json(request_path, request)
        try:
            completed = subprocess.run(
                [downloader, "--profile", str(profile.resolve()), "fetch", "--request", str(request_path)],
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PipelineError("trendradar-media is unavailable or timed out") from exc
    finally:
        request_path.unlink(missing_ok=True)

    try:
        envelope = json.loads(completed.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise PipelineError("trendradar-media returned an invalid JSON envelope") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "2.0":
        raise PipelineError("trendradar-media envelope contract mismatch")
    if completed.returncode != 0 or envelope.get("exit_code") != 0 or envelope.get("status") != "succeeded":
        error = envelope.get("error")
        code = error.get("code") if isinstance(error, dict) else envelope.get("status")
        raise PipelineError(f"trendradar-media fetch failed: {code or 'unknown_error'}")
    if envelope.get("job_id") != job_id or envelope.get("succeeded") != 1 or envelope.get("failed") != 0:
        raise PipelineError("trendradar-media returned an unexpected single-source result")

    manifest = Path(str(envelope.get("manifest_ref") or ""))
    if not manifest.is_absolute() or manifest.is_symlink() or not manifest.is_file():
        raise PipelineError("trendradar-media manifest_ref is missing or unsafe")
    try:
        rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError("trendradar-media manifest is unreadable") from exc
    if len(rows) != 1 or not isinstance(rows[0], dict):
        raise PipelineError("trendradar-media manifest must contain exactly one item")
    row = rows[0]
    source_path = Path(str(row.get("local_media_path") or ""))
    expected_size = row.get("media_size_bytes")
    expected_hash = row.get("media_hash")
    if (
        row.get("source_id") != args.source_id
        or row.get("source_url") != args.url
        or row.get("platform") not in {"douyin", "youtube", "bilibili", "direct"}
        or row.get("media_type") != "video"
        or row.get("download_status") != "succeeded"
        or not source_path.is_absolute()
        or source_path.is_symlink()
        or not source_path.is_file()
        or not isinstance(expected_size, int)
        or expected_size <= 0
        or source_path.stat().st_size != expected_size
        or expected_hash != f"sha256:{sha256(source_path)}"
    ):
        raise PipelineError("trendradar-media success item failed local verification")

    receipt_path = materials / "acquisition.json"
    if receipt_path.is_symlink():
        raise PipelineError("Refusing to replace a symlinked acquisition receipt")
    if receipt_path.is_file():
        existing = read_json(receipt_path)
        if existing.get("source_url") != args.url:
            raise PipelineError("This Variant is already bound to a different source URL")
    suffix = source_path.suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
        suffix = ".mp4"
    target = materials / f"source-video{suffix}"
    other_targets = [path for path in materials.glob("source-video.*") if path != target]
    if other_targets:
        raise PipelineError("Materials already contains a different source-video file")
    if target.is_symlink():
        raise PipelineError("Refusing to replace a symlinked source-video file")
    if target.exists() and not target.is_file():
        raise PipelineError("Materials source-video path is not a regular file")
    media_digest = sha256(source_path)
    if target.is_file() and sha256(target) != media_digest:
        raise PipelineError("Materials already contains a different source video")
    if not target.exists():
        fd, temporary_name = tempfile.mkstemp(prefix=".source-video.", suffix=suffix, dir=materials)
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            shutil.copy2(source_path, temporary)
            if temporary.stat().st_size != expected_size or sha256(temporary) != media_digest:
                raise PipelineError("Adopted media failed copy verification")
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    write_json(
        receipt_path,
        {
            "schema_version": SCHEMA_VERSION,
            "workflow": WORKFLOW,
            "provider": "trendradar-media",
            "provider_contract": "2.0",
            "job_id": job_id,
            "source_id": args.source_id,
            "source_url": args.url,
            "platform": row.get("platform"),
            "completed_at": envelope.get("completed_at"),
            "external_expires_at": envelope.get("expires_at"),
            "media": {"path": target.name, "size_bytes": expected_size, "sha256": media_digest},
        },
    )
    print(target)


def command_resolve(args: argparse.Namespace) -> None:
    transcript_path = Path(args.transcript).expanduser().resolve() if args.transcript else None
    subtitle_path = Path(args.subtitle).expanduser().resolve() if args.subtitle else None
    if transcript_path is None and subtitle_path is None and args.run_asr:
        if not args.video:
            raise PipelineError("--video is required with --run-asr")
        video = Path(args.video).expanduser().resolve()
        transcript_path = run_asr(
            video,
            Path(args.asr_output_dir).expanduser().resolve(),
            args.language,
            Path(args.asr_script).expanduser().resolve(),
        )
    if transcript_path is None and subtitle_path is None:
        raise PipelineError("Provide --transcript or --subtitle, or explicitly use --run-asr")

    transcript, language = parse_json_segments(transcript_path) if transcript_path else (None, "")
    if subtitle_path and subtitle_path.suffix.lower() == ".json":
        subtitles, subtitle_language = parse_json_segments(subtitle_path)
    else:
        subtitles = parse_subtitle_segments(subtitle_path) if subtitle_path else None
        subtitle_language = ""
    resolved, conflicts = resolve_segments(transcript, subtitles)
    canonical = []
    for index, item in enumerate(resolved, 1):
        canonical.append({"id": f"s{index:06d}", **item})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workflow": WORKFLOW,
        "status": "needs_review" if conflicts else "ready",
        "language": language or subtitle_language or args.language,
        "inputs": {
            "transcript": (
                {"name": transcript_path.name, "sha256": sha256(transcript_path)} if transcript_path else None
            ),
            "subtitle": ({"name": subtitle_path.name, "sha256": sha256(subtitle_path)} if subtitle_path else None),
        },
        "segments": canonical,
        "conflicts": conflicts,
    }
    output = Path(args.out).expanduser().resolve()
    write_json(output, payload)
    print(output)


def transcript_index(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    transcript = read_json(path)
    if transcript.get("schema_version") != SCHEMA_VERSION or transcript.get("workflow") != WORKFLOW:
        raise PipelineError("Transcript contract mismatch")
    if transcript.get("status") != "ready":
        raise PipelineError("Transcript is not ready; resolve conflicts before article planning")
    raw_segments = transcript.get("segments")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise PipelineError("Transcript requires non-empty segments")
    index = {}
    prior_start = -1.0
    for item in raw_segments:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise PipelineError("Transcript segment contract is invalid")
        if item["id"] in index or not clean_text(item.get("text")):
            raise PipelineError(f"Transcript segment id is duplicate or text is empty: {item['id']}")
        start, end = validate_segment_times(item.get("start"), item.get("end"), item["id"])
        if start < prior_start - 0.001:
            raise PipelineError("Transcript segments must be time ordered")
        prior_start = start
        index[item["id"]] = item
    return transcript, index


def validate_candidates(transcript_path: Path, candidates_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _, segments = transcript_index(transcript_path)
    value = read_json(candidates_path)
    if value.get("schema_version") != SCHEMA_VERSION or value.get("workflow") != WORKFLOW:
        raise PipelineError("Article candidate contract mismatch")
    if value.get("transcript_sha256") != sha256(transcript_path):
        raise PipelineError("Article candidates target a different transcript")
    candidates = value.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        raise PipelineError("Article planning must provide exactly 3 candidates")
    ids: set[str] = set()
    ranks: set[int] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise PipelineError("Each article candidate must be an object")
        candidate_id = candidate.get("id")
        rank = candidate.get("rank")
        if not isinstance(candidate_id, str) or not ID_RE.fullmatch(candidate_id) or candidate_id in ids:
            raise PipelineError(f"Invalid or duplicate candidate id: {candidate_id!r}")
        if not isinstance(rank, int) or rank not in range(1, 4) or rank in ranks:
            raise PipelineError(f"Invalid or duplicate candidate rank: {rank!r}")
        for field in ("core_viewpoint", "audience_tension", "rationale"):
            if not clean_text(candidate.get(field)):
                raise PipelineError(f"Candidate {candidate_id} requires {field}")
        images = candidate.get("images")
        if not isinstance(images, list) or len(images) not in range(4, 9):
            raise PipelineError(f"Candidate {candidate_id} must contain 4 to 8 image groups")
        used_segments: set[str] = set()
        previous_image_start = -1.0
        for image_index, image in enumerate(images, 1):
            image_id = f"g{image_index:02d}"
            if not isinstance(image, dict) or image.get("id") != image_id:
                raise PipelineError(f"Candidate {candidate_id} image {image_index} must be {image_id}")
            if not clean_text(image.get("structural_role")) or not clean_text(image.get("focus")):
                raise PipelineError(f"Candidate {candidate_id}/{image_id} requires structural_role and focus")
            units = image.get("units")
            if not isinstance(units, list) or len(units) not in {4, 5}:
                raise PipelineError(f"Candidate {candidate_id}/{image_id} requires 1 Hero and 3 or 4 supports")
            previous_unit_start = -1.0
            image_start = None
            for unit_index, unit in enumerate(units, 1):
                unit_id = f"u{unit_index:02d}"
                if not isinstance(unit, dict) or unit.get("id") != unit_id:
                    raise PipelineError(f"Candidate {candidate_id}/{image_id} unit {unit_index} must be {unit_id}")
                if not clean_text(unit.get("original")) or not clean_text(unit.get("translation_zh")):
                    raise PipelineError(f"Candidate {candidate_id}/{image_id}/{unit_id} requires bilingual text")
                source_ids = unit.get("source_segment_ids")
                if (
                    not isinstance(source_ids, list)
                    or not source_ids
                    or not all(isinstance(item, str) and item in segments for item in source_ids)
                ):
                    raise PipelineError(f"Candidate {candidate_id}/{image_id}/{unit_id} has invalid source ids")
                if used_segments.intersection(source_ids):
                    raise PipelineError(f"Candidate {candidate_id} reuses a source segment")
                used_segments.update(source_ids)
                unit_start = min(float(segments[item]["start"]) for item in source_ids)
                if unit_start < previous_unit_start:
                    raise PipelineError(f"Candidate {candidate_id}/{image_id} units must follow source order")
                previous_unit_start = unit_start
                image_start = unit_start if image_start is None else min(image_start, unit_start)
            if image_start is None or image_start < previous_image_start:
                raise PipelineError(f"Candidate {candidate_id} images must follow source order")
            previous_image_start = image_start
        ids.add(candidate_id)
        ranks.add(rank)
    if ranks != {1, 2, 3}:
        raise PipelineError("Candidate ranks must be exactly 1 through 3")
    return value, candidates


def command_validate_candidates(args: argparse.Namespace) -> None:
    validate_candidates(Path(args.transcript).resolve(), Path(args.candidates).resolve())
    print("ok: article candidates")


def command_approve(args: argparse.Namespace) -> None:
    transcript_path = Path(args.transcript).expanduser().resolve()
    candidates_path = Path(args.candidates).expanduser().resolve()
    _, candidates = validate_candidates(transcript_path, candidates_path)
    by_id = {item["id"]: item for item in candidates}
    if args.select not in by_id:
        raise PipelineError("Selected article candidate does not exist")
    selected = by_id[args.select]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workflow": WORKFLOW,
        "status": "approved",
        "approved_at": now(),
        "transcript_sha256": sha256(transcript_path),
        "candidates_sha256": sha256(candidates_path),
        "selected_id": selected["id"],
        "core_viewpoint": selected["core_viewpoint"],
        "audience_tension": selected["audience_tension"],
        "rationale": selected["rationale"],
        "groups": selected["images"],
    }
    output = Path(args.out).expanduser().resolve()
    write_json(output, payload)
    print(output)


def validate_selection(transcript_path: Path, selection_path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    _, segments = transcript_index(transcript_path)
    selection = read_json(selection_path)
    if selection.get("schema_version") != SCHEMA_VERSION or selection.get("workflow") != WORKFLOW:
        raise PipelineError("Article selection contract mismatch")
    if selection.get("status") != "approved" or selection.get("transcript_sha256") != sha256(transcript_path):
        raise PipelineError("Article selection is not approved for the current transcript")
    groups = selection.get("groups")
    if not isinstance(groups, list) or len(groups) not in range(4, 9):
        raise PipelineError("Approved article requires 4 to 8 image groups")
    for index, group in enumerate(groups, 1):
        if not isinstance(group, dict) or group.get("id") != f"g{index:02d}":
            raise PipelineError("Approved image groups must be ordered g01 through g08")
        if not isinstance(group.get("units"), list) or len(group["units"]) not in {4, 5}:
            raise PipelineError(f"{group.get('id')} requires 1 Hero and 3 or 4 supports")
    return selection, segments


def command_align(args: argparse.Namespace) -> None:
    transcript_path = Path(args.transcript).expanduser().resolve()
    selection_path = Path(args.selection).expanduser().resolve()
    selection, segments = validate_selection(transcript_path, selection_path)
    groups = []
    for group in selection["groups"]:
        units = []
        for unit in group["units"]:
            source = [segments[item] for item in unit["source_segment_ids"]]
            units.append(
                {
                    **unit,
                    "start": round(min(float(item["start"]) for item in source), 3),
                    "end": round(max(float(item["end"]) for item in source), 3),
                }
            )
        groups.append(
            {
                "id": group["id"],
                "structural_role": group["structural_role"],
                "focus": group["focus"],
                "start": units[0]["start"],
                "end": units[-1]["end"],
                "units": units,
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workflow": WORKFLOW,
        "selection_sha256": sha256(selection_path),
        "groups": groups,
    }
    output = Path(args.out).expanduser().resolve()
    write_json(output, payload)
    print(output)


def ffmpeg_executable() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise PipelineError("ffmpeg is required")
    return executable


def extract_frame(video: Path, seconds: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp.jpg")
    command = [
        ffmpeg_executable(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{seconds:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        str(temporary),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        with Image.open(temporary) as image:
            image.verify()
        os.replace(temporary, output)
    except (subprocess.CalledProcessError, OSError) as exc:
        temporary.unlink(missing_ok=True)
        raise PipelineError(f"Frame extraction failed at {seconds:.3f}s") from exc


def contact_sheet(paths: list[Path], output: Path, columns: int = 3) -> None:
    thumb_w, thumb_h = 320, 180
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * thumb_h), "#111111")
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            thumb = ImageOps.fit(source.convert("RGB"), (thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % columns) * thumb_w, (index // columns) * thumb_h))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=90, subsampling=0)


def command_extract(args: argparse.Namespace) -> None:
    video = Path(args.video).expanduser().resolve()
    if not video.is_file():
        raise PipelineError(f"Video is missing: {video}")
    aligned_path = Path(args.aligned).expanduser().resolve()
    aligned = read_json(aligned_path)
    if aligned.get("schema_version") != SCHEMA_VERSION or aligned.get("workflow") != WORKFLOW:
        raise PipelineError("Aligned article contract mismatch")
    groups = aligned.get("groups")
    if not isinstance(groups, list) or len(groups) not in range(4, 9):
        raise PipelineError("Aligned article requires 4 to 8 image groups")
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    candidate_groups = []
    for group in groups:
        group_paths = []
        units = []
        for unit in group["units"]:
            start, end = validate_segment_times(unit.get("start"), unit.get("end"), f"{group['id']}/{unit['id']}")
            duration = end - start
            candidates = []
            for frame_index, fraction in enumerate((0.25, 0.5, 0.75), 1):
                seconds = start + duration * fraction
                frame_id = f"{group['id']}-{unit['id']}-f{frame_index:02d}"
                relative = Path(group["id"]) / unit["id"] / f"f{frame_index:02d}.jpg"
                path = out_dir / relative
                extract_frame(video, seconds, path)
                group_paths.append(path)
                candidates.append(
                    {
                        "id": frame_id,
                        "time": round(seconds, 3),
                        "path": relative.as_posix(),
                        "sha256": sha256(path),
                    }
                )
            units.append({"id": unit["id"], "candidates": candidates})
        sheet = out_dir / group["id"] / "contact-sheet.jpg"
        contact_sheet(group_paths, sheet)
        candidate_groups.append(
            {
                "id": group["id"],
                "contact_sheet": sheet.relative_to(out_dir).as_posix(),
                "units": units,
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workflow": WORKFLOW,
        "video": {"name": video.name, "sha256": sha256(video)},
        "aligned_sha256": sha256(aligned_path),
        "groups": candidate_groups,
    }
    output = out_dir / "frame-candidates.json"
    write_json(output, payload)
    print(output)


def frame_candidate_index(path: Path) -> tuple[dict[str, Any], dict[str, tuple[str, str, dict[str, Any]]]]:
    value = read_json(path)
    if value.get("schema_version") != SCHEMA_VERSION or value.get("workflow") != WORKFLOW:
        raise PipelineError("Frame candidate contract mismatch")
    index = {}
    for group in value.get("groups") or []:
        for unit in group.get("units") or []:
            for candidate in unit.get("candidates") or []:
                index[candidate["id"]] = (group["id"], unit["id"], candidate)
    return value, index


def command_choose_frames(args: argparse.Namespace) -> None:
    candidates_path = Path(args.candidates).expanduser().resolve()
    value, index = frame_candidate_index(candidates_path)
    expected = {
        (group["id"], unit["id"])
        for group in value["groups"]
        for unit in group["units"]
    }
    chosen = {}
    for frame_id in args.choice:
        if frame_id not in index:
            raise PipelineError(f"Unknown frame candidate: {frame_id}")
        group_id, unit_id, candidate = index[frame_id]
        key = (group_id, unit_id)
        if key in chosen:
            raise PipelineError(f"Choose exactly one frame for {group_id}/{unit_id}")
        chosen[key] = candidate
    if set(chosen) != expected:
        missing = sorted(f"{group}/{unit}" for group, unit in expected - set(chosen))
        raise PipelineError(f"Frame selection is incomplete: {missing}")
    groups = []
    for group in value["groups"]:
        groups.append(
            {
                "id": group["id"],
                "units": [
                    {
                        "id": unit["id"],
                        "frame_id": chosen[(group["id"], unit["id"])]["id"],
                        "time": chosen[(group["id"], unit["id"])]["time"],
                        "path": chosen[(group["id"], unit["id"])]["path"],
                        "sha256": chosen[(group["id"], unit["id"])]["sha256"],
                    }
                    for unit in group["units"]
                ],
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workflow": WORKFLOW,
        "frame_candidates_sha256": sha256(candidates_path),
        "aligned_sha256": value.get("aligned_sha256"),
        "video": value.get("video"),
        "frames_root": str(candidates_path.parent),
        "groups": groups,
    }
    output = Path(args.out).expanduser().resolve()
    write_json(output, payload)
    print(output)


def resolve_font(explicit: str | None) -> Path:
    candidates = (Path(explicit).expanduser().resolve(),) if explicit else FONT_CANDIDATES
    for path in candidates:
        if path.is_file():
            try:
                ImageFont.truetype(str(path), 32)
            except OSError:
                continue
            return path
    raise PipelineError("No supported CJK font found; install Noto Sans CJK SC, Source Han Sans SC, or Microsoft YaHei")


def line_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke: int) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    return right - left


def line_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke: int) -> int:
    _, top, _, bottom = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    return bottom - top


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    max_lines: int,
    stroke: int,
) -> list[str] | None:
    text = clean_text(text)
    lines: list[str] = []
    remaining = text
    while remaining:
        if line_width(draw, remaining, font, stroke) <= max_width:
            lines.append(remaining)
            break
        best = 0
        for index in range(1, len(remaining) + 1):
            if line_width(draw, remaining[:index], font, stroke) <= max_width:
                best = index
            else:
                break
        if best == 0:
            return None
        space = remaining.rfind(" ", 0, best + 1)
        if space > 0 and best - space < max(6, best // 3):
            best = space
        lines.append(remaining[:best].rstrip())
        remaining = remaining[best:].lstrip()
        if len(lines) >= max_lines and remaining:
            return None
    return lines if len(lines) <= max_lines else None


def text_layout(
    draw: ImageDraw.ImageDraw,
    zh: str,
    original: str,
    font_path: Path,
    max_width: int,
    max_height: int,
    hero: bool,
) -> dict[str, Any]:
    zh_max, zh_min = ((76, 48) if hero else (56, 36))
    original_max, original_min = ((38, 24) if hero else (28, 20))
    stroke = 4 if hero else 3
    for zh_size in range(zh_max, zh_min - 1, -2):
        original_size = max(original_min, min(original_max, round(zh_size * 0.5)))
        zh_font = ImageFont.truetype(str(font_path), zh_size)
        original_font = ImageFont.truetype(str(font_path), original_size)
        zh_lines = wrap_text(draw, zh, zh_font, max_width, 2, stroke)
        original_lines = wrap_text(draw, original, original_font, max_width, 2, max(1, stroke - 1))
        if zh_lines is None or original_lines is None:
            continue
        zh_height = sum(line_height(draw, line, zh_font, stroke) for line in zh_lines)
        original_height = sum(
            line_height(draw, line, original_font, max(1, stroke - 1))
            for line in original_lines
        )
        line_gap = max(5, zh_size // 8)
        language_gap = max(8, zh_size // 5)
        total = zh_height + original_height + line_gap * (len(zh_lines) + len(original_lines) - 2) + language_gap
        if total <= max_height:
            return {
                "zh_font": zh_font,
                "original_font": original_font,
                "zh_lines": zh_lines,
                "original_lines": original_lines,
                "stroke": stroke,
                "line_gap": line_gap,
                "language_gap": language_gap,
                "height": total,
            }
    raise PipelineError("Bilingual text exceeds the readable layout capacity")


def draw_centered_line(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    stroke: int,
    width: int,
) -> int:
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    draw.text(
        ((width - text_width) // 2, y - box[1]),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke,
        stroke_fill="#050505",
    )
    return y + text_height


def render_panel(frame: Image.Image, size: tuple[int, int], zh: str, original: str, font: Path, hero: bool) -> Image.Image:
    width, height = size
    panel = ImageOps.fit(
        frame.convert("RGB"),
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.62 if hero else 0.72),
    )
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    horizontal_padding = round(width * 0.055)
    vertical_padding = round(height * (0.035 if hero else 0.06))
    maximum_height = round(height * (0.36 if hero else 0.82))
    layout = text_layout(
        draw,
        zh,
        original,
        font,
        width - 2 * horizontal_padding,
        maximum_height,
        hero,
    )
    block_top = height - layout["height"] - vertical_padding
    scrim_top = max(0, block_top - vertical_padding)
    draw.rectangle((0, scrim_top, width, height), fill=(0, 0, 0, 150 if hero else 165))
    y = block_top
    for line in layout["zh_lines"]:
        y = draw_centered_line(draw, y, line, layout["zh_font"], "#FFFFFF", layout["stroke"], width)
        y += layout["line_gap"]
    y += layout["language_gap"] - layout["line_gap"]
    for line in layout["original_lines"]:
        y = draw_centered_line(
            draw,
            y,
            line,
            layout["original_font"],
            "#E2E2E2",
            max(1, layout["stroke"] - 1),
            width,
        )
        y += layout["line_gap"]
    return Image.alpha_composite(panel.convert("RGBA"), overlay).convert("RGB")


def safe_title(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\n\r]+", "_", value).strip(" ._")
    return cleaned[:36] or "quote"


def markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def package_field(text: str, label: str) -> str:
    match = re.search(rf"^- {re.escape(label)}：\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return clean_text(match.group(1)) if match else ""


def validate_package(path: Path, group_ids: list[str]) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise PipelineError("PACKAGE.md is missing or empty")
    text = path.read_text(encoding="utf-8")
    missing_sections = [
        heading for heading in ("大标题", "开篇", "图片文案", "话题标签") if not markdown_section(text, heading)
    ]
    title = clean_text(markdown_section(text, "大标题"))
    image_copy = markdown_section(text, "图片文案")
    image_sections = re.findall(
        r"^### (g\d{2})[｜|]\s*(.+?)\s*$\n(.*?)(?=^### |\Z)",
        image_copy,
        flags=re.MULTILINE | re.DOTALL,
    )
    channel = package_field(text, "频道")
    source_url = package_field(text, "来源 URL")
    if missing_sections or not channel or not source_url or [item[0] for item in image_sections] != group_ids:
        raise PipelineError(
            "PACKAGE.md requires a title, opening, ordered copy for every image group, tags, channel, and source URL"
        )
    if len(title) > 20 or any(not clean_text(item[1]) or not clean_text(item[2]) for item in image_sections):
        raise PipelineError("PACKAGE.md title must be <=20 characters and every image needs a subtitle and body")
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PipelineError("PACKAGE.md 来源 URL must be an http(s) URL")


def final_contact_sheet(paths: list[Path], output: Path) -> None:
    columns = min(4, len(paths))
    thumb_w, thumb_h = 360, 480
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * thumb_h), "#111111")
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            thumb = ImageOps.fit(source.convert("RGB"), (thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % columns) * thumb_w, (index // columns) * thumb_h))
    sheet.save(output, quality=92, subsampling=0)


def command_render(args: argparse.Namespace) -> None:
    aligned_path = Path(args.aligned).expanduser().resolve()
    frames_path = Path(args.frames).expanduser().resolve()
    package_path = Path(args.package).expanduser().resolve()
    aligned = read_json(aligned_path)
    frames = read_json(frames_path)
    if aligned.get("schema_version") != SCHEMA_VERSION or aligned.get("workflow") != WORKFLOW:
        raise PipelineError("Aligned quote contract mismatch")
    if frames.get("schema_version") != SCHEMA_VERSION or frames.get("workflow") != WORKFLOW:
        raise PipelineError("Frame selection contract mismatch")
    if frames.get("aligned_sha256") != sha256(aligned_path):
        raise PipelineError("Frame selection targets a different aligned article")
    groups = aligned.get("groups")
    if not isinstance(groups, list) or len(groups) not in range(4, 9):
        raise PipelineError("Render requires 4 to 8 aligned image groups")
    validate_package(package_path, [group["id"] for group in groups])
    frame_groups = {group["id"]: group for group in frames.get("groups") or []}
    if set(frame_groups) != {group["id"] for group in groups}:
        raise PipelineError("Frame selection targets different image groups")
    frames_root = Path(frames.get("frames_root", "")).expanduser().resolve()
    font = resolve_font(args.font)
    out_dir = Path(args.out_dir).expanduser().resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise PipelineError(f"Render output directory must be empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for group_index, group in enumerate(groups, 1):
        selected_units = {unit["id"]: unit for unit in frame_groups[group["id"]]["units"]}
        if set(selected_units) != {unit["id"] for unit in group["units"]}:
            raise PipelineError(f"Incomplete frame selection for {group['id']}")
        out_width, out_height = 1440, 1920
        hero_height = round(out_height * 0.42)
        remaining = out_height - hero_height
        strip_count = len(group["units"]) - 1
        strip_heights = [remaining // strip_count] * strip_count
        strip_heights[-1] += remaining - sum(strip_heights)
        canvas = Image.new("RGB", (out_width, out_height), "black")
        y = 0
        for unit_index, unit in enumerate(group["units"]):
            frame_item = selected_units[unit["id"]]
            frame_path = frames_root / frame_item["path"]
            if not frame_path.is_file() or sha256(frame_path) != frame_item["sha256"]:
                raise PipelineError(f"Selected frame is missing or changed: {frame_item['path']}")
            height = hero_height if unit_index == 0 else strip_heights[unit_index - 1]
            with Image.open(frame_path) as source:
                panel = render_panel(
                    source,
                    (out_width, height),
                    clean_text(unit["translation_zh"]),
                    clean_text(unit["original"]),
                    font,
                    hero=unit_index == 0,
                )
            canvas.paste(panel, (0, y))
            y += height
        output = out_dir / f"{group_index:02d}_{safe_title(clean_text(group['units'][0]['translation_zh']))}.jpg"
        canvas.save(output, quality=93, subsampling=0)
        outputs.append(output)

    contact = out_dir / "final_contact_sheet.jpg"
    final_contact_sheet(outputs, contact)
    package_output = out_dir / "PACKAGE.md"
    shutil.copy2(package_path, package_output)
    artifacts = [
        {"path": path.name, "role": "image", "sha256": sha256(path)} for path in outputs
    ]
    artifacts.extend(
        [
            {"path": contact.name, "role": "contact_sheet", "sha256": sha256(contact)},
            {"path": package_output.name, "role": "package", "sha256": sha256(package_output)},
        ]
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "workflow": WORKFLOW,
        "qa": "pending_visual_review",
        "style": "podcast_stack_v1",
        "image_count": len(outputs),
        "dimensions": {"width": 1440, "height": 1920},
        "font": {"name": font.name, "path": str(font), "sha256": sha256(font)},
        "aligned_sha256": sha256(aligned_path),
        "frame_selection_sha256": sha256(frames_path),
        "artifacts": artifacts,
    }
    write_json(out_dir / "manifest.json", manifest)
    print(out_dir)


def verify_render(directory: Path) -> dict[str, Any]:
    manifest = read_json(directory / "manifest.json")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("workflow") != WORKFLOW:
        raise PipelineError("Render manifest contract mismatch")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise PipelineError("Render manifest requires artifacts")
    images = []
    roles: dict[str, int] = {}
    for item in artifacts:
        path = directory / item["path"]
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise PipelineError(f"Render artifact is missing, empty, or a symlink: {item['path']}")
        if sha256(path) != item.get("sha256"):
            raise PipelineError(f"Render artifact digest mismatch: {item['path']}")
        roles[item["role"]] = roles.get(item["role"], 0) + 1
        if item["role"] == "image":
            images.append(path)
    if len(images) not in range(4, 9) or roles.get("contact_sheet") != 1 or roles.get("package") != 1:
        raise PipelineError("Render requires 4 to 8 images, one contact sheet, and one package")
    for path in images:
        with Image.open(path) as image:
            if image.size != (1440, 1920) or image.format != "JPEG":
                raise PipelineError(f"Unexpected image geometry or format: {path.name}")
            image.verify()
    return manifest


def command_verify(args: argparse.Namespace) -> None:
    directory = Path(args.render_dir).expanduser().resolve()
    manifest = verify_render(directory)
    manifest["automated_checks"] = "passed"
    manifest["verified_at"] = now()
    manifest["qa"] = "passed" if args.visual_passed else "pending_visual_review"
    write_json(directory / "manifest.json", manifest)
    print(manifest["qa"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    acquire = commands.add_parser("acquire", help="Adopt one verified trendradar-media download")
    acquire.add_argument("--url", required=True)
    acquire.add_argument("--profile", default=os.environ.get("TRENDRADAR_MEDIA_PROFILE"))
    acquire.add_argument("--job-id", required=True)
    acquire.add_argument("--source-id", default="podcast-source")
    acquire.add_argument("--platform", choices=("douyin", "youtube", "bilibili", "direct"))
    acquire.add_argument("--materials-dir", required=True)
    acquire.add_argument("--downloader", default=os.environ.get("TRENDRADAR_MEDIA_COMMAND", "trendradar-media"))
    acquire.add_argument("--timeout", type=int, default=1200)
    acquire.set_defaults(handler=command_acquire)

    youtube_transcript = commands.add_parser(
        "youtube-transcript", help="Fetch one structured native YouTube transcript"
    )
    youtube_transcript.add_argument("--url", required=True)
    youtube_transcript.add_argument("--language", action="append", default=[])
    youtube_transcript.add_argument("--out", required=True)
    youtube_transcript.set_defaults(handler=command_youtube_transcript)

    resolve = commands.add_parser("resolve", help="Resolve transcript and structured subtitles")
    resolve.add_argument("--video")
    resolve.add_argument("--transcript")
    resolve.add_argument("--subtitle")
    resolve.add_argument("--language", default="auto")
    resolve.add_argument("--run-asr", action="store_true")
    resolve.add_argument("--asr-script", default=str(ASR_SCRIPT))
    resolve.add_argument("--asr-output-dir", default=".runtime/asr")
    resolve.add_argument("--out", required=True)
    resolve.set_defaults(handler=command_resolve)

    validate = commands.add_parser("validate-candidates", help="Validate three Agent-authored article candidates")
    validate.add_argument("--transcript", required=True)
    validate.add_argument("--candidates", required=True)
    validate.set_defaults(handler=command_validate_candidates)

    approve = commands.add_parser("approve", help="Record one user-approved article plan")
    approve.add_argument("--transcript", required=True)
    approve.add_argument("--candidates", required=True)
    approve.add_argument("--select", required=True)
    approve.add_argument("--out", required=True)
    approve.set_defaults(handler=command_approve)

    align = commands.add_parser("align", help="Map approved source segment ids to deterministic time spans")
    align.add_argument("--transcript", required=True)
    align.add_argument("--selection", required=True)
    align.add_argument("--out", required=True)
    align.set_defaults(handler=command_align)

    extract = commands.add_parser("extract", help="Extract three frame candidates per text unit")
    extract.add_argument("video")
    extract.add_argument("--aligned", required=True)
    extract.add_argument("--out-dir", required=True)
    extract.set_defaults(handler=command_extract)

    choose = commands.add_parser("choose-frames", help="Record one Agent-selected frame per text unit")
    choose.add_argument("--candidates", required=True)
    choose.add_argument("--choice", action="append", required=True)
    choose.add_argument("--out", required=True)
    choose.set_defaults(handler=command_choose_frames)

    render = commands.add_parser("render", help="Render the fixed bilingual 3:4 stack")
    render.add_argument("--aligned", required=True)
    render.add_argument("--frames", required=True)
    render.add_argument("--package", required=True)
    render.add_argument("--font")
    render.add_argument("--out-dir", required=True)
    render.set_defaults(handler=command_render)

    verify = commands.add_parser("verify", help="Run automated checks and record Agent visual QA")
    verify.add_argument("--render-dir", required=True)
    verify.add_argument("--visual-passed", action="store_true")
    verify.set_defaults(handler=command_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.handler(args)
    except (PipelineError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
