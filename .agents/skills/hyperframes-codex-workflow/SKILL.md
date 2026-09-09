---
name: hyperframes-codex-workflow
description: Route one local HyperFrames AI Work through DBS copy, a lightweight layout Plan, Draft acceptance, Final QA, and recoverable archive.
---

# HyperFrames AI Work Router

This Skill is intentionally thin. The repository root owns the workflow.

## Runtime Boundary

Windows creates and accepts production Works from the fixed workbench workspace, using one pinned installed version per session. Use its launchers rather than editing the installed Harness or resolving the mutable WSL checkout. Work-local content, Slots, layout, timing and scene orchestration are creation tasks. New component internals, shaders and reusable effect algorithms are WSL development tasks, even when delivered only to one Work.

Windows can create a static layout sample and describe effects before WSL delivery. A missing effect does not block Plan when layout can be judged without it. After Plan approval, hand off new internals as needed with the Work/Variant, affected Scene, frozen source, actual content, constraints and acceptance target. WSL develops in a private reproduction, never production Work state. A planned effect is not a reviewed implementation.

Candidate review runs only in an isolated Review WorkStore. It never grants production component installation, Finalize, archive completion or platform-draft permission. Component acceptance, Plan acceptance and Draft acceptance remain separate facts; one explicit user instruction may cover several. Apply an approved exact delivery in Windows only after checking its target snapshot, preserving unaffected Scenes and old accepted snapshots.

## Start

1. Run `./work current`; when no Work is current, run `./work list` and do not guess.
2. Confirm `WORK.md` declares `"workflow":"hyperframes_video"`; route `podcast_quote_image` to its own Skill.
3. Follow root `AGENTS.md` and `.studio/workflow.md`.
4. Load the current `WORK.md`, `variant.yaml`, `SCRIPT.md`, one Recipe, and only the selected Profile resolved through `.studio/capabilities.yaml`. Treat the marked Scene index in SCRIPT as non-spoken planning input; use `work script text` for narration consumers.
5. After the Script route is settled, create or load only the `RESEARCH.md` adopted entries and evidence relevant to the current Scene/Anchor gaps; load `ANIMATION_PLAN.md` only for visual planning, affected-scope revision, or recovery. Load `.studio/spec/hyperframes.md` only for implementation and QA.
6. Load `hyperframes-anti-ppt` only when forming or reviewing the Animation Plan, or when reviewing a rendered Draft.

## Route

