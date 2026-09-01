---
{
  "component_id": "rich-skill-explanation",
  "version": 2,
  "status": "library-approved",
  "profile": "optical_fluidity",
  "subtemplate": "module_stage",
  "communication_goal": "Introduce one capability with two explanatory statements and one mode-specific evidence lane.",
  "semantic_roles": ["explanation", "evidence", "handoff"],
  "information_shapes": ["sequence_position", "title", "ordered_explanation", "mode_specific_evidence", "trace"],
  "state_change": {
    "input": "The capability name is known but its operating pattern is still abstract.",
    "transition": "Two statements establish the capability while one finite evidence lane makes its relation visible.",
    "output": "The capability, operating pattern, and result trace remain legible for handoff."
  },
  "evidence_modes": ["none"],
  "content_density": "high",
  "duration_range": {"min_seconds": 12, "default_seconds": 12, "max_seconds": 12, "hero_hold_seconds": 2.5},
  "entry_contract": {
    "requires": ["module_stage", "skill_identity", "explanation_mode"],
    "accepts": "One capability, two explanation statements, and structured mode content."
  },
  "exit_contract": {
    "provides": ["explained_skill", "visible_relation", "result_trace"],
    "hands_off_to": "The next capability, a convergence scene, or a workflow result."
  },
  "semantic_jobs": ["skill_explanation", "relation_evidence", "result_trace"],
  "anti_use_cases": ["short_title_card", "media_showcase", "live_web_browser", "unbounded_step_list"],
  "slots": {
    "required": [
      {"name": "mode", "type": "string", "pattern": "^(input-transform|retrieve-distill|knowledge-roundtrip|persist-reuse)$", "description": "Evidence-lane layout."},
      {"name": "sequence_index", "type": "integer", "minimum": 1, "maximum": 20, "description": "Current item position."},
      {"name": "sequence_total", "type": "integer", "minimum": 1, "maximum": 20, "description": "Total peer items."},
      {"name": "title", "type": "string", "minLength": 1, "maxLength": 24, "description": "Capability name."},
      {"name": "subtitle", "type": "string", "minLength": 1, "maxLength": 32, "description": "Plain-language capability gloss."},
      {"name": "statement_1", "type": "string", "minLength": 1, "maxLength": 70, "description": "First explanatory statement."},
      {"name": "statement_2", "type": "string", "minLength": 1, "maxLength": 70, "description": "Second explanatory statement."},
      {"name": "trace_label", "type": "string", "minLength": 1, "maxLength": 16, "description": "Trace category."},
      {"name": "trace_value", "type": "string", "minLength": 1, "maxLength": 42, "description": "Concrete result or boundary trace."},
      {"name": "lane_kicker", "type": "string", "minLength": 1, "maxLength": 36, "description": "Evidence-lane proposition."},
      {"name": "source_items", "type": "array", "description": "Mode-specific source labels."},
      {"name": "result_items", "type": "array", "description": "Mode-specific result labels."},
      {"name": "mode_details", "type": "object", "description": "Named labels used by the selected evidence mode."}
    ],
    "optional": []
  },
  "visual_surfaces": [
    {"surface_id": "explanation_lane", "kind": "active_media_card", "modes": ["none"], "required": true, "fallback": "programmatic"}
  ],
  "states": {
    "opening": "Sequence, title, and capability gloss establish the subject.",
    "build": "The two statements resolve while the selected evidence lane begins its finite operation.",
    "hero": "The relation and its result trace are simultaneously legible.",
    "end": "The evidence lane settles without introducing new information.",
    "handoff": "The result trace remains available to the next scene."
  },
  "motion_recipe": {
    "recipe_id": "rich-skill-explanation-v2-chain",
    "purpose": "Pair dense explanatory copy with one of four reusable relation diagrams.",
    "motion_verb": "optical_fluidity.explain_transform_trace",
    "stages": ["opening", "copy_build", "mode_operation", "trace", "handoff"],
    "default_duration_seconds": 12,
    "allowed_time_scale": {"min": 0.8, "max": 1.2},
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "Both explanation statements, the resolved evidence lane, and the trace remain legible."
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "root": "No external payload; the evidence lane is programmatic.",
    "runtime_network": false,
    "missing_optional": "Render the frozen programmatic evidence lane."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [0, 3, 6.8, 9.4, 12],
    "default_asset_free": true,
    "overflow_checks": ["input_transform", "retrieve_distill", "knowledge_roundtrip", "persist_reuse"]
  },
  "customization": {
    "allowed": ["slots", "position", "size", "offset", "time_scale"],
    "forbidden": ["internal_dom", "internal_css_structure", "state_order", "gsap_beats", "runtime_network", "external_media"]
  },
  "artifact": {
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "rse-input-transform.html",
    "revision": 1,
    "sha256": "476932e90db050a194a9af78aec7f380c68a5cd70a91d8394f57186e1a22cf6e",
    "variants": {
      "retrieve-distill": "dc4e2086e8d2a539fe876d7906b66ade3c0ffb77eb7f0478cad22d791bdeffbc",
      "knowledge-roundtrip": "1df6fbf022ab9b9d81b1270145b01c344dc7ec14867ab808054b424d46adf551",
      "persist-reuse": "81e1f3914416460032448b3c2df408f040237d9af081a2a54d36b56065a0b7db"
    }
  }
}
---

# rich-skill-explanation@v2

One production component covers the four accepted Open Design artifacts through
the `mode` Slot. The artifacts differ only by their selected mode, so the public
release keeps one implementation instead of four duplicated packages.

The release is intended for dense capability introductions. Work-specific copy
and mode content belong in a Scene Binding; no runtime network or media asset is
required.
