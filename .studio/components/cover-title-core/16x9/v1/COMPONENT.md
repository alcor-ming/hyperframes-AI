---
{
  "component_id": "cover-title-core",
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
  "communication_goal": "Converge title candidates into one cover-ready headline.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "cover_title_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 5.6,
    "default_seconds": 5.6,
    "max_seconds": 5.6
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "cover-title-core-prototype-motion",
    "default_duration_seconds": 5.6,
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
    "file": "compositions/cover-title-core-prototype.html",
    "revision": 1,
    "sha256": "7e1353fe4b50494cd3cd83d435609894bd186e1207c06da7fd9b4c3acec6580c"
  }
}
---

# cover-title-core/16x9@v1

Production transport of the approved Open Design `cover-title-core-prototype.html` artifact.
