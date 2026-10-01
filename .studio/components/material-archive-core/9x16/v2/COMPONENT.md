---
{
  "component_id": "material-archive-core",
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
    "provider": "card-runtime-v351",
    "project": "Hyperframes",
    "file": "component.html",
    "revision": 2,
    "sha256": "0b8d71344afafaa5a4db571145d945ecf0d05b18002af20aeb1d9b31ceec75d0"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# material-archive-core/9x16@v2

Card runtime stage/text projections; native portrait choreography preserving source content.
