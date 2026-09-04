---
{
  "component_id": "storyboard-plan-core",
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
  "communication_goal": "Assemble script, visual, asset, and timing layers into a storyboard plan.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "storyboard_plan_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 5.0,
    "default_seconds": 5.0,
    "max_seconds": 5.0
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "storyboard-plan-core-prototype-motion",
    "default_duration_seconds": 5.0,
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
    "file": "storyboard-plan-core-prototype.html",
    "revision": 1,
    "sha256": "0308690ad125a18837bac513e2421f95d99f603fe2b2769e182522323b1c72de"
  }
}
---

# storyboard-plan-core/4x3@v1

Production transport of the approved Open Design `storyboard-plan-core-prototype.html` artifact.
