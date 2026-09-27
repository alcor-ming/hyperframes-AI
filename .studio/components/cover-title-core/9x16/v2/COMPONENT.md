---
{
  "component_id": "cover-title-core",
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
    "provider": "card-runtime-v351",
    "project": "Hyperframes",
    "file": "component.html",
    "revision": 2,
    "sha256": "fa14b7b26dc6b9316035121ec1fce0a948d3da97dd57f055abc8a351c2ad2264"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# cover-title-core/9x16@v2

Native portrait layout and stage/text projections derived from the source component content.
