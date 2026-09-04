---
{
  "component_id": "weekly-report-core",
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
  "communication_goal": "Condense weekly activity into a legible report and conclusion.",
  "semantic_roles": [
    "explanation",
    "transition"
  ],
  "information_shapes": [
    "weekly_report_core"
  ],
  "evidence_modes": [
    "none"
  ],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 6.4,
    "default_seconds": 6.4,
    "max_seconds": 6.4
  },
  "slots": {
    "required": [],
    "optional": []
  },
  "motion_recipe": {
    "recipe_id": "weekly-report-core-prototype-motion",
    "default_duration_seconds": 6.4,
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
    "file": "weekly-report-core-prototype.html",
    "revision": 1,
    "sha256": "ef3592b6f27421891728d8b0077b5e93554dde13bbca6d8a41ad05998af5541b"
  }
}
---

# weekly-report-core/4x3@v1

Production transport of the approved Open Design `weekly-report-core-prototype.html` artifact.
