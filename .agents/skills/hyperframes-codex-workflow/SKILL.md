---
name: hyperframes-codex-workflow
description: Route the current HyperFrames Work to its stage and load only the necessary contracts.
---

# HyperFrames Work Router

## Locate

Environment and authority: root `AGENTS.md`. Windows uses this root's `work.cmd`; development never reads production Current or configuration. Foreground creation locates `work current`, then `work list` if unset. Background jobs explicitly bind `--work <id>` and, for production, `--variant <id>`.

Read `WORK.md`, then the selected `variant.yaml`; resolve Script/Research through `shared_inputs`. Use the selected Variant's frozen mode (`card`, `explainer` or `showcase`) and appearance. Resume its actual stage in `.studio/workflow.md`.

Resolve the selected Variant's frozen `line.id` and `line.version` against `.studio/lines.yaml`. Read the line's `author_model`, `plan_template`, `brief`, `subjects`, `stages`, `thresholds`, `critic_checks`, `defaults`, `assets` and `exemptions`; use `stages` to load only the current stage's files. Product-line differences live in that catalogue, not duplicated here. An older Variant without `line` keeps its existing mode/spec contracts. `talking_head` remains a Template and podcast images keep their own workflow.

Read effective switches with `work settings show --json`: line defaults, then user, then Variant. Follow the actual `direction_approval`; full Draft acceptance and approval of dbs body changes remain mandatory. For critic, run `critic round`, then read the returned settings and prompt. When enabled, spawn an independent read-only agent with the configured image-capable model, restricted to the evidence package. It must inspect PNG frames and verify previous issues individually; use `critic record --file` to persist its result. If the host cannot use that model or read images, report unverified; never silently substitute a text-only critic. The automatic round limit stops automatic iteration, not a user's manual continuation.

For `podcast_quote_image`, retain its creation and selection contract: load `planner_skill` before article selection, `copy_skill` afterward and current machine artifacts; do not load video Plan, Recipe or theme rules.

## Stage Loading

| Stage | Load only as needed |
|---|---|
| Create, switch, accept, Finalize, archive | Root `AGENTS.md`; `.studio/workflow.md` governance and actual CLI help |
| Content preparation | Script, relevant Research and source/alignment evidence; `.studio/spec/creative.md` |
| Plan | Current Plan, selected Research, frozen line `stages.plan` (legacy: `.studio/spec/visual-design.md`), applicable `.studio/recipes/` structural difference and selected asset data |
| Draft | Current Plan and affected sources, frozen line `stages.draft` (legacy: `.studio/spec/visual-design.md` and `.studio/spec/hyperframes.md`) for implementation and QA |
| Selected assets / helpers | Selected interface card; `.studio/spec/runtime-interfaces.md`; `.studio/spec/hyperframes-assets.md` only for asset wiring |
| Final delivery | Accepted version and provenance; `.studio/workflow.md` Final delivery; `.studio/spec/hyperframes-final.md`; actual CLI help |
| Research registration | `.studio/spec/hyperframes-research.md` |
| Remotion integration | `.studio/spec/hyperframes-remotion.md` only when selected |
| Podcast images | Selected planner/copy Skill; `.studio/workflow.md` podcast branch and `.studio/spec/creative.md` podcast contracts |
