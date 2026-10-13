---
{
  "component_id": "capability-convergence",
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
  "communication_goal": "Converge five prior capability traces into one named shared capability.",
  "semantic_roles": [
    "recap",
    "convergence",
    "handoff"
  ],
  "information_shapes": [
    "five_traces",
    "progressive_convergence",
    "shared_capability",
    "summary"
  ],
  "state_change": {
    "input": "Five capability results are visible as separate traces.",
    "transition": "Each trace travels into one shared ring and becomes a persistent segment.",
    "output": "The completed ring names the shared capability and exposes its practical meaning."
  },
  "evidence_modes": [
    "none"
  ],
  "content_density": "high",
  "duration_range": {
    "min_seconds": 12.7,
    "default_seconds": 12.7,
    "max_seconds": 12.7,
    "hero_hold_seconds": 1.7
  },
  "entry_contract": {
    "requires": [
      "five_prior_results",
      "shared_capability_name"
    ],
    "accepts": "Exactly five indexed capability traces and one shared conclusion."
  },
  "exit_contract": {
    "provides": [
      "completed_convergence",
      "named_shared_capability",
      "handoff_marker"
    ],
    "hands_off_to": "The next capability group or summary scene."
  },
  "semantic_jobs": [
    "capability_recap",
    "result_convergence",
    "shared_capability_naming"
  ],
  "anti_use_cases": [
    "fewer_than_five_items",
    "more_than_five_items",
    "unrelated_item_list",
    "media_showcase"
  ],
  "slots": {
    "required": [
      {
        "name": "context",
        "type": "string",
        "minLength": 1,
        "maxLength": 40,
        "description": "Section context shown at top right."
      },
      {
        "name": "items",
        "type": "array",
        "description": "Exactly five indexed capability traces."
      },
      {
        "name": "proposition",
        "type": "string",
        "minLength": 1,
        "maxLength": 32,
        "description": "Five-to-one convergence statement."
      },
      {
        "name": "core_name",
        "type": "string",
        "minLength": 1,
        "maxLength": 12,
        "description": "Shared capability name."
      },
      {
        "name": "summary_emphasis",
        "type": "string",
        "minLength": 1,
        "maxLength": 34,
        "description": "Emphasized practical definition."
      },
      {
        "name": "summary_suffix",
        "type": "string",
        "minLength": 1,
        "maxLength": 34,
        "description": "Definition completion."
      },
      {
        "name": "handoff_label",
        "type": "string",
        "minLength": 1,
        "maxLength": 12,
        "description": "Next-section marker."
      }
    ],
    "optional": []
  },
  "visual_surfaces": [
    {
      "surface_id": "convergence_field",
      "kind": "active_media_card",
      "modes": [
        "none"
      ],
      "required": true,
      "fallback": "programmatic"
    }
  ],
  "states": {
    "opening": "Five result traces establish the source set.",
    "build": "The traces converge one by one and increment the shared ring.",
    "hero": "The completed ring reveals the shared capability and summary.",
    "end": "The complete five-to-one relation holds.",
    "handoff": "A single marker points to the next section."
  },
  "motion_recipe": {
    "recipe_id": "capability-convergence-five-to-one",
    "purpose": "Preserve five source identities while resolving their shared capability.",
    "motion_verb": "trace_converge_name",
    "stages": [
      "opening",
      "trace_convergence",
      "ring_completion",
      "capability_reveal",
      "handoff"
    ],
    "default_duration_seconds": 12.7,
    "allowed_time_scale": {
      "min": 0.8,
      "max": 1.2
    },
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "Five dimmed source labels orbit a completed ring around the shared capability."
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "root": "No external payload; the convergence field is programmatic.",
    "runtime_network": false,
    "missing_optional": "Render the frozen programmatic convergence field."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [
      0,
      2,
      6,
      9.6,
      12.5
    ],
    "default_asset_free": true,
    "overflow_checks": [
      "typical_five_items",
      "maximum_labels"
    ]
  },
  "customization": {
    "allowed": [
      "slots",
      "position",
      "size",
      "offset",
      "time_scale"
    ],
    "forbidden": [
      "item_count",
      "internal_dom",
      "internal_css_structure",
      "state_order",
      "gsap_beats",
      "runtime_network",
      "external_media"
    ]
  },
  "artifact": {
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "compositions/capability-convergence-v1.html",
    "revision": 1,
    "sha256": "7a5b7a5d426bdefd3558a36877914925ec5bf9c9a7c87101811c6dae8c1b4806"
  }
}
---

# capability-convergence/16x9@v1

This release translates the accepted Open Design artifact into one frozen,
seek-safe five-to-one convergence component. Work-specific labels belong in a
Scene Binding; the item count and internal motion remain fixed.
