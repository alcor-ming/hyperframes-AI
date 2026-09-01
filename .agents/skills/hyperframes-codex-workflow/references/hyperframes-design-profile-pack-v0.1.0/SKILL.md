---
name: hyperframes-design-profiles
description: Select and enforce one of three HyperFrames video design profiles—Optical Fluidity, Kami Editorial, or Monochrome Atelier—across talking-head enhancement and pure HyperFrames presentation videos. Use when planning, implementing, reviewing, or normalizing HyperFrames visual identity, typography, color, materials, composition, and motion. Requires an Animation Plan confirmation gate before implementation.
license: Internal profile pack; adapted principles are attributed in upstream/THIRD_PARTY_NOTICES.md
---

# HyperFrames Design Profiles

This skill is the runtime source of truth for visual identity. Upstream design skills are references, not runtime dependencies.

## Required inputs

Determine or infer:

- `mode`: `talking_head` or `pure_hyperframes`
- `profile`: `optical_fluidity`, `kami_editorial`, or `monochrome_atelier`
- `ratio`: `16:9` or `9:16`; `optical_fluidity` also has an approved `4:3` mapping
- `subtemplate` when `profile` is `optical_fluidity` and `mode` is `pure_hyperframes`: `hero_flow` or `module_stage`
- authoritative duration/audio source
- whether original captions already exist
- protected subject/face regions when video footage exists

If the user explicitly names a profile, do not substitute another one. If no profile is named, recommend one from the content purpose, then state the selection in the Animation Plan.

## One-profile rule

Load exactly one profile file:

- `profiles/01-optical-fluidity/PROFILE.md`
- `profiles/02-kami-editorial/PROFILE.md`
- `profiles/03-monochrome-atelier/PROFILE.md`

Do not combine their palettes, fonts, materials, signature motion, or composition logic. Shared accessibility and rendering rules may still apply.

## Execution order

1. Read `shared/profile-contract.md`.
2. Read `shared/two-template-mapping.md`.
3. Read the selected Profile and its `tokens.json`.
4. Analyze the source media, section map, transcript, and available negative space.
5. Produce an Animation Plan, Implementation Changes, and Test Plan.
6. Apply `shared/review-gate.md`.
7. Stop and wait for explicit confirmation of the Animation Plan.
8. Only after confirmation, implement the HyperFrames composition.
9. Render, inspect representative frames, correct bounded defects, and validate.

## Planning output

The plan must name:

- selected profile and reason;
- selected subtemplate and reason when the Profile requires one;
- visual thesis in one sentence;
- authoritative palette and fonts/fallbacks;
- information hierarchy;
- protected regions;
- scene-by-scene semantic objects;
- hero-frame composition;
- motion verbs and timings;
- profile-specific anti-pattern risks;
- tests and acceptance boundary.

## Precedence

Resolve conflicts in this order:

1. explicit user instruction in the current request;
2. locked project/brand rules;
3. video mode constraints;
4. selected Profile;
5. shared baseline;
6. upstream suggestions.

## Runtime ban on upstream replacement

Do not invoke an upstream design skill to redesign the visual world during normal video execution. An upstream skill may be used only when the user asks to maintain, compare, or audit the Profile, and its findings must be translated back into the selected Profile contract before implementation.
