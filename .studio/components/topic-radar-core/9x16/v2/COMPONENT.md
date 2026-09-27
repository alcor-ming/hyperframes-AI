---
{
  "component_id": "topic-radar-core",
  "ratio": "9x16",
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
  "communication_goal": "Scan candidate topics and resolve one focused direction.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "topic_radar_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 5.8,
    "default_seconds": 5.8,
    "max_seconds": 5.8
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "topic-radar-core-prototype-motion",
    "default_duration_seconds": 5.8,
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
    "sha256": "8e8de164b60817ceac74467072b4c30a2183aa6ed4aa54d4c40fe24017531988"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# topic-radar-core/9x16@v2

Card runtime stage/text projections; native portrait choreography preserving source content.
