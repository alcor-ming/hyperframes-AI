---
name: xiaohongshu-article-copy
description: Research one approved podcast article, write and render its Xiaohongshu image note, and save an explicitly authorized Final to Xiaohongshu Creator drafts.
---

# Xiaohongshu Article Copy

Continue one `podcast_quote_image` Work only after the user has approved exactly one `article-selection.json`. This Skill owns final copy and deterministic production. It does not reinterpret the transcript or offer new article directions.

## Start

1. In foreground mode, run `./work current`; in background mode, use the assigned Work and Variant IDs explicitly.
2. Confirm the Work uses `podcast_quote_image` and read only `article-selection.json`, the resolved transcript, acquisition metadata, `RESEARCH.md`, `PACKAGE.md`, and the machine artifacts needed by the current stage.
3. Reject a missing, stale, or unapproved selection. Do not fall back to an unapproved candidate.
4. Confirm the local video and selected frames are available. The workflow draws the approved bilingual subtitle text; embedded source subtitles are not required.

## Research The Guest

After article approval, verify the featured guest's identity from the source page or other reliable evidence. Research only background that explains the approved article's core viewpoint. Prefer primary sources, then reputable interviews or profiles; record direct links and distinguish the guest's own claims from independently verified facts.

Complete `RESEARCH.md` before writing `PACKAGE.md`:

```markdown
# 嘉宾背景调研

## 嘉宾身份
<verified name, role, and why this person is relevant>

## 与本文核心相关的经历
<only experiences that illuminate the approved viewpoint>

## 可用于正文补充的背景信息
<one concise, sourced context block>

## 事实边界
<uncertainty, self-reported claims, and details not safe to use>

## 来源
- [source title](https://example.com): <fact supported>
```

Do not turn biography into a general profile or use an unsourced anecdote. If the guest cannot be identified or the relevant background cannot be verified, run `./work wait source_metadata` and stop.

## Write Copy Before The Title

Draft the opening and image sections first. After the title is settled, write `PACKAGE.md` as copy-ready plain text in this exact shape:

```text
<final title, written last>

<first paragraph: summarize the approved selected passages only>

<optional second paragraph: add verified guest context only when it helps explain the selected passages>

01｜<summary of the first image's passage>

<third-person copy>

02｜<summary of the second image's passage>

<third-person copy>

<podcast · guest · episode attribution>

原视频：<original video title>

<topic tags>
```

Do not emit Markdown headings or structural labels such as `大标题`, `开篇`, `图片文案`, `播客信息`, or `话题标签`. The first line is the platform title; the remaining copy already uses sequential `01｜小标题` sections and can be pasted directly into the body field. `render` separates the trailing tags into `topics` without otherwise reformatting the body. The title is at most 20 characters; body plus topics is at most 1000 characters; use 1 to 3 unique topics, each at most 30 characters. The opening's first paragraph must distill the shared conclusion, tension, or causal relationship in the approved selected passages only. It must not lead with guest identity, valuation, biography, or any fact that is absent from those passages. Verified guest context may appear from the second paragraph onward only when it clarifies the selected passages. Each numbered section summarizes its approved image passage rather than adding a hook or a new claim. The sections must cover every approved group once, in source order, with no extra section. Write in third person. Attribute viewpoints to the actual speaker; never impersonate the guest, invent first-person experience, or turn a faithful translation into a stronger claim.

For an intentionally designed cover, follow the cited Xiaohongshu image-copy guidance: keep the cover's main title to 3 to 7 Chinese characters and total cover copy within 15 characters, establish a clear title/subtitle/body hierarchy, use high contrast, and confirm readability at feed size. Those are cover rules, not limits for the platform title or note body; this quote-stack workflow does not invent a separate cover or shorten faithful quotes unless the user approves that content change. See [花叔的小红书图片设计调研](https://www.huasheng.ai/insights/xiaohongshu-image-design/) and the [official Creator platform](https://creator.xiaohongshu.com/).

DBS execution is required here; reading a DBS Skill or silently borrowing its rules does not count as using it.

1. Prepare a working draft without the first-line platform title: opening, every `01｜小标题` section, third-person copy, attribution, original-video title, and topics.
2. Invoke `dbs-content` as a separate diagnostic pass with the approved article direction, target platform, and the complete working draft. Restrict it to the title/cover, expression-efficiency, and cognitive-gap checks in Phase 3; do not rerun format selection, product-premise questions, or ask it to write the copy.
3. Require a concrete revision brief covering the opening, every numbered small heading, and its body. Then this Skill, which owns the copy, applies the supported revisions. A small heading must still summarize its approved passage rather than become an independent hook.

