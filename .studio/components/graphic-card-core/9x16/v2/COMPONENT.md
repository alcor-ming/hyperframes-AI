---
{
  "component_id": "graphic-card-core",
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
    "sha256": "5f7796840e82992db6d1c902474a6c480bb47754571342633d4eeb2857dbfe33"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# graphic-card-core/9x16@v2

Native portrait layout and stage/text projections derived from the source component content.
