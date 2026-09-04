---
{
  "component_id": "chapter-intro",
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
  "communication_goal": "Introduce a chapter and establish its place in the sequence.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "chapter_intro"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 1.6,
    "default_seconds": 1.6,
    "max_seconds": 1.6
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "chapter-intro-prototype-motion",
    "default_duration_seconds": 1.6,
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
    "file": "compositions/chapter-intro-prototype.html",
    "revision": 1,
    "sha256": "c21dadacd17e2fa9f82835cd46c10e65ee2907ee3fe1890d46976f7a10d53424"
  }
}
---

# chapter-intro/16x9@v1

Production transport of the approved Open Design `chapter-intro-prototype.html` artifact.
