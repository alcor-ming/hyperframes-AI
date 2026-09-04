---
{
  "component_id": "cover-title-core",
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
    "file": "cover-title-core-prototype.html",
    "revision": 1,
    "sha256": "b2ecc38fe9657042ffd5ccc68a83fcfe82716926115e657d4364d24e6c7f055d"
  }
}
---

# cover-title-core/4x3@v1

Production transport of the approved Open Design `cover-title-core-prototype.html` artifact.
