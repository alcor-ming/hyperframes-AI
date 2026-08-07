---
name: hyperframes-codex-workflow
description: Plan and produce HyperFrames videos using one of three stable design profiles, either a talking-head enhancement template or a pure HyperFrames narrative template. Use when a video task requires a user-discussed Animation Plan, optional post-plan voiceover, optional image-gen assets, and quiet HyperFrames QA.
---

# HyperFrames Codex Workflow

Use this skill to coordinate visual planning and production. The detailed rules live in the files beside this document.

## Runtime loading

Use this file as the router. For a normal video task, load only:

1. the selected template document;
2. `docs/animation-plan-contract.md`;
3. `profile-registry.json`;
4. the selected Profile's `PROFILE.md` and `tokens.json`.

If no Profile is named, read only the profile pack's `prompt-blocks/profile-selector.md` before selecting one. Read `docs/discussion-protocol.md` only while revising a plan, image or voiceover docs only when those capabilities are used, and implementation or QA docs only after approval.

Do not load package overviews, prompts, examples, schemas, the nested Profile-pack `SKILL.md`, upstream references, or unselected Profile files during routine production. Do not invoke upstream design skills unless the user explicitly asks to maintain or audit a Profile.

## Select exactly one template

- `talking_head`: preserve an original talking-head video as the primary visual.
- `pure_hyperframes`: construct the complete visual narrative in HyperFrames.

Do not create a caption-only template. Captions are optional components.

## Select exactly one stable Profile

- `optical_fluidity`
- `kami_editorial`
- `monochrome_atelier`

Resolve the real Profile files through `profile-registry.json` and read exactly one Profile plus its tokens. Do not redesign, duplicate, or blend them.

## Planning gate

Create or update `ANIMATION_PLAN.md` before production. Treat it as a lightweight visual PRD that is discussed with the user and revised in place.

Before approval, only analyze source material, transcribe when useful, draft Scenes, and write optional Asset Briefs. Do not create final images, final voiceover, composition HTML, or final renders.

The visible plan contains only:

- Plan Header;
- Scene Table;
- Optional Asset Brief;
- up to three material open decisions.

Do not emit file-read lists, process proofs, repeated rules, implementation checklists, or full QA plans. Spend context on the actual visual plan, design decisions, implementation, and material blockers.

## After approval

1. Generate only approved optional image assets.
2. For `pure_hyperframes`, generate or receive final voiceover when required and retime Scenes from the real audio.
3. Build each Scene's static Hero State before GSAP animation.
4. Implement using the selected Profile's motion primitives.
5. Run quiet lint, validate, inspect, animation checks, and rendering.
6. Report only material deviations or unresolved blockers.

`section_map.json` is always optional.
