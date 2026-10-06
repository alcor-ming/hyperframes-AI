# Mathematical Diagram Module

`math-kit@v1` is an editable module AssetSource, not an automatically accepted
asset. Export to an explicit new source directory, then use the existing
`component pack`, `component validate`, exact SHA-256 `component accept`, and
schema 3 `component install` commands. A fixture acceptance is not production
acceptance. The approved Plan must declare the module for each target Scene.

```sh
work component math-kit-source <editable-source>
work component pack <editable-source>
work component accept math-kit@v1 --sha256 <reviewed-hash> --note <review-note>
work --work <id> --variant <id> component install math-kit@v1 --binding-file <binding.json>
work --work <id> --variant <id> math build --browser <chromium>
```

For registered AssetSource samples, `math build --project <sample> --plan <plan>`
replaces Work selectors. Build requires approved Plan and frozen `math` line metadata, or an existing
`explainer` / `math-rap` frozen identity. It only replaces its
`hf-math` block; edit Plan, never generated HTML. Repeated builds are stable.
Changed cues, font, module, runtime or Scene timing require rebuilding before
preview registration. Build measures a staged copy before writing and rejects
concurrently modified inputs. Scene source outside the generated block is kept.

## Plan Data

Within each participating `## S01` section, keep one existing `math-plan` block
for semantic units, symbols, invariants, zero-basics actions and cues. Add one
`math` JSON block for font and fixed geometry only. Its item IDs must exactly
match that Scene's semantic unit IDs. Do not repeat cue times in the `math`
block or manual event table. Every cue resolves inside the Scene; cue rows are
strictly chronological. `keep` and omitted IDs retain prior state, `reveal`
shows a unit, and `remove` hides it. All units initially start hidden.

```math
{
  "font": {
    "path": "assets/math.ttf",
    "sha256": "<actual 64-character lowercase SHA-256>",
    "characters": "x"
  },
  "items": [{"id": "U01", "kind": "unknown", "box": [100, 100, 180, 180], "label": "x"}]
}
```

All items have `id`, `kind`, and `box: [x,y,width,height]` in native frame pixels
(1920x1080 or 1080x1920). Geometry must fit the selected frame. Fields below
are required; unknown fields are rejected. Text uses fixed 32px frozen font,
never automatic shrink-to-fit. Empty formula slots reserve their space.

| Kind | Additional Fields | Meaning |
| --- | --- | --- |
| `formula` | `slots: [string,...]` | Fixed equal-width slots; no recentering on reveal |
| `unknown` | `label` | Drawn square, not a square font glyph |
| `units` | `count`, `value`, `label` | Separate equal units; inside value and outside count/total label |
| `segment` | `count`, `value`, `label` | Divided length model with inside value and outside label |
| `area` | `value`, `label` | Square area with inside value and outside label |
| `number-line` | `min`, `max`, `step`, `labels` | Integral number of steps; explicit text for every tick |
| `strike` | `label`, `negate: boolean` | Struck relation; true draws a second diagonal for negation |
| `edge` | `from`, `to`, `length`, `label`, `duration` | Original horizontal edge retained; copy flies between absolute points |
| `equals` | `to`, `duration` | Equals sign starts at box position and migrates to absolute point |

`unknown` and `area` boxes are square. Counts are 1..32; number lines have
1..32 steps; formula rows have 1..16 slots. Motion duration is positive and at
most 10 seconds. Motion endpoints and lengths must remain inside the frame.
All displayed characters, including `=` for equals, belong to `font.characters`.
No implicit tick or mathematical label is synthesized from the source video.

## Frozen Fonts And Closure

Font path is project-local and hash-bound, with explicit characters covering
all labels and mathematical symbols. Use a properly licensed local TTF/OTF/
WOFF/WOFF2 font and retain its provenance through the normal asset workflow.
The builder rejects escaped paths, changed bytes, missing glyphs, failed font
loads and system fallback. Chromium inspects the actual font used for labels
and the declared character probe; `document.fonts.ready` alone is insufficient.
No fonts or remote dependencies are bundled in the module. Its JS, CSS,
interface card, frozen font and generated runtime stay in the snapshot closure.
Installed projects do not need the original AssetStore to play.

## Runtime Interface

```javascript
const instance = await HarnessMathKit.mount({
  stage, text, math, intent, cues, ratio: "16:9", start: 0, end,
  appearance, fontURL
});
instance.renderAt(seconds);
```

`stage` and `text` are independent layer 2 and layer 4 hosts. The runtime draws
geometry only into stage, labels only into text, and inherits frozen Theme
tokens. No independent playback loop is created. Absolute-time rendering,
reveal/removal and edge/equality motion agree for playback, seek and reverse
scrubbing. The instance exposes `items`, `text`, `decorations`, `renderAt`,
`retime`, `rhythm`, `getState`, and `dispose`. Rhythm sources are automatically
registered and removed on disposal. Use generated `HarnessMathProject` for
Scene clocks, `scene(id)` A-group access, `setRolls(scenes)` B-roll wiring,
global-time `renderAt`, and disposal. The math runtime and builder operate
independently of the retired card chain.

WSL isolated Chromium tests do not establish Windows-native compatibility or
zero-basics educational effectiveness. Deployment and the user's Studio viewing
test remain separately authorized and separately reported.
