---
{
  "component_id": "opening-weave-core",
  "ratio": "16x9",
  "version": 2,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "theme_tokens": [
    "color.canvas",
    "color.surface",
    "color.text_primary",
    "color.text_secondary",
    "color.accent_primary",
    "color.accent_secondary",
    "font.display",
    "font.body",
    "font.mono"
  ],
  "communication_goal": "Weave source fragments into one opening proposition.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "opening_weave_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 4.8,
    "default_seconds": 4.8,
    "max_seconds": 4.8
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "opening-weave-core-prototype-motion",
    "default_duration_seconds": 4.8,
    "allowed_time_scale": {
      "min": 0.8,
      "max": 1.2
    },
    "seek_safe": true,
    "paused_timeline": true
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "runtime_network": false
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
      "runtime_network"
    ]
  },
  "artifact": {
    "provider": "card-runtime-v351",
    "project": "Hyperframes",
    "file": "component.html",
    "revision": 2,
    "sha256": "a0b92747965573fd1ce7498d54c2ec0396eeafa58623243691bf0272a5013db2"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# opening-weave-core/16x9@v2

Stage/text projections preserving the source component layout and timeline.
