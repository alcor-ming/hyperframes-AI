---
{
  "component_id": "graphic-card-core",
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
  "communication_goal": "Compose a message into a finished graphic card.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "graphic_card_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 6.1,
    "default_seconds": 6.1,
    "max_seconds": 6.1
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "graphic-card-core-prototype-motion",
    "default_duration_seconds": 6.1,
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
    "sha256": "93af96b34152d6b231907b1eae654d8c79412f7e25f797f2c649d2e6d925cea6"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# graphic-card-core/16x9@v2

Stage/text projections preserving the source component layout and timeline.
