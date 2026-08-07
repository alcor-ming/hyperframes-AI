# Profile 2：Kami Editorial｜纸上编辑

`profile_id: kami_editorial`

## Visual thesis

> 让信息像一页经过编辑的文章逐步成形：暖纸为底，墨蓝为唯一主强调，排版承担层级，动画只帮助阅读。

## Source adaptation

This Profile adapts `tw93/Kami` rather than directly running it.

Retained principles:

- warm parchment canvas `#F5F4ED`;
- ink blue `#1B365D` as the sole chromatic accent;
- all neutrals carry a warm yellow-brown undertone;
- typography and spacing create hierarchy;
- no cool gray, hard shadow, flashy palette or dashboard composition;
- a 4-unit spatial scale;
- accent coverage stays under 5%;
- composed pages, not card grids.

Changed for video:

- page density becomes scene density;
- printed hierarchy becomes timed editorial hierarchy;
- static figures become progressive diagrams;
- document templates and build scripts are not used;
- commercial-restricted TsangerJinKai02 is not included or required.

## Emotional target

Thoughtful, credible, composed, warm and literate. It should feel like a modern editorial page coming alive, not a vintage scrapbook.

## Best for

-观点与评论；
-读书、哲学、人文和历史；
-研究摘要；
-叙事型知识内容；
-报告和案例解释；
-需要降低“科技 UI 感”的 AI 主题。

## Color language

Use `tokens.json` as authority.

- Parchment is the emotional foundation.
- Ink blue is the only normal chromatic accent.
- Warm charcoal replaces pure black.
- Warm sand and ivory create quiet elevation.
- No cool blue-gray surfaces.
- Ink blue covers no more than 5% of the frame.

A warning color may appear only for an actual warning/error meaning, never decoration.

## Typography

### Commercial-safe default stacks

```css
--font-cn-display: "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", serif;
--font-cn-body: "Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC", sans-serif;
--font-en-display: Charter, "Source Serif 4", Georgia, serif;
--font-en-body: Charter, "Source Serif 4", Georgia, serif;
--font-label: "Source Sans 3", "Noto Sans CJK SC", sans-serif;
--font-mono: "JetBrains Mono", Consolas, monospace;
```

### Role rules

- Chinese claim/title: serif medium, never synthetic heavy black.
- Chinese explanation: readable sans body unless a short quotation intentionally uses serif.
- English title/body: restrained serif is allowed throughout.
- Labels, chapter numbers and metadata: sans or mono, short and compact.
- Use only two visible weight levels for serif: regular and medium.
- Large text gets tighter leading; reading text gets 1.5–1.6 line height.
- Do not use italic in normal video text. A quoted English phrase may use it only when explicitly justified.

### Font license rule

Do not bundle TsangerJinKai02. Kami documents it as personal-use-only unless separately licensed. This Profile defaults to Source Han/Noto/PingFang-style fallbacks.

## Composition

### Editorial structure

A scene behaves like a composed spread with a clear reading start:

1. chapter marker or eyebrow;
2. primary assertion;
3. explanatory line, quotation or evidence;
4. rule, annotation or figure;
5. resolved editorial page.

Not every scene needs all five.

### Layout principles

- Use proximity before containers.
- The gap below a heading is smaller than the gap above the next section.
- Use one major alignment axis.
- Asymmetric columns are allowed when reading order stays obvious.
- Paragraphs and diagrams sit on the same editorial grid.
- A repeated item does not earn a badge, connector or card merely because it repeats.
- Use lifted ivory surfaces sparingly and without closed hard borders.

## Material

Allowed:

- warm parchment field;
- ivory paper block;
- ink-blue rule or annotation;
- subtle warm grain at very low opacity;
- whisper/ring shadow;
- flat editorial diagrams;
- warm photographic treatment.

Rules:

- Paper surfaces are mostly solid, not glass.
- Texture opacity stays below 0.04.
- Shadows suggest paper separation but never become floating SaaS cards.
- No simulated torn edges, tape, pins, coffee stains or antique filters.
- Diagrams use simple single-line geometry and flat shapes.

## Motion grammar

### 1. Compose

Purpose: establish a page-like reading order.

- 24–48 frames;
- title, body and evidence settle onto a shared grid;
- use soft ease-out with minimal travel.

### 2. Reveal

Purpose: disclose a complete phrase, quotation or section.

- 18–36 frames;
- mask reveal, line reveal or short upward movement;
- ordinary prose appears by phrase/group, not character-by-character typewriter.

### 3. Annotate

Purpose: add an editorial note, underline, margin marker or evidence label.

- primary statement first;
- annotation enters 4–10 frames later;
- line draws before or with the note, never after an unexplained delay.

### 4. Rule

Purpose: separate chapters or establish a visual axis.

- thin line growth, 12–30 frames;
- ink blue or warm border token only;
- no glowing trails.

### 5. Turn

Purpose: move to the next section or argument.

- page flow shifts vertically or laterally without literal page-flip simulation;
- 30–60 frames;
- preserve one anchor—chapter number, baseline, image edge or rule—to maintain continuity.

### 6. Settle

Purpose: end movement and create a reading hold.

- allow 0.8–2.5 seconds of stable reading depending on copy length;
- remove decorative movement during the hold.

## Timing tokens

At 60fps:

- annotation: 12–24 frames;
- phrase reveal: 18–36 frames;
- composition build: 24–48 frames;
- chapter turn: 30–60 frames;
- stagger: 4–10 frames;
- stable reading hold is longer than in Profile 1.

## Talking-head mapping

- Do not place a full parchment layer over the footage.
- Use solid or near-solid paper strips/cards only in clean negative space.
- Prefer naked ink/ivory typography over a subtle local warm scrim when possible.
- Use short quotations, chapter marks and margin-note logic.
- One paper surface at a time; no dashboard card grid around the speaker.

## Pure HyperFrames mapping

- Parchment may become the full canvas.
- Build scenes as animated editorial pages or spreads.
- Use diagrams, quotations, chapter markers and evidence figures.
- Scene transitions should feel like argument progression, not app navigation.

## Hard bans

- Claude-orange as a permanent identity color;
- cool gray cards;
- pure-white page background as default;
- glass blur and neon;
- gradients, 3D and hard shadows;
- vintage scrapbook props;
- rounded-card dashboard composition;
- all text in decorative Chinese serif;
- synthetic 700/900 weight on serif;
- typewriter for ordinary prose;
- page-flip animation;
- more than one chromatic accent in normal scenes.

## Scene QA

- Does the scene read in one clear order without animation?
- Is ink blue actually scarce?
- Are neutrals warm rather than generic gray?
- Does typography, not container count, create hierarchy?
- Is there enough silent reading time after the page settles?
