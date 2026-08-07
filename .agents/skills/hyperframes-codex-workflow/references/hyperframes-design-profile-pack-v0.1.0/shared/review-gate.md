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
| Build / Breathe / Resolve | Timing structure |
| Exit or carry-over | How continuity is preserved |
| Risk | Overflow, occlusion, performance or profile drift |

Stop after the plan. Do not create composition code or render final assets until the user explicitly confirms the Animation Plan.

## Gate 3：Implementation

- All values come from Profile tokens or approved deviations.
- Use transform and opacity for most motion.
- Expensive blur/filter changes are small, brief and isolated.
- No infinite animation unless the scene explicitly requires a bounded ambient loop.
- Scene transitions preserve spatial or editorial continuity defined by the Profile.
- Current captions and face protection zones remain clear.

## Gate 4：Rendered-frame QA

Inspect at minimum:

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
6. Does motion clarify state, relation or sequence?
7. Is there enough static reading time?
8. Are any effects present only to make the frame look busy?
9. Does the scene still work if ambient motion is removed?
10. Does the final frame resolve instead of fading into visual residue?

## Gate 5：Technical verification

- output duration matches the authoritative media source;
- resolution and ratio are correct;
- 60fps output is verified;
- audio is neither duplicated nor shifted;
- no text overflow, offscreen content or unintentional clipping;
- HyperFrames lint/validate/inspect pass where available;
- perform no more than one primary correction pass and one confirmation pass.
