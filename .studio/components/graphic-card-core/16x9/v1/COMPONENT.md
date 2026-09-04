---
{
  "component_id": "graphic-card-core",
  "ratio": "16x9",
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
    "file": "compositions/graphic-card-core-prototype.html",
    "revision": 1,
    "sha256": "e7a1650242dde5d2c19f06cfdc5ef46cd5058daa88442e090cd4bd861f71221c"
  }
}
---

# graphic-card-core/16x9@v1

Production transport of the approved Open Design `graphic-card-core-prototype.html` artifact.
