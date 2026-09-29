# synthetic-broll

Synthetic B-roll shot fixture for the isolated contract and browser pipeline
(`BROLL-REQ-006`..`009`). It is a development fixture: no production assets,
Work, credentials or video output are involved.

## Mount interface

`main.js` is an ES module exporting `mount(options)`. It reads `./asset.json`
from `import.meta.url` and hands off to the shared runtime:

```js
// Load the frozen runtime BEFORE the dynamic import of the package module.
//   <script src="runtime/appearance.js"></script>
//   <script src="runtime/rolls.js"></script>
//   <script src="runtime/broll.js"></script>
import {mount} from './vendor/components/synthetic-broll/v1/main.js';
const cues = {find: key => ({sceneStart:0, shotStart:1, shotEnd:4, sceneEnd:5})[key]};

const shot = await mount({
  stage,                       // required: B-interval layer 2 (media) host
  text,                        // required here: layer 4 (B text) host
  appearance,                  // frozen appearance object (lock + theme)
  slots: {title: 'Broll signal', value: 42},
  params: {},
  startCue: 'shotStart', endCue: 'shotEnd',
  cues,
});
```

`stage` becomes the B `media` and `text` becomes the B `text` group of the
`HarnessRolls` scene:

```js
const rolls = HarnessRolls.mount({cues, scenes: [{
  id: 'broll',
  startCue: 'sceneStart', endCue: 'sceneEnd',
  a: {text: aText, items: [{id: 'a1', element: aItem, cue: 'sceneStart'}]},
  b: [{startCue: 'shotStart', endCue: 'shotEnd', retreat: 'hide', media: stage, text}],
}]});
```

Then seek the host in full seconds and read the mapped timing:

```js
shot.renderAt(2.5);                          // forward, direct seek or back-seek
await rolls.renderAt(2.5);
const {key_moments, sfx_cues} = shot.moments();
shot.dispose();                              // removes nodes and rhythm source
rolls.dispose();
```

## Timing

`timing: stretch` with `duration {min: 2, max: 6, default: 3}`. `key_moments`
and `sfx_cues` are written at the default duration and mapped by `moments()`
(`stretch` scales, `hold-end` keeps absolute seconds and holds the end state).
A second temporary manifest in the browser test flips `timing` to `hold-end`
with `{min: 3, max: 6, default: 3}`.

The shot only exposes a discrete, time-pure performance: state changes happen at
`0`, `0.75`, `1.5` and `2.25` local seconds. It never starts its own clock, uses
no random values, no `requestAnimationFrame` and no `onUpdate` state.

## Slots

| slot  | type   | layer | max_chars |
| ----- | ------ | ----- | --------- |
| title | text   | text  | 12        |
| value | number | text  | 8         |

Values that are mistyped, over capacity, `NaN`/`Infinity`, or come from outside
the project closure (URL, traversal, unregistered media, non-exact icon ref)
are rejected by the runtime before `build` runs.

## Layout and appearance

The layout is bound to 90% of the host width and stays above the caption safe
zone (bottom `0.16`, `caption_safe_zone`). Labels use a fixed `16px` frozen font,
so a 12-character Chinese title fits the mobile width, and the geometry is
stable across keyframes. Colours and fonts are read from `--appearance-*`
variables only; the module declares no private colours or fonts.

`tests/broll-browser.mjs` builds complete isolated sample projects from this
source via pack/install/verify, then renders them with two Themes, both ratios
and both timing modes. Its output lists the sample project and screenshot paths.
