# Profile 1：Optical Fluidity｜光学流动

`profile_id: optical_fluidity`

## Visual thesis

> 用空间连续性、即时聚焦和轻量光学材质解释信息；玻璃只是层级工具，不是画面主题。

## Source adaptation

This Profile adapts principles from `emilkowalski/skills`, especially `apple-design` and `emil-design-eng`:

- immediate response becomes alignment to the spoken semantic onset;
- direct manipulation becomes clear 1:1 progress along the audio timeline;
- interruptibility becomes transition continuity without jumps;
- velocity handoff becomes momentum continuity between scene states;
- spatial consistency becomes symmetric entry/exit paths and anchored origins;
- translucent material becomes a scarce functional layer;
- motion must have purpose and start from the current visible state.

Gesture-only rules are not copied literally because the output is pre-rendered video.

## Emotional target

Precise, calm, contemporary, responsive and spatially coherent. The viewer should feel that the information is being clarified in real time, not that a futuristic HUD is decorating the footage.

## Best for

- AI and software explanations;
- product demonstrations;
- technical processes;
- system architecture;
- data relationships;
- modern knowledge videos.

Avoid for nostalgic, literary, archival or intentionally tactile subjects unless the user explicitly requests a contrast.

## Color language

Use `tokens.json` as authority.

- Deep blue-black canvas, never generic pure black.
- White carries claims and primary text.
- Cool cyan carries relationships, routes and inactive data.
- Active blue carries the current decision or selected object.
- Only one of cyan/blue may be the dominant accent in a frame.
- Accent coverage target: under 5% of the frame.

## Typography

### Roles

- **Claim / Display**：neutral sans, medium-to-semibold, tight leading, slight negative tracking at large sizes.
- **Explanation**：same family, regular/medium, high contrast over changing backgrounds.
- **Data**：tabular numerals or mono only when alignment matters.
- **Labels**：small sans with modest positive tracking; never turn labels into sci-fi microtext.

### Stacks

```css
--font-cn: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
--font-en: system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
--font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
```

The system stack is intentional in this Profile. Do not replace it with a decorative geometric font merely to look futuristic.

## Composition

### Spatial layers

1. **Environment layer**：source footage or low-contrast spatial field.
2. **Information layer**：claims, evidence, paths and data.
3. **Focus layer**：current conclusion or active object.

Depth is created by clarity, scale, overlap, shadow and local material weight—not by stacking many cards.

### Hierarchy

- One claim is visually closest to the viewer.
- Supporting evidence sits one depth level behind or beside it.
- Relationship lines appear only after both endpoints exist.
- Empty space is an active depth separator.
- At most one major glass surface per scene.

## Material

Allowed:

- localized translucent glass;
- static backdrop blur in negative space;
- bright top-edge highlight;
- subtle cool volumetric light;
- hairline paths and nodes;
- brief optical focus change.

Rules:

- Never place glass or blur over a face.
- Never stack a light translucent surface on another translucent surface.
- Larger surfaces may have stronger static blur, but animated blur delta stays small.
- Material should appear to arrive through scale + clarity, not opacity alone.
- Busy footage requires stronger text contrast, not lower text opacity.

## Motion grammar

### 1. Focus

Purpose: shift a concept from context into primary attention.

- 12–24 frames at 60fps;
- opacity + 4–12px translate + optional blur delta no more than 8px;
- strong ease-out;
- no bounce.

### 2. Align

Purpose: show that separate values or concepts belong to one system.

- 18–36 frames;
- elements settle onto a shared baseline or grid;
- use ease-in-out for movement already on screen.

### 3. Connect

Purpose: reveal relation, causality or route.

- endpoints first, path second;
- path draw 18–42 frames depending on semantic distance;
- path opacity remains subordinate to text.

### 4. Resolve

Purpose: collapse complexity into a conclusion.

- supporting elements recede while one answer locks into place;
- 24–48 frames;
- preserve the current visible position; no reset jumps.

### 5. Refract

Purpose: mark a rare state change or reveal material depth.

- maximum once per macro information group;
- small highlight/blur/refraction change, 12–24 frames;
- never full-screen and never continuous.

## Timing tokens

At 60fps:

- micro feedback: 8–14 frames;
- normal reveal: 16–28 frames;
- spatial transition: 24–42 frames;
- major resolve: 30–54 frames;
- stagger: 3–6 frames;
- exit usually 20–35% faster than entry.

## Talking-head mapping

- Put naked claim text in the largest negative-space region.
- Use one glass evidence panel only when raw text would lose contrast.
- Route paths around the subject; do not outline the person like a scanner.
- Let the source video run clean between semantic groups.
- Avoid permanent corner HUDs and decorative telemetry.

## Pure HyperFrames mapping

- Build a complete three-layer spatial field.
- Use image, diagram or data objects as depth anchors.
- The scene may use more pronounced Focus → Connect → Resolve choreography.
- Ambient light may drift slowly, but it must not become a visible loop competing with speech.

## Hard bans

- full-screen glass;
- nested glass cards;
- cyberpunk grids, scanlines and neon glow;
- purple/blue generic AI gradients;
- continuous floating of every object;
- large animated blur or backdrop-filter;
- bounce without momentum semantics;
- different entry and exit origins for the same object;
- sci-fi micro-labels that add no information;
- more than two simultaneous motion events.

## Scene QA

- Is glass solving hierarchy or merely adding style?
- Does every path connect two meaningful anchors?
- Does the focal object remain obvious after motion stops?
- Are transitions continuous from the previous visible state?
- Could the same explanation work with fewer layers?
