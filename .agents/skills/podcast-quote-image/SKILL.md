---
name: podcast-quote-image
description: Turn one local podcast or interview video into 3 or 4 bilingual Xiaohongshu quote images. Use when a Work has workflow podcast_quote_image, or when the user asks to resolve a transcript, select and translate podcast quotes, choose nearby frames, render the fixed stacked layout, or package this image-and-copy format.
---

# Podcast Quote Image

Build one `podcast_quote_image` Work from local media. Do not download media, publish, or run ASR unless the user explicitly authorizes that external/local model step.

## Start

1. Run `./work current`; if there is no Current Work, run `./work list` and do not guess.
2. Confirm `WORK.md` declares `"workflow":"podcast_quote_image"`. Otherwise create a new Work with `./work new "<title>" --workflow podcast_quote_image`.
3. Put the local video and any supplied transcript/subtitle in `materials/`; generated state belongs in `artifacts/`, `frames/`, `render/`, and `final/`.
4. Require one local video. Accept an optional structured transcript JSON and optional `.srt`, `.vtt`, or subtitle JSON.

## Resolve Transcript

Use `.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py resolve`; run its subcommand `--help` for exact flags. Structured subtitles own wording and timing; transcript segments only fill uncovered intervals. Clear same-language disagreement produces `status: needs_review` and must be resolved before selection.

Resolution order is: supplied structured transcript/subtitle, then explicitly authorized shared ASR. If neither is usable, or ASR is unavailable or fails, run `./work wait transcript_fallback`, explain the failure, and ask whether to use the vendored `native-subtitle-quote-image` fallback. Never switch silently.

## Select And Translate Quotes

Read the whole resolved `artifacts/transcript.json`. Author exactly 6 candidates in `artifacts/quote-candidates.json`:

```json
{
  "schema_version": 1,
  "workflow": "podcast_quote_image",
  "transcript_sha256": "<sha256>",
  "candidates": [{
    "id": "q01",
    "rank": 1,
    "rationale": "<why it matters to Chinese readers>",
    "units": [{
      "id": "u01",
      "original": "<faithful source wording>",
      "translation_zh": "<natural faithful Chinese>",
      "source_segment_ids": ["s000001"]
    }]
  }]
}
```

Each candidate is one coherent passage with exactly 5 chronological units: one hero quote and four supporting strips. Prefer growth, women's growth, reading, technology, and podcast insight that stands alone without invented context. Preserve the source meaning, names, numbers, uncertainty, and tone. Chinese is primary and the source language remains secondary; do not embellish, merge unrelated claims, or translate the entire transcript.

Validate the file, then show all 6 ranked candidates with their bilingual units and rationale. Stop for explicit user approval of exactly 3 or 4 candidate IDs. Record that decision with `approve`; it orders the strongest approved candidate first and the rest by source chronology.

## Align And Choose Frames

Run `align`, then `extract`. The script maps source segment IDs to time and extracts three nearby candidates at 25%, 50%, and 75% of every unit span.

Inspect each generated contact sheet or candidate frame. Choose one per unit for clear expression, recognizable speaker, good composition, and room for text. Reject closed eyes, motion blur, awkward gestures, overlays covering a key subject, or frames that contradict the quote. Record choices with `choose-frames`; do not calculate timestamps or edit image paths by hand.

## Package, Render, Verify

Complete `PACKAGE.md` with one Xiaohongshu title, body, podcast/channel, source URL, and tags. Add guest and episode only when verified. If source URL or channel is missing, run `./work wait source_metadata` and ask the user before Final.

Run `render`. The fixed `podcast_stack_v1` output is 1440x1920: a 42% hero panel plus four equal strips, with Chinese primary and original text secondary on every panel. The lower scrim may cover hard subtitles; if it hides a key subject, stop for a human fallback decision.

Run `verify` without `--visual-passed`, inspect every final image and the final contact sheet, then rerun with `--visual-passed` only after checking text fidelity, bilingual pairing, crop, readability, and no truncation. Finalize the verified directory with:

```bash
./work finalize <variant>/render --qa-passed
```

Do not add a second Draft approval gate after quote approval. Do not put speaker, episode, or source attribution on the images; those belong in `PACKAGE.md`.
