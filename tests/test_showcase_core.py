from copy import deepcopy
import json
import unittest
from unittest import mock

import test_appearance_resolver
import appearance
import visual_diagnostics


class ShowcaseCoreTest(unittest.TestCase):
    setUp = test_appearance_resolver.AppearanceResolverTest.setUp
    ref = test_appearance_resolver.AppearanceResolverTest.ref

    def test_submodule_is_explicit_frozen_and_hashed(self):
        for submodule in appearance.SHOWCASE_SUBMODULES:
            lock = appearance.resolve(self.root, self.account, {"mode": "showcase", "submodule": submodule})
            appearance._check_lock(lock)
            self.assertEqual(lock["submodule"], submodule)
            self.assertFalse(lock["selection"]["captions"])
            damaged = deepcopy(lock)
            damaged["submodule"] = "science" if submodule == "pdoom" else "pdoom"
            with self.assertRaisesRegex(appearance.AppearanceError, "hash mismatch"):
                appearance._check_lock(damaged)
        for change in ({}, {"submodule": None}, {"submodule": "unknown"},
                       {"submodule": "pdoom", "ratio": "4:3"}):
            with self.subTest(change=change), self.assertRaises(appearance.AppearanceError):
                appearance.resolve(self.root, self.account, {"mode": "showcase", **change})
        for asset in self.assets:
            asset["metadata"]["compatibility"]["ratios"].append("9:16")
        lock = appearance.resolve(self.root, self.account, {"mode": "showcase", "submodule": "science", "ratio": "9:16"})
        appearance._check_lock(lock)
        account = {**self.account, "mode": "showcase", "submodule": "pdoom"}
        with self.assertRaisesRegex(appearance.AppearanceError, "explicit submodule"):
            appearance.resolve(self.root, account)

    def test_old_locks_unchanged_and_submodule_strict(self):
        for mode in ("card", "explainer"):
            lock = appearance.resolve(self.root, self.account, {"mode": mode})
            self.assertNotIn("submodule", lock)
            before = json.dumps(lock)
            appearance._check_lock(lock)
            self.assertEqual(json.dumps(lock), before)
            with self.assertRaises(appearance.AppearanceError):
                appearance.resolve(self.root, self.account, {"mode": mode, "submodule": "pdoom"})
            lock["submodule"] = "pdoom"
            lock["sha256"] = appearance.digest({key: value for key, value in lock.items() if key != "sha256"})
            with self.assertRaises(appearance.AppearanceError):
                appearance._check_lock(lock)
        lock = appearance.resolve(self.root, self.account, {"mode": "showcase", "submodule": "pdoom"})
        for value in (None, "unknown", {}, []):
            damaged = {**lock, "submodule": value}
            damaged["sha256"] = appearance.digest({key: value for key, value in damaged.items() if key != "sha256"})
            with self.assertRaises(appearance.AppearanceError):
                appearance._check_lock(damaged)

    def test_showcase_binds_no_appearance_unless_explicit(self):
        lock = appearance.resolve(self.root, self.account, {"mode": "showcase", "submodule": "pdoom"})
        appearance._check_lock(lock)
        self.assertEqual((lock["selection"]["theme"], lock["selection"]["background"]), (None, None))
        self.assertEqual(set(lock["selection"]["motion"].values()), {None})
        self.assertEqual(lock["overrides"]["account"], {})
        self.assertEqual(lock["account"]["sha256"], appearance.digest(self.account))
        with mock.patch("asset_store.resolve_asset_closure", return_value=[]) as closure:
            free = appearance.resolve(self.root, {}, {"mode": "showcase", "submodule": "science"})
        closure.assert_called_once_with(self.root, [])
        appearance._check_lock(free)
        chosen = appearance.resolve(self.root, self.account, {"mode": "showcase", "submodule": "pdoom",
                                                              "theme": self.ref("theme"), "parameters": {"theme": {"tokens.surface.amount": 3}}})
        appearance._check_lock(chosen)
        self.assertEqual(chosen["selection"]["theme"], self.ref("theme"))
        self.assertIsNone(chosen["selection"]["background"])
        self.assertEqual(chosen["parameters"]["theme"]["tokens.surface.amount"], 3)
        with self.assertRaisesRegex(appearance.AppearanceError, "unselected"):
            appearance.resolve(self.root, {}, {"mode": "showcase", "submodule": "pdoom",
                                               "parameters": {"background": {"color": "#000"}}})
        for mode in ("card", "explainer"):
            with self.subTest(mode=mode), self.assertRaises(appearance.AppearanceError):
                appearance.resolve(self.root, self.account, {"mode": mode, "theme": None})
        damaged = {**lock, "mode": "explainer"}
        damaged.pop("submodule")
        damaged["sha256"] = appearance.digest({key: value for key, value in damaged.items() if key != "sha256"})
        with self.assertRaises(appearance.AppearanceError):
            appearance._check_lock(damaged)

    def test_showcase_skips_layers_but_keeps_asset_closure(self):
        (self.root / "index.html").write_text('<main data-composition-id="root"></main>', encoding="utf-8")
        (self.root / "scene.html").write_text('<div data-composition-id="scene"></div>', encoding="utf-8")
        dependencies = ["index.html", "scene.html"]
        with mock.patch("explainer.installed_assets", return_value={}):
            report = visual_diagnostics.explainer_diagnostics(self.root, dependencies, {"mode": "showcase"})
            self.assertEqual(report["findings"], [])
            report = visual_diagnostics.explainer_diagnostics(self.root, dependencies, {"mode": "card"})
            self.assertTrue(any(item["kind"] == "explainer_layer_missing" for item in report["findings"]))
            (self.root / "scene.html").write_text('<div data-character-ref="missing@v1"></div><audio src="https://cdn.example/sound.mp3"></audio>', encoding="utf-8")
            report = visual_diagnostics.explainer_diagnostics(self.root, dependencies, {"mode": "showcase"})
            self.assertEqual({item["kind"] for item in report["findings"]},
                             {"character_asset_outside_closure", "sound_asset_outside_closure"})
        with mock.patch("explainer.installed_assets", side_effect=ValueError("broken lock")):
            report = visual_diagnostics.explainer_diagnostics(self.root, dependencies, {"mode": "showcase"})
            self.assertIn("asset_closure_invalid", {item["reason"] for item in report["unverified"]})


if __name__ == "__main__":
    unittest.main()
