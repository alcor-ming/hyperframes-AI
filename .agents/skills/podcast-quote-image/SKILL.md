---
name: podcast-quote-image
description: Resolve one podcast or interview transcript, understand its argument and audience tension, and produce three evidence-backed Xiaohongshu article plans for human selection.
---

# Podcast Quote Planner

Prepare the transcript and one approved article plan for a `podcast_quote_image` Work. Download only through `trendradar-media`; do not publish or run ASR unless the user explicitly authorizes that local model step.

## Batch Background Mode

For multiple URLs, create one detached Work per source and dispatch each as an independent background task. Do not put multiple sources in one Work. A background task must receive its Work and Variant IDs, start with `./work --work <work-id> --variant <variant-id> status`, and pass both overrides to every lifecycle command; `Current Work` is foreground navigation only.

Different Works and workflows may run in parallel. Keep the shared ASR dispatcher single-instance, while verified downloads may overlap. One failed or waiting Work must not stop its siblings. Continue each podcast Work through acquisition, transcript resolution, and three article plans, then stop at `waiting_user/article_selection`. Do not add a daemon or shared Batch content directory to the Harness.

## Start

1. In foreground mode, run `./work current`; if there is no Current Work, run `./work list` and do not guess. In background mode, use the explicitly assigned Work and Variant IDs instead.
2. Confirm `WORK.md` declares `"workflow":"podcast_quote_image"`. Otherwise create a new Work with `./work new "<title>" --workflow podcast_quote_image`.
3. Put a supplied local video and any supplied transcript/subtitle in `materials/`; generated state belongs in `artifacts/`, `frames/`, `render/`, and `final/`.
4. Require either one local video or one explicit source URL. Accept an optional structured transcript JSON and optional `.srt`, `.vtt`, or subtitle JSON. The final renderer draws approved subtitle text over selected video frames; embedded source subtitles are not required.

## Acquire URL Media

For a URL, use the external `trendradar-media` v2.0 entry point. Require a regular local profile via `--profile` or `TRENDRADAR_MEDIA_PROFILE`; do not copy credentials or backend configuration into the Work.

Run its `healthcheck` before the first real use of a configured backend, then adopt the single source through this Skill's script:

```bash
trendradar-media --profile <profile.json> healthcheck
.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py acquire \
  --url <source-url> --profile <profile.json> --job-id <work-id> \
  --platform youtube --materials-dir <variant>/materials
```

A `partial` healthcheck is acceptable only when the requested platform's own check is `available`; unavailable unrelated backends do not block that source.

The adapter accepts only a successful v2.0 envelope and one successful manifest row, rechecks the external file size and SHA-256, then atomically copies it to `materials/source-video.*`. `materials/acquisition.json` retains source provenance and the adopted hash without retaining the expiring `manifest_ref` or external file path. Never use the downloader run-root path as the durable input.

If the command, profile, backend, manifest, or copied media is unavailable or invalid, run `./work wait external_asset`, report the stable downloader error, and stop for retry or a local-file decision. Do not call another downloader or silently accept an unverified path.

## Resolve Transcript

Use `.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py resolve`; run its subcommand `--help` for exact flags. Structured subtitles own wording and timing; transcript segments only fill uncovered intervals. Clear same-language disagreement produces `status: needs_review` and must be resolved before selection.

For YouTube, reuse the native-transcript fast path adapted from NousResearch's [youtube-content Skill](https://github.com/NousResearch/hermes-agent/blob/main/skills/media/youtube-content/SKILL.md) before shared ASR. `trendradar-media` remains the only media downloader. Install this Skill's declared requirements into the active Python environment before the first run:

```bash
python3 -m pip install --user --break-system-packages -r .agents/skills/podcast-quote-image/requirements.txt
```

Then run:

```bash
.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py youtube-transcript \
  --url <youtube-url> --language en,zh-Hans,zh-Hant \
  --out <variant>/materials/youtube-transcript.json
```

The adapter accepts standard, short, Shorts, embed, live, and raw video IDs; keeps structured segment timing; prefers requested languages; and records when it falls back to another available transcript. Validate non-empty text and actual language before `resolve`. Native transcript failure falls through to explicitly authorized shared ASR, not to a second media downloader.

For transcripts over roughly 50K characters, inspect overlapping windows of about 40K characters with 2K overlap, but keep the full canonical transcript unchanged. Candidate units must still cite original segment IDs; never select quotes from a summary.

`trendradar-media` supplies verified media, not a transcript. Resolution order is: supplied structured transcript/subtitle, native YouTube transcript when applicable, then explicitly authorized shared ASR against `materials/source-video.*`. If none is usable, or ASR is unavailable or fails, run `./work wait transcript_fallback`, explain the failure, and ask whether to use the vendored `native-subtitle-quote-image` fallback. Never switch silently.

After `artifacts/transcript.json` is ready, identify the guest and one concise article-level topic from the full transcript, then run `./work --work <work-id> --variant <variant-id> name "<guest>-<topic>"` before producing candidates. The CLI adds the per-workflow three-digit sequence. Do not rename the Work ID or use a platform video ID as the semantic name.

## Produce Article Plans

Read the whole resolved `artifacts/transcript.json`. Author exactly 3 complete article candidates in `artifacts/article-candidates.json`:

```json
{
  "schema_version": 1,
  "workflow": "podcast_quote_image",
  "transcript_sha256": "<sha256>",
  "candidates": [{
    "id": "a01",
    "rank": 1,
    "core_viewpoint": "<whose central viewpoint and what it is>",
    "audience_tension": "<the audience predicament or emotion>",
    "rationale": "<why it matters to Chinese readers>",
    "images": [{
      "id": "g01",
      "structural_role": "<setup|viewpoint|reasoning|example|contrast|payoff>",
      "focus": "<what this image contributes to the article>",
      "units": [{
        "id": "u01",
        "original": "<faithful source wording>",
        "translation_zh": "<natural faithful Chinese>",
        "source_segment_ids": ["s000001"]
      }]
    }]
  }]
}
```

Each candidate is one complete Xiaohongshu article direction containing 8 to 12 ordered image groups. Every image group contains exactly one Hero followed by enough supporting units to advance that beat; use complete short sentences of about 10 Chinese characters for both Hero and supports, with about 60 to 90 Chinese characters across the image. These are generation targets, not per-unit hard limits. Keep the English original faithful and similarly concise. A single argument may continue across two adjacent images, while its background, examples, and full reasoning stay available for the later article body through the group focus and cited transcript. Image boundaries follow the source passage's setup, viewpoint, reasoning, example, contrast, and payoff; they are not a sentence counter. Every unit must cite the source segments that justify both its wording and frame timing. A source segment may support multiple short units within one image or span two adjacent image groups, but no farther. Do not pad, merge unrelated claims, or split on punctuation mechanically.

Use `dbs-resonate` to ensure every image in a candidate serves one article-level core mechanism. Use only the audience emotion, effective stance, and first-spreader signals from `dbs-spread` to write each rationale and rank the three plans. DBS must not rewrite the original quote or its faithful translation.

Validate the file, then show the three article directions, their 8 to 12 image outlines, core viewpoint, audience tension, and rationale. Stop for explicit approval of exactly one article ID with `./work wait article_selection`. Record the decision with:

```bash
.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py approve \
  --transcript <variant>/artifacts/transcript.json \
  --candidates <variant>/artifacts/article-candidates.json \
  --select a01 --out <variant>/artifacts/article-selection.json
```

The approved `article-selection.json` is the only handoff to `xiaohongshu-article-copy`. Do not generate final title, opening, per-image copy, frames, or renders in this Skill.
