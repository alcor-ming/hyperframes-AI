---
{
  "component_id": "graphic-card-core",
  "ratio": "4x3",
  "version": 1,
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
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "graphic-card-core-prototype.html",
    "revision": 1,
    "sha256": "7f0021fecc8ebd7fb065caceac1c4be9cbe2e76f565cc727336690f39654a0d3"
  }
}
---

# graphic-card-core/4x3@v1

Production transport of the approved Open Design `graphic-card-core-prototype.html` artifact.
