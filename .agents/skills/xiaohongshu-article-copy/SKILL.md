---
name: xiaohongshu-article-copy
description: Research the guest behind one approved podcast article plan, then write its Xiaohongshu copy, title, frames, renders, and local Final package.
---

# Xiaohongshu Article Copy

Continue one `podcast_quote_image` Work only after the user has approved exactly one `article-selection.json`. This Skill owns final copy and deterministic production. It does not reinterpret the transcript or offer new article directions.

## Start

1. In foreground mode, run `./work current`; in background mode, use the assigned Work and Variant IDs explicitly.
2. Confirm the Work uses `podcast_quote_image` and read only `article-selection.json`, the resolved transcript, acquisition metadata, `RESEARCH.md`, `PACKAGE.md`, and the machine artifacts needed by the current stage.
3. Reject a missing, stale, or unapproved selection. Do not fall back to an unapproved candidate.

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

Draft the opening and image sections first. Generate `PACKAGE.md` in this output order, but leave the title blank until the rest of the article is settled:

```markdown
# Package

## 大标题
<write this last>

## 开篇
<summarize the article's core viewpoint and connect it to the guest's verified background story>

## 图片文案

### g01｜<summary of this image's passage>
<third-person copy>

### g02｜<image subtitle>
<third-person copy>

## 播客信息
...

## 话题标签
...
```

The opening states the core conclusion immediately, then uses the guest's relevant background story to explain why the viewpoint carries weight. Each image subtitle summarizes that image's approved passage rather than adding a hook or a new claim. The image sections must cover every approved group once, in `g01...g08` order, with no extra group. Write in third person. Attribute viewpoints to the actual speaker; never impersonate the guest, invent first-person experience, or turn a faithful translation into a stronger claim.

Apply only the expression-efficiency and cognitive-gap checks from `dbs-content` to the opening, subtitles, and third-person copy; do not rerun format selection or its product-premise flow.

## Write The Title Last

After the full article is stable, use `dbs-xhs-title` to generate formula-traceable candidates. The final title must combine the article's core conclusion with the guest's most relevant verified identity or background signal, stay within 20 Chinese characters, and promise no more than the transcript and `RESEARCH.md` support.

Run `dbs-ai-check` on the completed title, opening, subtitles, and third-person copy, then fix only confirmed issues without touching the approved source quotes or translations. Do not use `dbs-hook` or `dbs-script-flow`.

Reuse `materials/acquisition.json` for the source URL and the verified research for guest metadata; verify the channel separately. Add episode or issue only when verified. If channel or source URL is missing, run `./work wait source_metadata` and stop.

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
