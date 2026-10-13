---
{
  "component_id": "capability-convergence",
  "ratio": "16x9",
  "version": 1,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "theme_tokens": ["color.canvas", "color.surface", "color.text_primary", "color.text_secondary", "color.accent_primary", "color.accent_secondary", "font.display", "font.body", "font.mono"],
  "communication_goal": "Converge five synthetic capability traces into one named shared capability.",
  "semantic_roles": ["recap", "convergence", "handoff"],
  "content_density": "high",
  "duration_range": {"min_seconds": 12.7, "default_seconds": 12.7, "max_seconds": 12.7},
  "customization": {"allowed": ["slots", "position", "size", "offset", "time_scale"]},
  "preview": {"fixture": "preview.fixture.json", "key_times_seconds": [0, 2, 6, 9.6, 12.5]},
  "artifact": {
    "provider": "synthetic_fixture",
    "project": "ratio-migration",
    "file": "artifact.html",
    "revision": 1,
    "sha256": "42f6cc3bb5ecae8174b8f384cff5e2c8e51e35bdea1ece79cb02336e14cfa5a4"
  }
}
---

# capability-convergence/16x9@v1

Synthetic ratio-migration fixture. It mirrors the migrated component contract
(transparent theme-aware template, closed package hashes, slot parity) without
depending on the removed `.studio/components` production tree.
