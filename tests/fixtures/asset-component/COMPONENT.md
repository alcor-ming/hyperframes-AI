---
{
  "component_id": "external-example",
  "ratio": "4x3",
  "version": 1,
  "contract": "component-contract-v2",
  "status": "migration-ready",
  "theme_tokens": [],
  "communication_goal": "Synthetic component for asset discovery and installation tests.",
  "semantic_roles": ["explanation"],
  "information_shapes": ["text"],
  "evidence_modes": ["none"],
  "content_density": "low",
  "duration_range": {"min_seconds": 1.6, "default_seconds": 1.6, "max_seconds": 1.6},
  "slots": {"required": [], "optional": []},
  "motion_recipe": {
    "allowed_time_scale": {"min": 0.8, "max": 1.2},
    "seek_safe": true,
    "paused_timeline": true
  },
  "asset_contract": {"allowed_types": [], "runtime_network": false},
  "customization": {"allowed": ["position", "size", "time_scale"]},
  "artifact": {"provider": "synthetic-test", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
}
---

# Synthetic test component

Test data only; no production or visual acceptance. Tests generate HASHES.json
in their temporary copy before packing or importing it.
