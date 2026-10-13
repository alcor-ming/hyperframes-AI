---
{
  "component_id": "rich-skill-explanation",
  "version": 1,
  "status": "library-approved",
  "profile": "optical_fluidity",
  "subtemplate": "module_stage",
  "communication_goal": "Explain one complex Skill through staged copy, a programmatic evidence demo, and a concrete result handoff.",
  "semantic_roles": [
    "explanation",
    "evidence",
    "handoff"
  ],
  "information_shapes": [
    "sequence_position",
    "title",
    "ordered_explanation",
    "programmatic_demo",
    "result"
  ],
  "state_change": {
    "input": "A Skill name and its role are known, but its operation and result are not yet concrete.",
    "transition": "The explanation grows beside one finite simulated operation whose outcome becomes a captured result card.",
    "output": "The Skill's use, conditions, and result remain legible while the evidence window yields."
  },
  "evidence_modes": [
    "none"
  ],
  "content_density": "high",
  "duration_range": {
    "min_seconds": 9.6,
    "default_seconds": 12.27,
    "max_seconds": 14.27,
    "hero_hold_seconds": 0
  },
  "entry_contract": {
    "requires": [
      "module_stage",
      "skill_identity"
    ],
    "accepts": "One Skill explanation with two required statements and one optional third statement."
  },
  "exit_contract": {
    "provides": [
      "explained_skill",
      "captured_result",
      "handoff_hold"
    ],
    "hands_off_to": "The next Skill, comparison, or workflow result."
  },
  "semantic_jobs": [
    "skill_explanation",
    "operation_evidence",
    "result_capture"
  ],
  "anti_use_cases": [
    "short_title_card",
    "dashboard_summary",
    "live_web_browser",
    "unbounded_step_list"
  ],
  "slots": {
    "required": [
      {
        "name": "context",
        "type": "string",
        "minLength": 1,
        "maxLength": 40,
        "description": "Top-left explanation context."
      },
      {
        "name": "sequence_index",
        "type": "integer",
        "minimum": 1,
        "maximum": 20,
        "description": "Current item position."
      },
      {
        "name": "sequence_total",
        "type": "integer",
        "minimum": 1,
        "maximum": 20,
        "description": "Total peer items."
      },
      {
        "name": "title",
        "type": "string",
        "minLength": 1,
        "maxLength": 24,
        "description": "Skill or capability name."
      },
      {
        "name": "subtitle",
        "type": "string",
        "minLength": 1,
        "maxLength": 32,
        "description": "Plain-language capability gloss."
      },
      {
        "name": "address",
        "type": "string",
        "minLength": 1,
        "maxLength": 80,
        "description": "Short source or tool context shown in the simulated browser chrome."
      },
      {
        "name": "result_label",
        "type": "string",
        "minLength": 1,
        "maxLength": 32,
        "description": "Concrete result label."
      },
      {
        "name": "demo_type",
        "type": "string",
        "pattern": "^(browser-click|skill-create|file-download)$",
        "description": "Frozen programmatic evidence mechanism."
      },
      {
        "name": "duration_seconds",
        "type": "number",
        "minimum": 9.6,
        "maximum": 14.27,
        "description": "Internal component duration before time scaling."
      },
      {
        "name": "segment_1_label",
        "type": "string",
        "minLength": 1,
        "maxLength": 20,
        "description": "First explanation label."
      },
      {
        "name": "segment_1_text",
        "type": "string",
        "minLength": 1,
        "maxLength": 42,
        "description": "First explanation statement."
      },
      {
        "name": "segment_2_label",
        "type": "string",
        "minLength": 1,
        "maxLength": 20,
        "description": "Second explanation label."
      },
      {
        "name": "segment_2_text",
        "type": "string",
        "minLength": 1,
        "maxLength": 42,
        "description": "Second explanation statement."
      },
      {
        "name": "segment_3_mode",
        "type": "string",
        "pattern": "^(none|text|skeleton)$",
        "description": "Optional third explanation treatment."
      }
    ],
    "optional": [
      {
        "name": "segment_3_label",
        "type": "string",
        "nullable": true,
        "maxLength": 20,
        "description": "Third explanation label."
      },
      {
        "name": "segment_3_text",
        "type": "string",
        "nullable": true,
        "maxLength": 42,
        "description": "Third explanation statement when mode is text."
      },
      {
        "name": "segment_3_note",
        "type": "string",
        "nullable": true,
        "maxLength": 120,
        "description": "Condition note when mode is skeleton."
      }
    ]
  },
  "visual_surfaces": [
    {
      "surface_id": "demo_primary",
      "kind": "active_media_card",
      "modes": [
        "none"
      ],
      "required": true,
      "fallback": "programmatic"
    }
  ],
  "states": {
    "opening": "Context, sequence position, title, and the evidence window establish the Skill.",
    "build": "The finite operation advances while explanation statements appear from the same action cues.",
    "hero": "The evidence outcome becomes the result card and both are briefly legible.",
    "end": "The evidence window exits while the captured result stays anchored.",
    "handoff": "The result card remains as the next scene takes over."
  },
  "motion_recipe": {
    "recipe_id": "rich-skill-explanation-chain",
    "purpose": "Tie dense explanatory copy to one visible operation and its captured result.",
    "motion_verb": "optical_fluidity.enter_operate_capture_handoff",
    "stages": [
      "opening",
      "operation_build",
      "result_capture",
      "hero",
      "handoff"
    ],
    "default_duration_seconds": 12.27,
    "allowed_time_scale": {
      "min": 0.8,
      "max": 1.2
    },
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "The result card has landed at lower left while the evidence window begins yielding."
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "root": "No external payload; the evidence demo is programmatic.",
    "runtime_network": false,
    "missing_optional": "Render the frozen programmatic evidence demo."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [
      0,
      3,
      8.5,
      11.35,
      12.27
    ],
    "default_asset_free": true,
    "overflow_checks": [
      "short_two_segment",
      "typical_two_segment",
      "long_three_segment"
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
    "file": "rich-skill-explanation-prototype.html",
    "revision": 3,
    "sha256": "020b80ab8d493ace6bd99171aeb037d897deb2a93ad215e10078b25cc637083a"
  }
}
---

# rich-skill-explanation@v1

Open Design project `Hyperframes`, artifact `rich-skill-explanation-prototype.html`
revision 3, is the recorded design evidence for this release. The production
translation removes only the prototype inspection toolbar, replaces sample
selection with explicit Slots, and keeps the frozen 1440x1080 geometry,
programmatic demos, action-linked copy cues, result capture, and paused GSAP
timeline.

Work-specific copy and timing belong in a Scene Binding. The public package has
no runtime network or external media dependency; `demo_primary` always uses its
programmatic fallback.
