---
{
  "component_id": "chapter-intro",
  "version": 1,
  "status": "library-approved",
  "profile": "optical_fluidity",
  "subtemplate": "module_stage",
  "communication_goal": "Establish which module is entering, what it does, and where it sits in the sequence.",
  "semantic_roles": ["orientation", "transition"],
  "information_shapes": ["ordinal", "title", "short_summary", "active_media"],
  "state_change": {
    "input": "The previous module has completed and the next module is not yet the focus.",
    "transition": "Module identity and progress become legible while the evidence surface selects a local payload or its programmatic fallback.",
    "output": "The module identity remains readable and the next module can take over without an empty stage."
  },
  "evidence_modes": ["none", "image", "video"],
  "content_density": "medium",
  "duration_range": {
    "min_seconds": 1.2,
    "default_seconds": 1.6,
    "max_seconds": 3.0,
    "hero_hold_seconds": 0.02
  },
  "entry_contract": {
    "requires": ["module_stage", "previous_handoff_or_opening"],
    "accepts": "A new peer module with ordinal and title."
  },
  "exit_contract": {
    "provides": ["module_identity", "progress_context", "handoff_hold"],
    "hands_off_to": "The next module's own narrative mechanism."
  },
  "semantic_jobs": ["chapter_identity", "progress_context", "optional_source_preview"],
  "anti_use_cases": ["full_scene_argument", "repeated_page_header", "dashboard_summary", "evidence_required_for_layout"],
  "slots": {
    "required": [
      {"name": "chapter_index", "type": "string", "pattern": "^[0-9]{2}$", "description": "Two-digit module ordinal."},
      {"name": "chapter_total", "type": "integer", "minimum": 1, "maximum": 99, "description": "Total peer modules."},
      {"name": "title", "type": "string", "minLength": 1, "maxLength": 24, "description": "Module title."},
      {"name": "summary", "type": "string", "minLength": 1, "maxLength": 48, "description": "Short module function line."},
      {"name": "progress", "type": "number", "minimum": 0, "maximum": 1, "description": "Module position, not completion percentage."}
    ],
    "optional": [
      {"name": "icon", "type": "string", "nullable": true, "description": "Local icon or glyph reference."},
      {"name": "evidence", "type": "string", "nullable": true, "description": "Legacy local evidence path retained for Binding compatibility; the active surface uses evidence_primary."},
      {"name": "source_label", "type": "string", "nullable": true, "maxLength": 80, "description": "Local source label."},
      {"name": "previous_context", "type": "string", "nullable": true, "maxLength": 48, "description": "Minimum preceding-module context."}
    ]
  },
  "visual_surfaces": [
    {
      "surface_id": "evidence_primary",
      "kind": "active_media_card",
      "modes": ["none", "image", "video"],
      "required": true,
      "fallback": "programmatic"
    }
  ],
  "states": {
    "opening": "Previous context remains visible while the new module is not yet the focus.",
    "build": "Identity, summary, progress relation, and the evidence surface establish finite beats.",
    "hero": "The identity card and selected evidence payload are simultaneously legible.",
    "end": "Evidence and summary yield while identity and progress remain readable.",
    "handoff": "The stage can move to the next module without an empty frame."
  },
  "motion_recipe": {
    "recipe_id": "chapter-intro-reveal",
    "purpose": "Reveal module identity, establish progress, and yield to the module mechanism.",
    "motion_verb": "optical_fluidity.enter_build_hold_handoff",
    "stages": ["opening", "identity_build", "progress_and_evidence_build", "hero_hold", "handoff"],
    "default_duration_seconds": 1.6,
    "allowed_time_scale": {"min": 0.5, "max": 1.5},
    "seek_safe": true,
    "paused_timeline": true,
    "hero_state": "Identity card and selected evidence payload are clear at the Hero point."
  },
  "asset_contract": {
    "allowed_types": ["local_image", "local_video", "inline_svg"],
    "required": false,
    "root": "Work-local project assets",
    "runtime_network": false,
    "missing_optional": "Keep the evidence area structurally complete with the programmatic placeholder."
  },
  "preview": {
    "fixture": "preview.fixture.json",
    "key_times_seconds": [0.0, 0.7, 1.49, 1.6],
    "default_asset_free": true,
    "overflow_checks": ["short", "typical", "long", "optional_absent"]
  },
  "customization": {
    "allowed": ["slots", "surfaces", "position", "size", "offset", "time_scale", "hero_hold", "handoff_hold", "Work-local_media_paths"],
    "forbidden": ["internal_dom", "internal_css_structure", "state_order", "gsap_beats", "runtime_network"]
  },
  "artifact": {
    "provider": "open_design_mcp",
    "project": "Hyperframes",
    "file": "chapter-intro-prototype.html",
    "revision": 5,
    "sha256": "daf3e1f2ed2b9a45a45bba16ec9f156623ed7998a6d5322cbf72e209ce247652"
  }
}
---

# chapter-intro@v1

Open Design `Hyperframes` revision 5 and its recorded SHA-256 are the design
evidence and source-of-truth artifact for this release. This `component.html`
is the smallest production translation of that evidence: it preserves the
frozen geometry, states, and paused GSAP timeline while adding the HyperFrames
sub-composition transport and the `evidence_primary` payload surface. It is
not the Open Design frozen artifact itself.

Work-specific copy, timing, and local media belong in a Scene Binding and never
in this package. The default preview is asset-free; `none` uses the existing
programmatic evidence fallback.
