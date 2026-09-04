---
{
  "background_id": "rse-functional-background",
  "ratio": "4x3",
  "version": 1,
  "contract": "background-contract-v1",
  "status": "migration-ready",
  "theme_tokens": ["color.canvas", "color.surface", "color.text_primary", "color.text_secondary", "color.accent_primary"],
  "communication_goal": "Provide a continuous low-contrast graphite field behind foreground explanation components.",
  "semantic_roles": ["environment", "continuity"],
  "information_shapes": ["ambient_field", "masked_grid", "grain"],
  "state_change": {
    "input": "The stage begins as a flat graphite canvas.",
    "transition": "A restrained cyan field, grid, and grain establish depth without becoming a focal point.",
    "output": "The environment remains stable behind foreground components for the full sequence."
  },
  "evidence_modes": ["none"],
  "content_density": "low",
  "duration_range": {"min_seconds": 48, "default_seconds": 48, "max_seconds": 48, "hero_hold_seconds": 46.8},
  "entry_contract": {
    "requires": ["empty_full_frame_stage"],
    "accepts": "A 1440x1080 composition that needs a continuous background field."
  },
  "exit_contract": {
    "provides": ["stable_environment", "foreground_clearance"],
    "hands_off_to": "The end of the containing composition."
  },
  "semantic_jobs": ["background_environment", "scene_continuity"],
  "anti_use_cases": ["foreground_argument", "title_card", "evidence_display", "short_decorative_transition"],
  "slots": {"required": [], "optional": []},
  "visual_surfaces": [
    {"surface_id": "background_field", "kind": "active_media_card", "modes": ["none"], "required": true, "fallback": "programmatic"}
  ],
  "states": {
    "default": {
      "description": "Graphite canvas, restrained cyan depth, masked grid, and finite grain drift.",
      "seek": "Seek the single paused timeline directly; no wall-clock state is used."
    }
  },
  "default_state": "default",
  "motion_recipe": {
    "recipe_id": "rse-functional-background-drift",
    "purpose": "Maintain spatial continuity with one finite ambient drift.",
    "motion_verb": "background_establish_hold",
    "stages": ["canvas", "field_build", "finite_drift", "hold"],
    "default_duration_seconds": 48,
    "allowed_time_scale": {"min": 0.8, "max": 1.2},
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "A faint cyan graphite field and masked grid sit behind the foreground."
  },
  "asset_contract": {
    "allowed_types": [],
    "required": false,
    "root": "No external payload; the background field is programmatic.",
    "runtime_network": false,
    "missing_optional": "Render the frozen programmatic field."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [0, 0.9, 12, 24.4, 47.9],
    "default_asset_free": true,
    "overflow_checks": ["foreground_clearance", "full_duration_seek"]
  },
  "customization": {
    "allowed": ["position", "size", "offset", "time_scale"],
    "forbidden": ["internal_dom", "internal_css_structure", "state_order", "gsap_beats", "runtime_network", "foreground_content"]
  },
  "artifact": {
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "rse-functional-background.html",
    "revision": 1,
    "sha256": "e4bdf553ac9fce0edce62834a2ef218aeba2928d728b59e29b017a649134235a"
  }
}
---

# rse-functional-background/4x3@v1

This release is the production transport for the accepted Open Design
`rse-functional-background.html` artifact. It provides one finite, seek-safe
graphite environment and contains no foreground message or Work-specific data.
