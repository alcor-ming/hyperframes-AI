---
{
  "component_id": "production-loop-core",
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
  "communication_goal": "Close the production cycle and reconnect its output to the next input.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "production_loop_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 9.8,
    "default_seconds": 9.8,
    "max_seconds": 9.8
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "production-loop-core-prototype-motion",
    "default_duration_seconds": 9.8,
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
    "file": "compositions/production-loop-core-prototype.html",
    "revision": 1,
    "sha256": "79d5967773ec4fa647d5f477c82bb7b0c980a928bdca3a1d9d5e11d851dced8b"
  }
}
---

# production-loop-core/16x9@v1

Production transport of the approved Open Design `production-loop-core-prototype.html` artifact.
