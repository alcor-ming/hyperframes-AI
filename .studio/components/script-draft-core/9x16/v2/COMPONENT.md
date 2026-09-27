---
{
  "component_id": "script-draft-core",
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
  "communication_goal": "Turn selected material into a structured script draft.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "script_draft_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 4.26,
    "default_seconds": 4.26,
    "max_seconds": 4.26
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "script-draft-core-prototype-motion",
    "default_duration_seconds": 4.26,
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
    "sha256": "d6b0074a9e574bd288a23210324c08e8268d587bd618f0b1ddfee88d7a59705c"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# script-draft-core/9x16@v2

Native portrait layout and stage/text projections derived from the source component content.
