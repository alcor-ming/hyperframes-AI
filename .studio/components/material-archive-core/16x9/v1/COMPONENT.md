---
{
  "component_id": "material-archive-core",
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
  "communication_goal": "Classify finished material into a reusable archive.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "material_archive_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 6.6,
    "default_seconds": 6.6,
    "max_seconds": 6.6
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "material-archive-core-prototype-motion",
    "default_duration_seconds": 6.6,
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
    "file": "compositions/material-archive-core-prototype.html",
    "revision": 1,
    "sha256": "ae36dcd2ff503a3180d670efe5d587df3925bdc9ddd757b8e9facce7d6afe9a3"
  }
}
---

# material-archive-core/16x9@v1

Production transport of the approved Open Design `material-archive-core-prototype.html` artifact.
