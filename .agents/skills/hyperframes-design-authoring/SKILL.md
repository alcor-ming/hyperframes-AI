---
name: hyperframes-design-authoring
description: Create or edit HyperFrames user design cards and material cards, including card assets, references, localization and deterministic example previews.
---

# Design card and asset authoring

Use the current root Work CLI. Read `.studio/spec/hyperframes-assets.md` for asset wiring and the selected card's guidance; obtain the configured user root from the design catalog. Built-in cards (installed under `.studio/designs/`) are read-only. When the root rules say cards are maintained elsewhere and not authored in this root, do not author here; record the request for the card owner. Design cards describe style and stage recipes; material cards supply assets and cannot be selected for a Variant.

Start with the user's subject, visual intent and default switches. Reuse supplied answers. Create a skeleton with `design new <id>` or copy an existing card with `design new <id> --from <card>`; use `--type material` for an asset-only card. Write guidance, example and assets in that user card. Do not turn style choices into model restrictions.

Assets live in `assets/<asset-id>/` with `asset.json`. Their identity is `<card>/<asset>`. Declare cross-card assets in `design.json.references` for live read-only reuse. Before changing a borrowed asset, use `design localize <card> <reference>`; preserve license/attribution and `borrowed.json`. Use `design compare <card> [<asset>]` to inspect source changes; do not merge automatically.

Declare host runtime versions and plugins in `runtime`. Do not include GSAP files in a card. Keep animation seek deterministic and avoid an independent clock. Run `design validate <id>`, then `design preview <id>` for cold, repeated and backward seek checks and screenshots. Report missing runtime/browser evidence as unverified; iterate on the actual preview and user feedback. Material cards need asset validation, not a fabricated design example.

Use `design list` to inspect origin/type and owned, referenced or localized assets; an invalid or conflicting card appears with its `error` and hides only itself. Card edits are immediately available while authoring; Draft submission saves Variant-owned snapshots. For an existing Draft use explicit `variant design-update` only on the chosen Variant. It preserves authored project assets and reports assets requiring explicit reinstallation; it does not accept a Draft or update sibling Variants. Existing vendor/lock and accepted snapshots remain independently usable.

## Version-controlled card root

`design_root` may itself be a Git working tree; tool releases never touch it. Keep deconstruction notes of reference videos as text under `<card>/study/`, or `studies/<slug>/` at the root for notes not yet tied to a card: mechanism breakdown, palette study, timing notes and what was deliberately not taken. Never commit the reference video, frames or full transcripts; record URL and timestamps instead. `study/` and `studies/` are ignored by the catalog, `validate` and Draft snapshots.

Loop: deconstruct, write study notes, create or change the card, run `design validate` / `design preview`, bump `design.json.version` with a `CHANGELOG.md` line, then commit. `design root` shows branch and uncommitted counts; `design compare <card> --since <rev>` lists changes since a revision and whether the version was bumped. Pull with fast-forward only; a dirty or diverged tree is reported, never auto-merged, and the CLI never runs git write commands.

## Extract a third-party design

Pin an HTTPS code repository with `design source-add <url> --commit <full-sha>` (requires local Git). The read-only `.sources` cache stays outside cards and delivery. Review each copied file's license and attribution; the generated `unreviewed` entries are not reuse permission. Exclude proprietary characters and restricted data. Prompt collections are reference-only: record URL, author and design mechanism in Brief without copying prompts.

Extract style into stages/Plan/GUIDE, colors into Theme, easing/transitions into Motion and drawing into a card-local module. Preserve notices and record `source.kind: external`, URL, commit and per-file hash/license/attribution in borrowed.json. Replace eval, synchronous XHR and runtime network loading with static closure files. Document conflicts resolved in favor of this project's contracts. Compare a separately cached new commit explicitly; do not auto-sync.

Canvas/WebGL modules expose complete `texts()` inventories (empty for no text). Independent embedded text requires text_type matching that asset's text_ownership.kinds. Keep kind attached/independent separate. Declare card-local fonts/licenses in fonts; map appearance.fontFamily, Theme palette, cues and caption safe zones into the engine. Check glyph coverage, cold/repeat/backward seek and every supported ratio. Hook 3D titles use the same explicit declaration, not an implicit exception. Draft acceptance must record actual human confirmation per embedded Scene with --confirm-embedded; never invent that confirmation. See `.studio/spec/broll-assets.md` for the contract.
