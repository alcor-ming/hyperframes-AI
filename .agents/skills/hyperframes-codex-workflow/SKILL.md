---
name: hyperframes-codex-workflow
description: Route the current HyperFrames Work to its stage and load only the necessary contracts.
---

# HyperFrames Work Router

## Locate

Environment and authority: root `AGENTS.md`. Windows uses this root's `work.cmd`; development never reads production Current or configuration. Foreground creation locates `work current`, then `work list` if unset. Background jobs explicitly bind `--work <id>` and, for production, `--variant <id>`.

Work owns one content goal; peer Variants own their independent production and delivery. A Work may have no Variant while content is prepared. Read `WORK.md`, then the explicitly selected, valid current or sole Variant's `variant.yaml`; never choose `main` from multiple candidates. Resolve Script/Research through `shared_inputs`. Use the selected Variant's frozen mode (`explainer`, `showcase`, `math` or `english`) and appearance. Resume its actual stage in `.studio/workflow.md`. Card production is removed; history may be viewed or explicitly adopted into a supported Variant.

Resolve the selected Variant's frozen `line.id` and `line.version` against `.studio/lines.yaml`. Read the line's `author_model`, `plan_template`, `brief`, `subjects`, `stages`, `thresholds`, `critic_checks`, `defaults`, `assets` and `exemptions`; use `stages` to load only the current stage's files. Product-line differences live in that catalogue, not duplicated here. An older Variant without `line` keeps its existing mode/spec contracts. `talking_head` remains a Template. Only video production is available; report retired or unknown Work types without treating them as video or running retired tools.

Read effective switches with `work settings show --json`: line defaults, then user, then Variant. Follow the actual `direction_approval`; full Draft acceptance and approval of dbs body changes remain mandatory. For critic, run `critic round`, then read the returned settings and prompt. When enabled, spawn an independent read-only agent with the configured image-capable model, restricted to the evidence package. It must inspect PNG frames and verify previous issues individually; use `critic record --file` to persist its result. If the host cannot use that model or read images, report unverified; never silently substitute a text-only critic. The automatic round limit stops automatic iteration, not a user's manual continuation.

After a successful official Finalize, the target Variant is archived. Resume revisions on that same Variant with `work reopen <Work-ID> --variant-id <Variant-ID>`; preserve sibling lifecycle and frozen deliveries. Work aggregation, park/resume, history and storage rules live in `.studio/workflow.md`, not Current.

For asset selection, use `work component list --include-references --query <purpose>` to search packages, scene sources and recipes together. Explicit `--kind scene-source` / `--kind recipe` needs no extra flag; plain list still hides references. Pass the returned `detail.argv` to the same root work entry for exact details; use `full_result` for untruncated JSON. Follow the current status and next_step, resolve ambiguity with the listed path, and never treat a reference or candidate as installation authority. Interface and list --audit write no cache, index or report.

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
| Content retrospective | Explicit Work/Variant/publication; `.studio/workflow.md` 内容复盘; `CONTENT_RETRO.template.md`. Use `content link/import/open/check/summary`; Opus first, Codex fallback. Write only `retro/content/` (including import originals) and `content-summary/`. No Work source, Plan, Current or acceptance edits; no network or video export. |
| Visual retrospective | User-designated Work/Variant/Draft; `.studio/workflow.md` 画面复盘与样片记忆; `VISUAL_RETRO.template.md`. Opus first, Codex fallback. Write only retro, sample-library, known-defects and retro-summary; no source, Plan, Current or acceptance changes. User confirms memories in conversation. |