- For downloaded video, route `SCRIPT.md` through either multi-round `dbs` editing or timestamp-preserving `verbatim`; Script approval appears only when spoken text changed.
- Once the Script is settled, run `./work --work <work-id> --variant <variant-id> name "<core-topic>"` before Research. The CLI preserves the per-workflow three-digit sequence allocated by `work new` and leaves the Work ID unchanged.
- Research only genuine Scene/Anchor information gaps. In the existing `RESEARCH.md`, keep source findings and media evidence positions under evidence, and directly usable wording with citations under adopted information. A Scene may need no new research. Research does not prescribe layout, crop, animation state, or final screen time.
- Before Plan approval, use `hyperframes-anti-ppt` to verify that the intended conclusion is expressed through the chosen text, media, operation, or motion, and that text which must be read has a real reading window. Merge concrete findings into `ANIMATION_PLAN.md`; do not require verbatim card-by-card repetition, a uniform transformation formula, or another approval artifact.
- When component candidates or a combination Preview exist, the video workflow owns discovery, versioning, and installation. Discover Component Releases from `.studio/components/**/COMPONENT.md`, and inspect only matching Cases from `.studio/components/*/cases/**/CASE.md` plus boundary Fixtures when needed. A Case records an in-contract real use; it never widens the Component contract. `hyperframes-anti-ppt` reviews narrative and motion fit only.
- Keep the Scene brief and matching rationale in `ANIMATION_PLAN.md`: cite Script Anchors for spoken excerpts, Research adopted entries for independently maintained information, and the source asset for native screenshot/video text. Presentation-only labels stay in the project. Record the chosen Component or effect, relevant Case, fit and limits, or `custom:<slug>`. Compare alternatives only for a real tradeoff; do not create a second Scene or copy database. Distinguish code reuse from design reference and technical bindings from proven production reuse.
- When creating the Animation Plan, use DBS to write the final title, cover text, one-line summary, and content overview to `PACKAGE.md`. Keep the overview concise and split it by the main subjects or topics; introduce each Skill, tool, feature, or case separately when there are several. Do not retain the candidate list there.
- Use exactly one of `talking_head` or `pure_hyperframes` and exactly one stable Profile.
- With Script and Research ready, keep a brief whole-film Scene/Anchor plan and build one representative actual passage as ordinary HTML/CSS at the target canvas size. Choose meaningful text density, not automatically the easy opening. Reuse approved fonts, colors, tokens and useful static components; no complete project, new schema or component installation is required.
- The sample uses actual text, hierarchy, colors and layout. Media placeholders describe purpose, subject, ratio and crop assumptions, never fake paths. Existing relevant images may be reused. A few static states with minimal JavaScript are enough; show the sample Scene and that motion/media are unimplemented. Do not initialize HF, GSAP, Three, all Scenes, audio sync or MP4 rendering for the default Plan. Add another small sample only if a materially different layout cannot be inferred.
- Describe principal motion through objects, relationships, start/end states and reading arrangements; give costly or novel effects a fallback when needed. Default to implementing uncertain effects first inside Draft. Use an early local experiment only for a risk that changes the overall decision, not as a new mandatory approval.
- Stop once layout, colors, fonts and actual text capacity can be judged and unresolved implementation is explicit. Register with `preview register --purpose plan --kind layout --sample-dir <directory-inside-Variant> --scene S01` (repeat `--scene` as needed), then `preview open plan-vNNN` and, after the user's confirmation, `preview accept plan-vNNN`. Freeze `SCRIPT.md`, `RESEARCH.md`, and `ANIMATION_PLAN.md` as source inputs plus the actual sample, styles, and used assets; do not expand this into a complete project snapshot. Record displayed design separately from agreed-but-unverified effects, media and other Scenes. Acceptance never writes `accepted_preview` or permits Final.
- A complete executable Visual Plan remains an explicitly selected advanced path via `preview register --purpose plan --kind executable`; omitted kinds on legacy records retain their original meaning. Do not choose it by default. Qualified component installation still uses `--purpose plan` before approval and never modifies frozen vendor.
- After approval, carry useful HTML/CSS, text and tokens into Draft, implement the riskiest actual shot first, then add the remaining Scenes, motion and media. The same model may change line breaks, grouping, order, presentation labels, and equivalently shorten adopted information in place; update that Research entry and its presentation without browsing or creating a copy handoff. Omit optional additions freely. New data/comparisons/causality need focused research; deleting core information or changing facts, viewpoint, causality, required numbers/units/ownership, or confirmed narrative is a local tradeoff for the user.
- Necessary structure changes are allowed without changing the approved visual result. Do not require missing production code to be backfilled into Plan. Use `preview diff <id>` for scoped changes. After an equivalent Research/project change, use `--compatible` only when narration, Anchors, and the accepted Plan's visual body are unchanged; only its `status`, `visual_plan`, `revision`, `script_revision`, and `research_revision` frontmatter fields may differ. Record the affected Scene and rationale. The runtime verifies frozen/current inputs, revisions, and project hashes and does not infer semantic equivalence. Compatibility carries the Accepted Plan into a new Draft; it never extends an Accepted Draft across source content or revision changes. Legacy records without frozen source inputs keep the original flow. Required media/effects must be complete before accepting Draft or Final.
- For formal audio, adjust reading holds, flexible motion and handoffs before assuming whole-scene time scaling. Preserve required text, complete audio and old Accepted Draft/Final snapshots.
- Keep time authorities separate: SCRIPT carries planning budgets, formal audio and `section_map.json` carry measured time, and the project timeline carries actual visual appearance and duration. Plan records only the needed basis and rhythm intent.
- Review the rendered Draft or representative keyframes with `hyperframes-anti-ppt` before registering it for user review.
- Register each Draft with `./work preview register`, then record the user's accepted Draft with `./work preview accept`.
- Finalize only from the accepted source snapshot and only after Final QA.

Do not load or invoke image generation, Prompt libraries, `design-taste-frontend`, subtitle generation, publishing, Examples, Migration files, all Profiles, or all Draft/QA history during normal production.