Do not write the final `PACKAGE.md` or proceed to the platform title until this `dbs-content` pass has been applied.

## Write The Title Last

After the opening, small headings, and body are stable, invoke `dbs-xhs-title` as a separate generation pass; reading its formula library does not count. Supply the shared conclusion, tension, or causal relationship from the approved passages as the topic, the article's actual audience/domain as the field, and the stable draft as supporting context. Require 5 to 8 candidates spanning at least 3 formula types, with a formula number for every candidate and a ranked Top 3. Select the strongest supported Top 1, then place only that title on the first line of `PACKAGE.md`.

The final title must stay within 20 Chinese characters and promise no more than the approved passages support. Do not use guest identity, valuation, biography, or external research as the title premise unless that information appears in the approved passages and is essential to their meaning. Do not run `dbs-xhs-title` on numbered small headings; those are passage summaries reviewed by `dbs-content`, not feed-click titles.

Finally, invoke `dbs-ai-check` as a separate diagnostic pass on the completed title, opening, small headings, subtitles, and third-person copy. This Skill applies only confirmed issues without touching the approved source quotes or translations. If the platform title needs substantive revision, return to the `dbs-xhs-title` pass instead of free-writing a replacement. Do not use `dbs-hook` or `dbs-script-flow`.

Reuse `materials/acquisition.json` only to verify the source and use the verified research for guest metadata; verify the channel and original video title separately. Add episode or issue only when verified. End the publishable copy with `原视频：<original video title>` and do not include the source URL, because the target audience may not be able to open YouTube. If the channel or original video title is missing, run `./work wait source_metadata` and stop.

## Align And Choose Frames

Run `align`, then `extract`. Each approved article contains 8 to 12 image groups. Every image contains one Hero followed by the short supporting sentences needed for that beat; a single source segment may support adjacent short units within one image or span two adjacent image groups. The script maps every unit's source segment IDs to time and extracts candidates at 25%, 50%, and 75% of its span.

Inspect each contact sheet. Choose one frame per unit with a clear expression, recognizable speaker, useful composition, and clean lower area for the workflow-drawn subtitle. Reject closed eyes, motion blur, awkward gestures, obstructive overlays, or a frame that contradicts the passage. Record choices with `choose-frames`; do not hand-edit timestamps or paths.

## Render And Verify

Run `render`. Every panel displays the approved bilingual text at fixed 50px Chinese and 30px English. Each support strip takes its measured bilingual text height plus up to 30px of visual room; long text reduces that room first, then tightens horizontal padding from 6% to no less than 3%, so Hero remains at or above 60%. Hero and support text backdrops use alpha 145 and 165 respectively. Every panel crops from the bottom edge of its selected video-frame image upward, and the support strips have no gaps. The workflow does not preserve or locate subtitles from the source video. Keep at least 40% of the full image free of subtitle text.

```bash
.agents/skills/podcast-quote-image/scripts/podcast_quote_pipeline.py render \
  --aligned <variant>/artifacts/aligned-quotes.json \
  --frames <variant>/frames/frame-selection.json \
  --package <variant>/PACKAGE.md --min-hero-fraction 0.60 \
  --out-dir <variant>/render
```

The article produces 8 to 12 images, one contact sheet, the copy-ready `PACKAGE.md`, and `xiaohongshu.json`. The JSON is the native draft input and fixes the ordered image paths and digests, title, plain-text body, and topics.

Run `verify` without `--visual-passed`, inspect every image and the contact sheet, then rerun with `--visual-passed` only after checking fixed bilingual font sizing, dynamic strip heights, bottom-anchored crop, readability, ordering, and no truncation. Finalize with:

```bash
./work finalize <variant>/render --qa-passed
```

The approved article plan is the only content gate. Do not add a second visual Draft approval. Final is local and does not authorize any platform action.

## Save To Xiaohongshu Creator Drafts

Only continue when the user explicitly authorizes saving this exact Work and Variant to the Xiaohongshu Creator draft box. Validate the Final manifest and `xiaohongshu.json`, including every image digest and its order. Use the user's existing logged-in Windows Chrome session through Computer Use; never read, export, or reuse browser cookies and never call an undocumented private API.

Open the official Creator platform, create an image note, upload the ordered images, fill `title` and `body`, and add the listed topics through the platform topic control. Never click `发布`, `定时发布`, or any equivalent submission control. Let the platform save the draft, then open `草稿箱` and verify the matching title and image count. Record only the payload digest, save time, title, image count, and verification result in `<variant>/.runtime/xiaohongshu-draft.json`; do not store cookies or page data. Stop without retrying if login, CAPTCHA, an ambiguous save state, or changed fields prevent verification.
