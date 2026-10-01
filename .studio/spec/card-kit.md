# Card Kit Module Contract

`card-kit@v1` is an editable AssetSource exported from the Harness-owned runtime.
It is not the approved design-source package, and does not replace or mutate
`card-family-source@v1` or `card-family-svg-slots-source@v3`.

## Assets And Installation

The source contains `asset.json`, `card-kit.js`, `card-kit.css`, and this interface
card as `USAGE.md`. No design preview UI, font, icon collection or third-party
media is bundled. Content SVGs and fonts belong to the Work's frozen closure.

Export to an explicit new directory, then use the existing `component pack`,
`component validate`, `component accept` and `component install` commands.
Export never accepts a candidate. Acceptance names the exact package SHA-256
and a review note; automated fixture acceptance is not production acceptance.
Re-export is idempotent only for identical bytes. Changed bytes under an
existing source identity are rejected, never overwritten.

```sh
work component card-kit-source <editable-source>
work component pack <editable-source>
work component accept card-kit@v1 --sha256 <reviewed-hash> --note <review-note>
work --work <id> --variant <id> component install card-kit@v1 --binding-file <binding.json>
work --work <id> --variant <id> cards build --browser <chromium>
work --work <id> --variant <id> cards studio --browser <chromium>
```

The approved Plan must include `card-kit@v1` for installation. `cards build`
preserves hand-authored Scene content and replaces only its marked mount block.
It measures actual frozen-font layout in an isolated browser before writing.
Never edit the generated block. A standalone registered AssetSource sample uses
`--project <project> --plan <plan>` instead of Work/Variant selectors.

`cards studio` opens a loopback companion editor alongside the unmodified official
Studio. Its card editor writes Plan first, regenerates and refreshes the preview;
it is not an interceptor for arbitrary native Studio source edits. Each save
requires the current Plan hash, invalidates prior approval/acceptance, and retains
unrelated Markdown and Scene code. CLI automation uses `cards edit --card <id>
--body-file <file> --plan-sha256 <hash>`. Saved content needs the normal direction
approval before a later independent build; saving never grants acceptance.

Install using the existing module binding schema 3 with `component_ref`, `scene`
and `usage`. Both JS and CSS are copied into
`vendor/components/card-kit/v1/` and covered by `COMPONENT_LOCK.json`.
Load the installed stylesheet and JS from that directory, not the editable
source or a remote CDN. The installed project remains usable without AssetStore.

## Runtime API

```javascript
const instance = await HarnessCardKit.mount({
  stage, text, card, ratio: "16:9", cues, start: 0, end,
  appearance, resolveSVG, cueTime, reducedMotion
});
instance.renderAt(seconds);
```

`stage` and `text` are connected, independent layer 2 and layer 4 DOM hosts;
neither may contain the other. `card` is the parsed Plan card object. `end` is
required and greater than `start`. `cues.find(query)` resolves speech cues;
optional `cueTime(query)` overrides this resolution. Resolved cue seconds and
`renderAt(seconds)` use the same time domain.

`resolveSVG(ref)` is required only when a card contains SVG slots. It resolves
to a frozen SVG string, not a remote URL. The module never downloads resources.
Optional `appearance` uses `HarnessAppearance.apply`; omitting it inherits the
hosts' frozen `--appearance-*` tokens. Optional `reducedMotion` overrides the
platform reduced-motion preference. Load `card-kit.css` before mounting.

The returned object exposes `text`, `decorations`,
`items: [{id, cue, element}]`, `renderAt(seconds)`, `retime(cueTime, activeEnd)`, `getState()`, `rhythm()` and
`dispose()`. Supply `text` and `decorations` to the Harness Rolls integration;
the kit registers its rhythm source in `__hfRhythmSources`. Call `dispose()`
when replacing or removing an instance. Mount failures and overflow must be
reported, not replaced with a hidden or truncated card.

## Content And Appearance

The current-version Plan is the sole content source. Cards select F01-F08,
an explicit area, speech cues, optional emphasis and exit. Content is projected
to layer 4; card surfaces and decorations are projected to layer 2.

| Preset | Text slots | Optional SVG slots |
| --- | --- | --- |
| F01 | title, lines, note | title, each line |
| F02 | title, lines, note | title, each line |
| F03 | title, lines, note | title, each line, figure |
| F04 | title, indexKey, lines, note | title, each line |
| F05 | title, paragraph lines, note | title, figure |
| F06 | title, key, lines, note | title, each key |
| F07 | title, input, inputLabel, outputLabel, lines, note | title, input, output |
| F08 | title, lines, note | title, each line, figure |

Only 16:9 and 9:16 are supported. Named areas and explicit pixel regions stay
inside the frame safe area. Compact placement may reflow grids and padding;
text is never shrunk or truncated to conceal overflow. Overflow is an error.
Appearance is mapped from the Variant's frozen Theme; there is no independent
light/dark theme or background option.

Cues, layer projection, rhythm registration and A/B freeze/resume use the
Harness runtime helpers. Every card instance has its own stable Plan ID.
Absolute-time rendering must agree for playback, seeking and reverse scrubbing.
Windows native Studio and user visual acceptance remain distinct from WSL checks.
