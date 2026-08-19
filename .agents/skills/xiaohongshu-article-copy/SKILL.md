---
name: xiaohongshu-article-copy
description: Research the guest behind one approved podcast article plan, write publish-ready Xiaohongshu Markdown, and render its drawn-subtitle image stack and local Final package.
---

# Xiaohongshu Article Copy

Continue one `podcast_quote_image` Work only after the user has approved exactly one `article-selection.json`. This Skill owns final copy and deterministic production. It does not reinterpret the transcript or offer new article directions.

## Start

1. In foreground mode, run `./work current`; in background mode, use the assigned Work and Variant IDs explicitly.
2. Confirm the Work uses `podcast_quote_image` and read only `article-selection.json`, the resolved transcript, acquisition metadata, `RESEARCH.md`, `PACKAGE.md`, and the machine artifacts needed by the current stage.
3. Reject a missing, stale, or unapproved selection. Do not fall back to an unapproved candidate.
4. Confirm the local video and selected frames are available. The workflow draws the approved Chinese subtitle text; embedded source subtitles are not required.

## Research The Guest

After article approval, verify the featured guest's identity from the source page or other reliable evidence. Research only background that explains the approved article's core viewpoint. Prefer primary sources, then reputable interviews or profiles; record direct links and distinguish the guest's own claims from independently verified facts.

Complete `RESEARCH.md` before writing `PACKAGE.md`:

```markdown
# 嘉宾背景调研

## 嘉宾身份
<verified name, role, and why this person is relevant>

## 与本文核心相关的经历
<only experiences that illuminate the approved viewpoint>

## 可用于开篇的背景故事
<one concise, sourced story arc>

## 事实边界
<uncertainty, self-reported claims, and details not safe to use>

## 来源
- [source title](https://example.com): <fact supported>
```

Do not turn biography into a general profile or use an unsourced anecdote. If the guest cannot be identified or the relevant background cannot be verified, run `./work wait source_metadata` and stop.

## Write Copy Before The Title

Draft the opening and image sections first. After the title is settled, write `PACKAGE.md` as publication-ready Markdown in this exact shape:

```markdown
# <final title, written last>

<summarize the article's core viewpoint and connect it to the guest's verified background story>

## <summary of the first image's passage>

<third-person copy>

## <summary of the second image's passage>

<third-person copy>

<podcast · guest · episode attribution>

原视频：<original video title>

<topic tags>
```

Do not emit structural labels such as `大标题`, `开篇`, `图片文案`, `播客信息`, or `话题标签`. Put a blank line after every heading and between sentences or paragraphs so the file can be published without cleanup. The opening states the core conclusion immediately, then uses the guest's relevant background story to explain why the viewpoint carries weight. Each H2 summarizes its approved image passage rather than adding a hook or a new claim. The H2 sections must cover every approved group once, in source order, with no extra section. Write in third person. Attribute viewpoints to the actual speaker; never impersonate the guest, invent first-person experience, or turn a faithful translation into a stronger claim.

Apply only the expression-efficiency and cognitive-gap checks from `dbs-content` to the opening, subtitles, and third-person copy; do not rerun format selection or its product-premise flow.

## Write The Title Last

After the full article is stable, use `dbs-xhs-title` to generate formula-traceable candidates. The final title must combine the article's core conclusion with the guest's most relevant verified identity or background signal, stay within 20 Chinese characters, and promise no more than the transcript and `RESEARCH.md` support.

Run `dbs-ai-check` on the completed title, opening, subtitles, and third-person copy, then fix only confirmed issues without touching the approved source quotes or translations. Do not use `dbs-hook` or `dbs-script-flow`.

Reuse `materials/acquisition.json` only to verify the source and use the verified research for guest metadata; verify the channel and original video title separately. Add episode or issue only when verified. End the publishable copy with `原视频：<original video title>` and do not include the source URL, because the target audience may not be able to open YouTube. If the channel or original video title is missing, run `./work wait source_metadata` and stop.

## Align And Choose Frames

Run `align`, then `extract`. Each approved article contains 4 to 8 image groups, and every image contains one Hero plus 3 or 4 supports. The script maps every unit's source segment IDs to time and extracts candidates at 25%, 50%, and 75% of its span.

Inspect each contact sheet. Choose one frame per unit with a clear expression, recognizable speaker, useful composition, and clean lower area for the workflow-drawn subtitle. Reject closed eyes, motion blur, awkward gestures, obstructive overlays, or a frame that contradicts the passage. Record choices with `choose-frames`; do not hand-edit timestamps or paths.

## Render And Verify

Run `render`. Every panel displays only the approved Chinese text at a fixed 42px size. Hero is fixed at 52% of the image; the 3 or 4 support strips fill the remaining 48% and divide it dynamically from their measured text heights. Horizontal padding tightens from 6% to no less than 3% only when needed for fit. The black text backdrop uses alpha 185, reducing transparency for clearer text. Every panel crops from the bottom edge of its selected video-frame image upward, and the support strips have no gaps. The workflow does not preserve or locate subtitles from the source video. Keep at least 40% of the full image free of subtitle text.

```bash
.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py render \
  --aligned <variant>/artifacts/aligned-quotes.json \
  --frames <variant>/frames/frame-selection.json \
  --package <variant>/PACKAGE.md --hero-fraction 0.52 \
  --out-dir <variant>/render
```

The article produces 4 to 8 images plus one contact sheet and the publish-ready `PACKAGE.md`.

Run `verify` without `--visual-passed`, inspect every image and the contact sheet, then rerun with `--visual-passed` only after checking fixed font sizing, dynamic strip heights, bottom-anchored crop, readability, ordering, and no truncation. Finalize with:

```bash
./work finalize <variant>/render --qa-passed
```

The approved article plan is the only content gate. Do not add a second Draft approval. Final is local and does not authorize publishing.
