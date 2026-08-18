---
name: xiaohongshu-article-copy
description: Turn one approved podcast article plan into the final Xiaohongshu title, opening, ordered per-image copy, frames, renders, and local Final package.
---

# Xiaohongshu Article Copy

Continue one `podcast_quote_image` Work only after the user has approved exactly one `article-selection.json`. This Skill owns final copy and deterministic production. It does not reinterpret the transcript or offer new article directions.

## Start

1. In foreground mode, run `./work current`; in background mode, use the assigned Work and Variant IDs explicitly.
2. Confirm the Work uses `podcast_quote_image` and read only `article-selection.json`, the resolved transcript, acquisition metadata, `PACKAGE.md`, and the machine artifacts needed by the current stage.
3. Reject a missing, stale, or unapproved selection. Do not fall back to an unapproved candidate.

## Write The Package

Generate `PACKAGE.md` in this exact order:

```markdown
# Package

## 大标题
<one final title>

## 开篇
<state whose central viewpoint this is, or name the audience predicament/emotion>

## 图片文案

### g01｜<image subtitle>
<third-person copy>

### g02｜<image subtitle>
<third-person copy>

## 播客信息
...

## 话题标签
...
```

The image sections must cover every approved group once, in `g01...g08` order, with no extra group. Write in third person. Attribute viewpoints to the actual speaker; never impersonate the guest, invent first-person experience, or turn a faithful translation into a stronger claim.

Use `dbs-xhs-title` to generate formula-traceable candidates and keep Top 1 at no more than 20 Chinese characters. Reject formulas that promise more than the source evidence supports. Apply only the expression-efficiency and cognitive-gap checks from `dbs-content`; do not rerun format selection or its product-premise flow. Run `dbs-ai-check` on the completed title, opening, subtitles, and third-person copy, then fix only confirmed issues without touching the approved source quotes or translations. Do not use `dbs-hook` or `dbs-script-flow`.

Reuse `materials/acquisition.json` for the source URL and verify the channel separately. Add guest, episode, or issue only when verified. If channel or source URL is missing, run `./work wait source_metadata` and stop.

## Align And Choose Frames

Run `align`, then `extract`. Each approved article contains 4 to 8 image groups, and every image contains one Hero plus 3 or 4 supports. The script maps every unit's source segment IDs to time and extracts candidates at 25%, 50%, and 75% of its span.

Inspect each contact sheet. Choose one frame per unit for a clear expression, recognizable speaker, useful composition, and room for text. Reject closed eyes, motion blur, awkward gestures, obstructive overlays, or a frame that contradicts the text. Record choices with `choose-frames`; do not hand-edit timestamps or paths.

## Render And Verify

Run `render`. Each 1440x1920 image uses a 42% Hero panel and 3 or 4 equal supporting panels. Chinese is primary and the original wording secondary. The article produces 4 to 8 images plus one contact sheet and `PACKAGE.md`.

Run `verify` without `--visual-passed`, inspect every image and the contact sheet, then rerun with `--visual-passed` only after checking fidelity, bilingual pairing, crop, readability, ordering, and no truncation. Finalize with:

```bash
./work finalize <variant>/render --qa-passed
```

The approved article plan is the only content gate. Do not add a second Draft approval. Final is local and does not authorize publishing.
