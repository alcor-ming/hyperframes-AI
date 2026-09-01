---
name: hyperframes-codex-workflow
description: Route one local HyperFrames AI Work through DBS copy design, an approved Animation Plan, Draft acceptance, Final QA, and recoverable archive.
---

# HyperFrames AI Work Router

This Skill is intentionally thin. The repository root owns the workflow.

## Start

1. Run `./work current`; when no Work is current, run `./work list` and do not guess.
2. Confirm `WORK.md` declares `"workflow":"hyperframes_video"`; route `podcast_quote_image` to its own Skill.
3. Follow root `AGENTS.md` and `.studio/workflow.md`.
4. Load the current `WORK.md`, `variant.yaml`, `SCRIPT.md`, one Recipe, and only the selected Profile resolved through `.studio/capabilities.yaml`.
5. After the Script route is settled, create or load the matching `RESEARCH.md`; load `ANIMATION_PLAN.md` only for visual planning or recovery. Load `.studio/spec/hyperframes.md` only for implementation and QA.
6. Load `hyperframes-anti-ppt` only when forming or reviewing the Animation Plan, or when reviewing a rendered Draft.

## Route

- For downloaded video, route `SCRIPT.md` through either multi-round `dbs` editing or timestamp-preserving `verbatim`; Script approval appears only when spoken text changed.
- Once the Script is settled, run `./work --work <work-id> --variant <variant-id> name "<core-topic>"` before Research. The CLI preserves the per-workflow three-digit sequence allocated by `work new` and leaves the Work ID unchanged.
- Research the settled Script online into `RESEARCH.md`, then require the Animation Plan to target that Research Revision.
- Before Plan approval, use `hyperframes-anti-ppt` to define or review the motion-native premise and merge the result into the existing `ANIMATION_PLAN.md`; do not create another approval artifact.
- When component candidates or a combination Preview exist, the video workflow owns discovery, versioning, and installation. Discover Component Releases from `.studio/components/**/COMPONENT.md`, and inspect only matching Cases from `.studio/components/*/cases/**/CASE.md` plus boundary Fixtures when needed. A Case records an in-contract real use; it never widens the Component contract. `hyperframes-anti-ppt` reviews narrative and motion fit only.
- Keep the Scene Semantic Brief and Component Match Record in the existing `ANIMATION_PLAN.md`: record the selected Component, matched Case, fit reason, anti-use check, relevant rejected candidates, and `custom:<slug>` fallback. Do not create `SCENE_SEMANTICS.md` or a second semantic source of truth.
- When creating the Animation Plan, use DBS to write the final title, cover text, one-line summary, and content overview to `PACKAGE.md`. Keep the overview concise and split it by the main subjects or topics; introduce each Skill, tool, feature, or case separately when there are several. Do not retain the candidate list there.
- Use exactly one of `talking_head` or `pure_hyperframes` and exactly one stable Profile.
- Require one approved `ANIMATION_PLAN.md` before formal HTML work.
- Review the rendered Draft or representative keyframes with `hyperframes-anti-ppt` before registering it for user review.
- Register each Draft with `./work preview register`, then record the user's accepted Draft with `./work preview accept`.
- Finalize only from the accepted source snapshot and only after Final QA.

Do not load or invoke image generation, Prompt libraries, `design-taste-frontend`, subtitle generation, publishing, Examples, Migration files, all Profiles, or all Draft/QA history during normal production.
