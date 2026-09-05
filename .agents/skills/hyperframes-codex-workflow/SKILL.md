---
name: hyperframes-codex-workflow
description: Route one local HyperFrames AI Work through DBS copy, a same-source playable Visual Plan, Draft acceptance, Final QA, and recoverable archive.
---

# HyperFrames AI Work Router

This Skill is intentionally thin. The repository root owns the workflow.

## Runtime Boundary

Windows creates and accepts production Works from the fixed workbench workspace, using one pinned installed version per session. Use its launchers rather than editing the installed Harness or resolving the mutable WSL checkout. Work-local content, Slots, layout, timing and scene orchestration are creation tasks. New component internals, shaders and reusable effect algorithms are WSL development tasks, even when delivered only to one Work.

Keep a missing capability in the current discussion and hand off a frozen request with the Work/Variant, affected Scene, source snapshot, actual content, constraints and acceptance target. WSL reads that revision and develops in a private reproduction; it does not write production Work state. Continue unaffected Scenes without pretending the missing effect has been reviewed.

Candidate review runs only in an isolated Review WorkStore. It never grants production component installation, Finalize, archive completion or platform-draft permission. Component acceptance, Plan acceptance and Draft acceptance remain separate facts; one explicit user instruction may cover several. Apply an approved exact delivery in Windows only after checking its target snapshot, preserving unaffected Scenes and old accepted snapshots.

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
- Before Plan approval, use `hyperframes-anti-ppt` to protect required information, reading windows, and meaningful motion. Merge concrete findings into `ANIMATION_PLAN.md`; do not impose a uniform transformation formula or another approval artifact.
- When component candidates or a combination Preview exist, the video workflow owns discovery, versioning, and installation. Discover Component Releases from `.studio/components/**/COMPONENT.md`, and inspect only matching Cases from `.studio/components/*/cases/**/CASE.md` plus boundary Fixtures when needed. A Case records an in-contract real use; it never widens the Component contract. `hyperframes-anti-ppt` reviews narrative and motion fit only.
- Keep the Scene brief and matching rationale in `ANIMATION_PLAN.md`: cite actual text in its single source/Binding, the chosen Component or effect, relevant Case, fit and limits, or `custom:<slug>`. Compare alternatives only for a real tradeoff; do not create a second Scene database. Distinguish code reuse from design reference and technical bindings from proven production reuse.
- When creating the Animation Plan, use DBS to write the final title, cover text, one-line summary, and content overview to `PACKAGE.md`. Keep the overview concise and split it by the main subjects or topics; introduce each Skill, tool, feature, or case separately when there are several. Do not retain the candidate list there.
- Use exactly one of `talking_head` or `pure_hyperframes` and exactly one stable Profile.
- With Script and Research ready, assemble Work-local HTML and candidate bindings before Plan approval, using `component install ... --purpose plan` for qualified Releases. Never edit frozen vendor; request WSL development when new internals are needed, with Work-local custom as an allowed delivery scope.
- Build every Scene with actual required text, principal motion, and handoffs at the final canvas dimensions. Preserve precise content; GSAP guides reading and relationships, Three.js serves useful spatial mechanisms. Mark missing critical assets rather than presenting placeholders as approved results.
- Register the same-source rehearsal with `preview register --purpose plan` (MP4 optional), inspect it with `preview open plan-vNNN`, and record the user's one Plan confirmation with `preview accept plan-vNNN`. This binds Plan approval to its snapshot, never `accepted_preview`, and does not permit Final.
- Refine that Work project into the formal Draft after Plan approval; do not rebuild approved scenes. Use `preview diff <id>` to compare current source with the snapshot. Feedback is scoped to version, Scene and optional time/object; change only affected content and necessary handoffs, confirming only material design changes.
- For formal audio, adjust reading holds, flexible motion and handoffs before assuming whole-scene time scaling. Preserve required text, complete audio and old Accepted Draft/Final snapshots.
- Review the rendered Draft or representative keyframes with `hyperframes-anti-ppt` before registering it for user review.
- Register each Draft with `./work preview register`, then record the user's accepted Draft with `./work preview accept`.
- Finalize only from the accepted source snapshot and only after Final QA.

Do not load or invoke image generation, Prompt libraries, `design-taste-frontend`, subtitle generation, publishing, Examples, Migration files, all Profiles, or all Draft/QA history during normal production.
