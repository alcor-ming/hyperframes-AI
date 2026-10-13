---
{
  "component_id": "gap-first-selection",
  "version": 1,
  "status": "library-approved",
  "profile": "optical_fluidity",
  "subtemplate": "module_stage",
  "communication_goal": "Resolve candidate overload by finding one workflow bottleneck, matching one tool, and testing it for three days before asking the audience to respond.",
  "semantic_roles": ["selection", "diagnosis", "trial", "cta"],
  "information_shapes": ["ten_candidate_pool", "four_step_workflow", "single_gap", "single_match", "three_day_trial", "final_question"],
  "state_change": {
    "input": "Ten candidates are available but none is yet justified by the user's workflow.",
    "transition": "A scan exposes one workflow gap, pulls the matching candidate into it, and carries that choice through a three-day trial.",
    "output": "The trial resolves into one question with a primary response action and a restrained secondary action."
  },
  "evidence_modes": ["none"],
  "content_density": "medium",
  "duration_range": {"min_seconds": 16.964, "default_seconds": 16.964, "max_seconds": 16.964, "hero_hold_seconds": 1.564},
  "entry_contract": {
    "requires": ["ten_candidates", "one_workflow_gap", "one_selected_candidate"],
    "accepts": "Exactly ten candidates, four workflow labels, one selected index, and one bottleneck statement."
  },
  "exit_contract": {
    "provides": ["matched_tool", "three_day_trial", "final_question", "cta_handoff"],
    "hands_off_to": "Audience response, a recommendation detail, or the end of the composition."
  },
  "semantic_jobs": ["workflow_gap_diagnosis", "single_tool_selection", "trial_commitment", "audience_question"],
  "anti_use_cases": ["candidate_count_not_ten", "multi_select", "ranked_recommendations", "app_store_grid", "installation_controls", "workflow_without_a_real_gap"],
  "slots": {
    "required": [
      {"name": "context", "type": "string", "minLength": 1, "maxLength": 40, "description": "Sequence and section context."},
      {"name": "pool_label", "type": "string", "minLength": 1, "maxLength": 16, "description": "Candidate-pool label."},
      {"name": "candidates", "type": "array", "description": "Exactly ten candidate identities and their profile tones."},
      {"name": "selected_index", "type": "integer", "minimum": 1, "maximum": 10, "description": "One-based candidate selected by the visible gap."},
      {"name": "warning", "type": "string", "minLength": 1, "maxLength": 16, "description": "Opening selection warning."},
      {"name": "warning_detail", "type": "string", "minLength": 1, "maxLength": 30, "description": "Short diagnostic instruction."},
      {"name": "workflow_label", "type": "string", "minLength": 1, "maxLength": 20, "description": "Workflow owner label."},
      {"name": "workflow_nodes", "type": "array", "description": "Exactly four short workflow steps around the gap."},
      {"name": "bottleneck_kicker", "type": "string", "minLength": 1, "maxLength": 24, "description": "Bottleneck field name."},
      {"name": "bottleneck_label", "type": "string", "minLength": 1, "maxLength": 24, "description": "Visible workflow problem."},
      {"name": "trial_prefix", "type": "string", "minLength": 1, "maxLength": 20, "description": "Three-day trial lead-in."},
      {"name": "trial_emphasis", "type": "string", "minLength": 1, "maxLength": 16, "description": "Emphasized trial commitment."},
      {"name": "usage_label", "type": "string", "minLength": 1, "maxLength": 8, "description": "Repeated daily-use trace."},
      {"name": "hero_kicker", "type": "string", "minLength": 1, "maxLength": 24, "description": "Final principle above the question."},
      {"name": "question", "type": "string", "minLength": 1, "maxLength": 30, "description": "Final audience question."},
      {"name": "primary_cta", "type": "string", "minLength": 1, "maxLength": 20, "description": "Primary response action."},
      {"name": "secondary_primary", "type": "string", "minLength": 1, "maxLength": 16, "description": "Short secondary action."},
      {"name": "secondary_secondary", "type": "string", "minLength": 1, "maxLength": 40, "description": "Secondary follow-up action."}
    ],
    "optional": []
  },
  "visual_surfaces": [
    {"surface_id": "selection_flow", "kind": "active_media_card", "modes": ["none"], "required": true, "fallback": "programmatic"}
  ],
  "states": {
    "opening": "Ten colored candidate marks converge into a bounded pool.",
    "build": "A separate workflow appears, is scanned, exposes one gap, and receives one matching candidate.",
    "hero": "The matched candidate completes a continuous three-day trial and resolves into the final question.",
    "end": "The question and action hierarchy remain still and fully legible.",
    "handoff": "The primary response action remains dominant while the secondary action stays on the footer rail."
  },
  "motion_recipe": {
    "recipe_id": "gap-first-selection-scan-match-trial",
    "purpose": "Make the selection causal: expose the gap before moving one candidate into it.",
    "motion_verb": "optical_fluidity.scan_match_commit",
    "stages": ["candidate_pool", "workflow_build", "gap_scan", "candidate_match", "three_day_trial", "question_handoff"],
    "default_duration_seconds": 16.964,
    "allowed_time_scale": {"min": 0.8, "max": 1.2},
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "The question and CTA hierarchy replace the compacted selection history after the three-day trace completes."
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "root": "No external payload; the candidate pool, workflow, gap, trial, and CTA are programmatic.",
    "runtime_network": false,
    "missing_optional": "Render the frozen programmatic selection flow."
  },
  "profile_tokens": {
    "canvas": "#0b0b0f",
    "ink": "#f5f1ea",
    "relation": "#9bd6bd",
    "candidate_tones": ["#54d7ff", "#ffb76b", "#9bd6bd", "#7da4ff", "#d6a8ff"]
  },
  "anti_ppt": {
    "required_change": "The workflow gap must visibly cause the single selection and the trial must preserve continuity.",
    "forbidden": ["ten_equal_cards", "checkbox_grid", "candidate_ranking", "three_equal_day_cards", "decorative_fade_sequence"]
  },
  "layout_safety": {
    "canvas": "1440x1080",
    "safe_inset": "80px horizontal, 54px top, 44px bottom",
    "long_copy_policy": "Use the declared Slot maxima; do not shrink the final question below its frozen type size."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [0, 2.2, 4.6, 7.42, 11.24, 15.4, 16.964],
    "default_asset_free": true,
    "overflow_checks": ["maximum_candidate_label", "maximum_question", "four_workflow_nodes"]
  },
  "customization": {
    "allowed": ["slots", "position", "size", "offset", "time_scale"],
    "forbidden": ["candidate_count", "workflow_node_count", "internal_dom", "internal_css_structure", "state_order", "gsap_beats", "runtime_network", "external_media"]
  },
  "artifact": {
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "gap-first-selection-core-prototype.html",
    "revision": 1,
    "sha256": "891f39fdc58437e9f5689cdc3ba9876dff8a84eaa6c3f2a9516579bd82ff0237"
  }
}
---

# gap-first-selection@v1

This release translates the accepted Open Design artifact into one frozen,
seek-safe selection component. Work-specific candidate names and CTA copy belong
in a Scene Binding; the ten-to-one scan, match, and three-day trial remain fixed.
