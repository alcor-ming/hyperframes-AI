---
{
  "component_id": "chapter-intro",
  "ratio": "4x3",
  "version": 1,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "theme_tokens": ["color.canvas", "color.surface", "color.text_primary", "color.text_secondary", "color.accent_primary", "color.accent_secondary", "font.display", "font.body", "font.mono"],
  "communication_goal": "Introduce a synthetic chapter and establish its place in the sequence.",
  "semantic_roles": ["chapter", "orientation"],
  "content_density": "low",
  "duration_range": {"min_seconds": 1.6, "default_seconds": 1.6, "max_seconds": 1.6},
  "customization": {"allowed": ["slots", "position", "size", "offset", "time_scale"]},
  "preview": {"fixture": "preview.fixture.json", "key_times_seconds": [0, 0.8, 1.6]},
  "artifact": {
    "provider": "synthetic_fixture",
    "project": "ratio-migration",
    "file": "artifact.html",
    "revision": 1,
    "sha256": "59fd169039cc2ddd5003fc28231a8a43cbb9f9d3272f1c40dd6e1fcb7f709854"
  }
}
---

# chapter-intro/4x3@v1

Synthetic ratio-migration fixture. It mirrors the migrated component contract
(transparent theme-aware template, closed package hashes, slot parity) without
depending on the removed `.studio/components` production tree.
