---
{
  "component_id": "rse-knowledge-roundtrip",
  "ratio": "16x9",
  "version": 1,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "communication_goal": "Show local knowledge moving through read, retrieve, and write-back as one continuous round trip.",
  "semantic_roles": [
    "knowledge_flow",
    "roundtrip",
    "handoff"
  ],
  "information_shapes": [
    "source_notes",
    "retrieval_links",
    "write_back"
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
    "recipe_id": "rse-knowledge-roundtrip-chain",
    "purpose": "Show local knowledge moving through read, retrieve, and write-back as one continuous round trip.",
    "motion_verb": "read_retrieve_write_back",
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
    "file": "compositions/rse-knowledge-roundtrip.html",
    "revision": 1,
    "sha256": "06bb48fb540ab52fb45400ee67c6e9fb515da637c5a2d43c5bbd3318dbbb46b2"
  }
}
---

# rse-knowledge-roundtrip/16x9@v1

Production translation of the accepted Open Design artifact. The root is transparent, the timeline is finite and paused, and all environment rendering belongs to the selected Background Release.
