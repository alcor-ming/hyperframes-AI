---
{
  "component_id": "chapter-intro",
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
    "provider": "card-runtime-v351",
    "project": "Hyperframes",
    "file": "component.html",
    "revision": 2,
    "sha256": "28d385e9ee3b19c52d7c800084a0babbd2afdb52e017e7b81c6a4957179c3dc3"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# chapter-intro/9x16@v2

Native portrait layout and stage/text projections derived from the source component content.
