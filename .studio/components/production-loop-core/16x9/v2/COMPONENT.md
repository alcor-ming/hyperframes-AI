---
{
  "component_id": "production-loop-core",
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
  "communication_goal": "Close the production cycle and reconnect its output to the next input.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "production_loop_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 9.8,
    "default_seconds": 9.8,
    "max_seconds": 9.8
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "production-loop-core-prototype-motion",
    "default_duration_seconds": 9.8,
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
    "sha256": "4dec507fc0c7ce771a0502512a29355e8ff233d39b858b1de0a1e892b39f10e7"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# production-loop-core/16x9@v2

Stage/text projections preserving the source component layout and timeline.
