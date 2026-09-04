---
{
  "component_id": "rse-persist-reuse",
  "ratio": "4x3",
  "version": 1,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "communication_goal": "Show one corrected rule persisting into and improving a later related task.",
  "semantic_roles": [
    "memory",
    "reuse",
    "handoff"
  ],
  "information_shapes": [
    "first_session",
    "persisted_rule",
    "later_session"
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
    "recipe_id": "rse-persist-reuse-chain",
    "purpose": "Show one corrected rule persisting into and improving a later related task.",
    "motion_verb": "capture_persist_reuse",
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
    "file": "rse-persist-reuse.html",
    "revision": 1,
    "sha256": "5cb25650a8e1ff9c94a8ad401ccd88d6777d3f7f2dc7d97e6e9acdc350d62e53"
  }
}
---

# rse-persist-reuse/4x3@v1

Production translation of the accepted Open Design artifact. The root is transparent, the timeline is finite and paused, and all environment rendering belongs to the selected Background Release.
