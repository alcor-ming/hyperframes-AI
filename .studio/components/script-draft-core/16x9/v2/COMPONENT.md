---
{
  "component_id": "script-draft-core",
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
    "sha256": "032a6484a71164042b3da0e5c56c0d4d75f7573540752ba6321889a4eea044bd"
  },
  "layers": [
    "stage",
    "text"
  ]
}
---

# script-draft-core/16x9@v2

Stage/text projections preserving the source component layout and timeline.
