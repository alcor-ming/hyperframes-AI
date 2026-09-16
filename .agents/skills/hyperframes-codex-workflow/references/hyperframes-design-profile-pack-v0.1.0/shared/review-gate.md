# Review Gate

## Gate 1：Profile lock

Before planning, verify:

- exactly one Profile is selected;
- no token from another Profile appears;
- all proposed fonts have fallbacks;
- no restricted font file is bundled;
- mode and ratio are explicit.

## Gate 2：Animation Plan

For every scene, provide:

| Field | Required content |
|---|---|
| Scene ID | Stable identifier |
| Time range | Start/end against authoritative audio |
| Spoken idea | The semantic source, not full transcript repetition |
| Primary claim | One message the viewer must retain |
| Supporting evidence | Optional data/example/relationship |
| Hero frame | Static final composition and protected zones |
| Profile motion verb | One or more verbs defined by the selected Profile |
| Reading and emphasis | Actual screen text, stable reading, keyword emphasis and required visual changes |
| Exit or carry-over | How continuity is preserved |
| Risk | Overflow, occlusion, performance or profile drift |

Create one real dynamic Scene reference after the whole-film Plan. Obtain one direction approval for both, including generated assets with specified purpose, quantity, style and Asset Brief. Then expand the full placeholder Draft without another mandatory acceptance gate; do not add a separate Profile approval.

## Gate 3：Implementation

- All values come from Profile tokens or approved deviations.
- Use transform and opacity for most motion.
- Expensive blur/filter changes are small, brief and isolated.
- No infinite animation unless the scene explicitly requires a bounded ambient loop.
- Scene transitions preserve spatial or editorial continuity defined by the Profile.
- Current captions and face protection zones remain clear.

## Gate 4：Studio Draft QA

Inspect affected Scenes and necessary handoffs in actual playback, with representative frames as supporting evidence:

- first stable frame;
- each scene hero frame;
- each transition midpoint;
- the frame with the longest text;
- the most crowded frame;
- final frame.

Answer:

1. Can the primary message be identified with a squint test?
2. Does only one Profile appear?
3. Is accent coverage within the Profile limit?
4. Are all text roles legible at output size?
5. Are face, subject and existing captions unobstructed?
6. Does the selected animation-led or text-led treatment communicate clearly with sound?
7. Is there enough static reading time?
8. Are decorative icons/images restrained and compatible with reading? Decoration itself is allowed.
9. Is the whole frame never completely static for more than 2 seconds while text can remain stable? Judge perceptible changes during playback, not tween existence; no reliable automatic tolerance is claimed.
10. Does the final frame resolve instead of fading into visual residue?

## Gate 5：Technical verification

- output duration matches the authoritative media source;
- resolution and ratio are correct;
- 60fps output is verified;
- audio is neither duplicated nor shifted;
- no text overflow, offscreen content or unintentional clipping;
- HyperFrames lint/validate/inspect pass where available;
- register the media-complete executable Studio Draft without a file, open its exact draft ID and accept the isolated reviewed version; no complete Draft MP4 prerequisite;
- verify Studio sound, continuous playback, seek and backward dragging; local limitations may use an audible short export, not silently require a full Draft render;
- render Final with `preview render <draft-id> --output <final.mp4> --final`, then check streams, specs, duration, full decode, representative frames and necessary audio;
- fix actual failures and re-render as needed, with no arbitrary correction-pass limit;
- unchanged accepted content needs source/evidence applicability only; local edits need affected scope, shared changes expand by dependencies; Finalize/archive checks sources, render records, file consistency and lifecycle without another aesthetic review/render.
