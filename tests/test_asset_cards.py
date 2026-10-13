"""v4.2 card-asset discovery, references, localize and compare (D9/D10/D16).

Discovery reads design-card asset libraries through the catalog API. The
catalog is stubbed here until the P2 catalog lands, as allowed by the handoff.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / ".studio"))
import asset_contract as CONTRACT
import asset_store as STORE
import designs


class CardAssetTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.designs_root = self.root / "designs"
        self.cards = {}
        self.write_card("my-card", references=["kit/tone"])
        self.write_card("kit", references=[])
        self.write_asset("my-card", "signal-card", body="window.signalCard = 1;", tags=["demo"])
        self.write_asset("kit", "tone", body="export const tone = 1;")
        catalog = patch.object(designs, "catalog_report", lambda root=None, config=None: (self.cards, []))
        card_path = patch.object(designs, "card_path",
                                 lambda identity, root=None, config=None: self.designs_root / identity,
                                 create=True)
        catalog.start(); card_path.start()
        self.addCleanup(catalog.stop); self.addCleanup(card_path.stop)

    def write_card(self, card_id, *, references):
        card = self.designs_root / card_id
        card.mkdir(parents=True)
        payload = {"id": card_id, "version": 1, "references": references}
        (card / "design.json").write_text(json.dumps(payload), encoding="utf-8")
        self.cards[card_id] = payload

    def write_asset(self, card_id, asset_id, *, body, tags=None):
        directory = self.designs_root / card_id / "assets" / asset_id
        directory.mkdir(parents=True)
        metadata = {"schema_version": 1, "id": asset_id, "version": 1, "kind": "module",
                    "entry": "main.js", "purpose": f"{asset_id} asset"}
        if tags is not None:
            metadata["tags"] = tags
        (directory / "asset.json").write_text(json.dumps(metadata), encoding="utf-8")
        (directory / "main.js").write_text(body, encoding="utf-8")
        return directory

    def rows(self, **kwargs):
        return STORE.discover_components(self.root, **kwargs)

    def test_discovers_card_assets_with_card_identity(self):
        assets = self.rows()["assets"]
        self.assertEqual(["kit/tone", "my-card/signal-card"], [row["component_ref"] for row in assets])
        row = next(item for item in assets if item["component_ref"] == "my-card/signal-card")
        self.assertEqual("card", row["origin"])
        self.assertTrue(row["available"])
        self.assertFalse(row.get("reference_only"))
        self.assertEqual("my-card", row["card"])
        self.assertTrue(row["path"].endswith("my-card/assets/signal-card"))

    def test_references_hidden_until_requested_and_resolve_readonly(self):
        self.assertFalse([row for row in self.rows()["assets"] if row.get("reference_only")])
        assets = self.rows(include_references=True)["assets"]
        ref = next(row for row in assets if row["origin"] == "reference")
        self.assertEqual("kit/tone", ref["component_ref"])
        self.assertEqual("my-card", ref["referenced_by"])
        self.assertFalse(ref["available"])
        self.assertFalse(ref["installable"])
        # The reference identity is the source card identity, so resolving it
        # yields the source card's own (editable) asset.
        path, acceptance = STORE.resolve_component(self.root, "kit/tone")
        self.assertTrue(path.is_relative_to(self.designs_root / "kit" / "assets" / "tone"))
        self.assertIsNone(acceptance)

    def test_broken_reference_reports_error(self):
        self.cards["my-card"]["references"] = ["kit/missing", "absent/thing"]
        result = self.rows()
        self.assertEqual(2, len(result["errors"]))
        self.assertFalse([row for row in result["assets"] if row.get("reference_only")])

    def test_filters_apply_to_card_assets(self):
        self.write_asset("kit", "poster", body="window.poster = 1;", tags=["still"])
        self.assertEqual(3, len(self.rows(kind="module")["assets"]))
        self.assertEqual(["kit/poster"], [row["component_ref"] for row in self.rows(tag="still")["assets"]])
        self.assertEqual(["kit/poster"], [row["component_ref"] for row in self.rows(query="poster")["assets"]])
        self.assertFalse(self.rows(kind="media")["assets"])
        self.assertFalse(self.rows(query="not-a-match")["assets"])

    def test_component_interface_reads_card_asset(self):
        card = STORE.component_interface(self.root, "my-card/signal-card")
        self.assertEqual("my-card/signal-card", card["component_ref"])
        self.assertEqual("card asset field contract checked; not accepted or frozen", card["check_scope"])
        self.assertEqual(str(self.designs_root / "my-card" / "assets" / "signal-card" / "asset.json"),
                         card["declaration"])

    def test_invalid_card_asset_fails_closed(self):
        directory = self.designs_root / "kit" / "assets" / "tone"
        (directory / "asset.json").write_text(json.dumps({"schema_version": 1, "id": "tone", "version": 1,
                                                          "kind": "media", "entry": "main.js"}), encoding="utf-8")
        result = self.rows()
        self.assertTrue(result["errors"])
        self.assertEqual(["my-card/signal-card"], [row["component_ref"] for row in result["assets"]])

    def test_card_asset_reference_validation(self):
        self.assertEqual(("kit", "tone"), CONTRACT.validate_card_asset_reference("kit/tone"))
        for value in ("Kit/tone", "kit", "kit/tone/extra", 5):
            with self.assertRaisesRegex(CONTRACT.COMPONENT.ComponentError, "card-id"):
                CONTRACT.validate_card_asset_reference(value)


if __name__ == "__main__":
    unittest.main()
