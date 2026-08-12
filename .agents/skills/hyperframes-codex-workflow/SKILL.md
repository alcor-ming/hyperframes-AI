---
name: hyperframes-codex-workflow
description: Route one local HyperFrames AI Work through DBS copy design, an approved Animation Plan, Draft acceptance, Final QA, and recoverable archive.
---

# HyperFrames AI Work Router

This Skill is intentionally thin. The repository root owns the workflow.

## Start

1. Run `./work current`; when no Work is current, run `./work list` and do not guess.
2. Follow root `AGENTS.md` and `.studio/workflow.md`.
3. Load the current `WORK.md`, `variant.yaml`, `SCRIPT.md`, one Recipe, and only the selected Profile resolved through `.studio/capabilities.yaml`.
4. After the Script route is settled, create or load the matching `RESEARCH.md`; load `ANIMATION_PLAN.md` only for visual planning or recovery. Load `.studio/spec/hyperframes.md` only for implementation and QA.

## Route

- For downloaded video, route `SCRIPT.md` through either multi-round `dbs` editing or timestamp-preserving `verbatim`; Script approval appears only when spoken text changed.
- Research the settled Script online into `RESEARCH.md`, then require the Animation Plan to target that Research Revision.
- Use exactly one of `talking_head` or `pure_hyperframes` and exactly one stable Profile.
- Require one approved `ANIMATION_PLAN.md` before formal HTML work.
- Register each Draft with `./work preview register`, then record the user's accepted Draft with `./work preview accept`.
- Finalize only from the accepted source snapshot and only after Final QA.

Do not load or invoke image generation, Prompt libraries, `design-taste-frontend`, subtitle generation, publishing, Examples, Migration files, all Profiles, or all Draft/QA history during normal production.
