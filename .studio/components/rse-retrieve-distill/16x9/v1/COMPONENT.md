---
{
  "component_id": "rse-retrieve-distill",
  "ratio": "16x9",
  "version": 1,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "communication_goal": "Show noisy retrieval results being reduced to a concise, traceable evidence set.",
  "semantic_roles": [
    "retrieval",
    "distillation",
    "handoff"
  ],
  "information_shapes": [
    "result_set",
    "filtering_path",
    "distilled_evidence"
  ],
  "state_change": {
    "input": "The source material is visible but not yet usable by the next step.",
    "transition": "One finite programmatic motion chain exposes the transformation.",
    "output": "The resolved result remains legible for handoff."
  },
  "duration_range": {
    "min_seconds": 12,
    "default_seconds": 12,
    "max_seconds": 12,
    "hero_hold_seconds": 1
  },
  "entry_contract": {
    "requires": [
      "source_state"
    ],
    "accepts": "One fixed conceptual transformation."
  },
  "exit_contract": {
    "provides": [
      "resolved_result",
      "handoff_state"
    ],
    "hands_off_to": "The next workflow step or explanation."
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "states": {
    "opening": "Identity and source state establish.",
    "build": "The transformation advances through one causal path.",
    "hero": "The resolved output and its provenance are visible together.",
    "end": "The output holds without introducing a new action.",
    "handoff": "The resolved output remains available to the next scene."
  },
  "motion_recipe": {
    "recipe_id": "rse-retrieve-distill-chain",
    "purpose": "Show noisy retrieval results being reduced to a concise, traceable evidence set.",
    "motion_verb": "retrieve_filter_distill",
    "stages": [
      "opening",
      "build",
      "hero",
      "handoff"
    ],
    "default_duration_seconds": 12,
    "allowed_time_scale": {
      "min": 0.8,
      "max": 1.2
    },
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "The output and its causal path are simultaneously legible."
  },
  "theme_tokens": [
    "color.surface",
    "color.text_primary",
    "color.text_secondary",
    "color.accent_primary",
    "color.accent_secondary",
    "font.display",
    "font.body",
    "font.mono"
  ],
  "layering": {
    "root": "transparent",
    "position": "above_background"
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "runtime_network": false,
    "missing_optional": "Render the frozen programmatic demonstration."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [
      0,
      2.4,
      6,
      9.5,
      11.9
    ],
    "default_asset_free": true
  },
  "customization": {
    "allowed": [
      "position",
      "size",
      "offset",
      "time_scale"
    ],
    "forbidden": [
      "internal_dom",
      "internal_css_structure",
      "state_order",
      "gsap_beats",
      "runtime_network",
      "full_frame_background"
    ]
  },
  "artifact": {
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "compositions/rse-retrieve-distill.html",
    "revision": 1,
    "sha256": "1e048034b1343ff51e33b78d9ee9c3f9b1d073b053d059a7fb75270e081a5f47"
  }
}
---

# rse-retrieve-distill/16x9@v1

Production translation of the accepted Open Design artifact. The root is transparent, the timeline is finite and paused, and all environment rendering belongs to the selected Background Release.
