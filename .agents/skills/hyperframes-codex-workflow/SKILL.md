---
name: hyperframes-codex-workflow
description: Route the current HyperFrames Work to the current stage and its necessary contracts; do not duplicate the production workflow.
---

# HyperFrames Work Router

Environment and authority: root `AGENTS.md`. Stage order and acceptance: `.studio/workflow.md`.

## Locate

In Windows use the production root's `work.cmd`; in development do not read production Current or configuration. Foreground creation uses `work current`, then `work list` if unset; never guess. Background jobs receive explicit Work and Variant IDs and use `work --work <id> --variant <id> status` without touching Current.

Read `WORK.md` and `variant.yaml`. For `podcast_quote_image`, load only `planner_skill` before article selection or `copy_skill` afterward and the current machine artifacts. Do not load video Plan, Recipe or theme rules for that branch.

For video, resolve Script/Research through `shared_inputs` when present; new Works use `shared/`, while old Variant-local sources remain compatible. Mode defaults to `text-led`, without a default Profile. Use the Variant's frozen account/theme settings rather than rereading changed service defaults.

Before creating a video object, first distinguish discussion/research from making something, then locate an explicitly continued Work/Variant, a needed independent Variant of the same content goal, or a temporary experiment. Continue an existing matching Variant; create a new production Work only for a new content goal, and keep an ordinary fix in the current Variant. A request to test one Scene inside an already specified production Work stays there; an independent comparison that must leave the original untouched uses an isolated experiment. Do not infer purpose from keywords, source URL, media, missing Final, or Current. Search only the current object and relevant named/title/account candidates. If purpose materially changes the organization and is still ambiguous, ask one short question before creating; otherwise state whether you are continuing, adding a Variant, experimenting, or creating production work without adding an approval gate.

New video Works explicitly pass `--purpose standard|ip|test`: `standard` and `ip` are production, `test` is an experiment. Production creation needs a valid Series and registered `--account`; experiments do not bind an account and may snapshot its settings as a reference. An account is a Variant owner, not a unique Variant ID; select the exact Variant when several belong to it. Keep `podcast_quote_image` creation and routing unchanged.

Keep experiments until specifically asked to delete them. Before deletion, check active Studio/request and real production path dependencies; do not cascade into production or shared assets. Copy or freeze any adopted result inside the production Work first, and treat `source_work` as lineage rather than a live dependency or production acceptance.

## Stage Loading

For `hyperframes_video`, resume the actual stage in `.studio/workflow.md`; reuse sufficient existing inputs.

| Stage | Load only as needed |
|---|---|
| Content preparation | `SCRIPT.md`, source/alignment evidence, relevant `RESEARCH.md` entries; `.studio/spec/creative.md` for source ownership or revisions |
| Whole-film design | `ANIMATION_PLAN.md`, selected Research, applicable `.studio/recipes/` structural difference, selected visual theme data, `.studio/spec/visual-design.md` |
| Studio production and acceptance | Current Plan and affected source entries; `.studio/spec/hyperframes.md`; `.studio/spec/visual-design.md` for production defaults and actual Draft review |
| Final delivery | Accepted version and its provenance; `.studio/spec/hyperframes.md` Final QA; actual CLI help for the installed Finalize entry |

User-facing inputs are independent narrative mode, visual theme, background and ratio, with optional motion slots. Theme never chooses or restricts narrative mode, background, layout or cue timing. Use frozen appearance_lock and its local closure when present; otherwise preserve legacy snapshots. Do not require Profile, Template or Subtemplate selection as additional entry steps. Legacy Profile data is optional compatibility material, not an orchestration Skill. IP Beta follows its actual artistic brief rather than forcing the two standard modes.

Load asset contracts only for selected assets, deployment/request guidance only for an actual tool defect, and packaging Skills only when packaging is requested. `PACKAGE.md` is not a video prerequisite. Do not preload all profiles, examples, migrations, Draft history or unrelated Skills. `hyperframes-anti-ppt` is a compatibility entry to the single visual-design reference, not another workflow.

Scene dispatch includes the visual-design section `图文互补与辅助图形` and `work component list --query <purpose>` (Windows: `work.cmd`). Pass selected exact references, acquisition instructions and local usage/examples, not a full inventory. Ordinary auxiliary graphics remain the maker's responsibility without per-icon Plan fields or approval. If no usable object exists, route content creation to Windows Work-local or editable AssetSource; never claim bundled WSL presets or accepted assets exist. Discovery, research and cache refresh do not update frozen Work dependencies; explicit adoption follows `.studio/spec/hyperframes.md`.
