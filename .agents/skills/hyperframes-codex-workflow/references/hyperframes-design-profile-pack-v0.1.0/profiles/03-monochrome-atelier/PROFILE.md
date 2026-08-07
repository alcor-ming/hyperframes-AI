# Profile 3：Monochrome Atelier｜黑白工坊

`profile_id: monochrome_atelier`

## Visual thesis

> 通过删减、排版、留白与精确时机，让极少的信息获得最大重量；高级感来自编辑判断，不来自黑金装饰。

## Source adaptation

This Profile uses `pbakaus/impeccable` primarily as a design-governance method, not as a copied visual theme.

Four mandatory gates are adapted:

1. **Distill**：remove anything that does not earn its place.
2. **Quieter**：reduce saturation, layering, motion and decorative intensity without erasing identity.
3. **Typeset**：make typography carry hierarchy, voice and reading comfort.
4. **Layout**：use reading order, proximity, rhythm and the squint test before adding containers.

Impeccable's current project brand identity is not inherited. This Profile remains an independent monochrome editorial world.

## Emotional target

Controlled, authoritative, cinematic, deliberate and memorable. It should feel like a designed stage or fashion editorial, not a generic luxury template.

## Best for

- brand statements;
- product launches;
- high-level conclusions;
- fashion, culture and premium consumer topics;
- short conceptual explanations;
- chapter dividers and climactic moments.

It is less suitable for dense multi-variable technical explanation unless the content is aggressively distilled.

## Four-gate workflow

### Gate 1：Distill

Before designing a scene, state the one message it must communicate. Remove repeated copy, decorative lines, redundant labels and unnecessary containers.

### Gate 2：Quieter

Keep one bold anchor and make everything else recede. Reduce color, motion distance, layer count and effect intensity. Quiet does not mean uniformly small or gray.

### Gate 3：Typeset

Define explicit roles: display, support, metadata and data. Make the roles recognizable before the words are read.

### Gate 4：Layout

Apply the squint test. The primary, secondary and major grouping must remain visible. Use proximity and rhythm before boxes or rules.

A scene that fails any gate must be revised before animation.

## Color language

Use `tokens.json` as authority.

- Use tinted near-black, not pure `#000000`.
- Use warm off-white, not harsh pure white.
- Secondary text is a warm neutral.
- Champagne/kinpaku-like accent is optional and rare.
- Gold is a semantic punctuation mark, not a permanent border color.
- Accent coverage target: 0–1.5%; a scene may use no accent at all.

## Typography

### Stacks

```css
--font-cn-display: "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", serif;
--font-cn-body: "Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC", sans-serif;
--font-en-display: "Libre Bodoni", "Bodoni Moda", "Cormorant Garamond", Georgia, serif;
--font-en-body: "Source Sans 3", system-ui, sans-serif;
--font-mono: "JetBrains Mono", Consolas, monospace;
```

### Role rules

- Display serif is reserved for short, high-value lines.
- Chinese long-form explanation uses a stable sans body.
- Large type may be highly contrasted; small type must not be ultra-thin.
- Use at most two font families in a scene, plus optional mono data.
- Letter spacing may animate only on a short display line.
- Avoid automatic all-caps for every English phrase.
- Use one deliberate type scale, not many adjacent sizes.

## Composition

The frame is a stage.

- One dominant object or phrase.
- One supporting group at most.
- A clear axis, edge or baseline.
- Large quiet regions are intentional.
- The focal point may be off-center.
- Cards are exceptional; most hierarchy comes from scale, spacing and alignment.
- A rule line is used only when it establishes an axis or boundary.

### Density

- Lowest default density of the three Profiles.
- When content is dense, split it into sequential scenes rather than shrinking type or adding cards.
- A technical diagram may appear, but it must be reduced to its decisive relationship.

## Material

Allowed:

- tinted black field;
- off-white typography;
- hairline rules;
- high-quality monochrome photography;
- flat metallic accent;
- mask/crop interaction;
- very subtle grain.

Rules:

- No glass.
- No glow.
- No synthetic metallic gradient.
- No repeated gold frames.
- Gold appears as a point, short rule, number or one emphasized word.
- Depth comes from crop, overlap, scale and timing—not shadow stacks.

## Motion grammar

### 1. Isolate

Purpose: remove competing context and make one object unavoidable.

- other elements fade/cut away before the primary item moves;
- 12–30 frames;
- minimal travel.

### 2. Unveil

Purpose: reveal a word, image or decisive fragment.

- mask or crop reveal;
- 24–54 frames;
- one direction only;
- the final silhouette must be clean.

### 3. Cut

Purpose: make a decisive chapter or contrast change.

- hard cut, short dip or rule-based wipe;
- 0–12 frames;
- use sparingly; not every scene needs a soft transition.

### 4. Condense

Purpose: bring dispersed evidence into one final statement.

- position, scale or letter spacing closes with precision;
- 24–48 frames;
- no bounce or elastic overshoot.

### 5. Lock

Purpose: establish the final composition and hold it.

- the ending frame must feel intentional, not merely stopped;
- hold 1–3 seconds depending on copy and audio;
- ambient motion normally stops.

## Timing tokens

At 60fps:

- cut: 0–12 frames;
- isolate: 12–30 frames;
- unveil: 24–54 frames;
- condense: 24–48 frames;
- stagger: 5–12 frames, used rarely;
- hold: 60–180 frames where the speech allows it.

## Talking-head mapping

- Use sparse large keywords, short rules or one key number.
- Avoid background cards; let type sit in clean negative space.
- Do not make every spoken sentence a title card.
- Lower overlay frequency than the other Profiles.
- A champagne accent may mark one climactic word, not every section.

## Pure HyperFrames mapping

- Use the full frame as a typographic and photographic stage.
- Alternate decisive cuts with long stable compositions.
- Use image crop, type scale and silence to create rhythm.
- Keep technical evidence sequential and distilled.

## Hard bans

- black-and-gold card grids;
- gold borders around every element;
- metallic gradients and glow;
- pure black/pure white default pairing;
- glass, blur panels and SaaS chrome;
- nested cards;
- bounce, elastic or playful spring;
- many tiny labels;
- ultra-thin Chinese body text;
- continuous slow motion on every scene;
- excessive centered composition;
- adding decoration after the four gates already produced a complete frame.

## Scene QA

- What was removed during Distill?
- Is there one unmistakable anchor?
- Does the frame remain distinctive after becoming Quieter?
- Can type roles be recognized without reading?
- Does the squint test reveal the intended order?
- Is gold absent unless it carries a specific meaning?
