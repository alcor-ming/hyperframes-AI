---
{
  "component_id": "tone-rewrite-core",
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
  "communication_goal": "Transform a draft into a clearer human tone while preserving meaning.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "tone_rewrite_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 5.9,
    "default_seconds": 5.9,
    "max_seconds": 5.9
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "tone-rewrite-core-prototype-motion",
    "default_duration_seconds": 5.9,
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
    "sha256": "39491a1b5a6c34c9b8decef7b1e5c368dfdfbb9dd5fd22ac2228b1769a00a50b"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# tone-rewrite-core/16x9@v2

Stage/text projections preserving the source component layout and timeline.
