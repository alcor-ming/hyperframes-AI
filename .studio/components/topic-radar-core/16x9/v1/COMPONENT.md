---
{
  "component_id": "topic-radar-core",
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
  "communication_goal": "Scan candidate topics and resolve one focused direction.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "topic_radar_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 5.8,
    "default_seconds": 5.8,
    "max_seconds": 5.8
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "topic-radar-core-prototype-motion",
    "default_duration_seconds": 5.8,
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
    "file": "compositions/topic-radar-core-prototype.html",
    "revision": 1,
    "sha256": "296d4c8eba1a9aa1167f4d9166b096e88d046b5ffca50eed3c30985664daa3c2"
  }
}
---

# topic-radar-core/16x9@v1

Production transport of the approved Open Design `topic-radar-core-prototype.html` artifact.
