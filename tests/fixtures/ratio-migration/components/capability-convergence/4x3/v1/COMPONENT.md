---
{
  "component_id": "capability-convergence",
  "ratio": "4x3",
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
    "sha256": "b14f51701cd490f26a7111747051c6f5885a20ef5037ff9e32140ad1ed55d6e2"
  }
}
---

# capability-convergence/4x3@v1

Synthetic ratio-migration fixture. It mirrors the migrated component contract
(transparent theme-aware template, closed package hashes, slot parity) without
depending on the removed `.studio/components` production tree.
