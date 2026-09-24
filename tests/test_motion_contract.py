from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from test_work_cli import REPO
import appearance
import asset_contract
import asset_store
import component_harness


def motion_payload():
    slots = {
        "reveal": {"effect": "short-rise", "duration": 0.4, "easing": "ease-out", "opacity_from": 0, "opacity_to": 1, "y": 16, "hide_before": True},
        "exit": {"effect": "fade-out", "duration": 0.3, "easing": "linear", "opacity_from": 1, "opacity_to": 0},
        "emphasis": {"effect": "focus-restore", "duration": 0.2, "restore_duration": 0.2, "easing": "ease-in-out", "color_token": "colors.accent", "outline_width": 3},
        "transition": {"effect": "crossfade", "duration": 0.5, "easing": "linear"},
    }
    reduced = deepcopy(slots)
    reduced["reveal"].update(y=0, duration=0)
    reduced["emphasis"].update(duration=0, restore_duration=0)
    reduced["transition"].update(effect="cut", duration=0)
    return {"capability_version": 2, "slots": slots, "reduced_motion": reduced}


class MotionContractTest(unittest.TestCase):
    def test_color_resolution_checks_both_modes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payloads = {"theme": {"tokens": {"colors": {"accent": "#ff2200"}}},
                        "background": {"renderer": "transparent", "parameters": {}}, "motion": motion_payload()}
            closure = []
            for kind, payload in payloads.items():
                (root / f"{kind}.json").write_text(json.dumps(payload))
                closure.append({"ref": kind, "kind": kind, "path": root, "metadata": {
                    "kind": kind, "contract_version": 2 if kind == "motion" else 1,
                    "entry": f"{kind}.json", "parameters": {}}})
            selections = {"theme": {"ref": "theme"}, "background": {"ref": "background"},
                          "motion": {slot: {"asset": {"ref": "motion"}, "entry": slot} for slot in appearance.SLOTS}}
            appearance._resolve_parameters(closure, selections, "16:9", [])
            for group in ("slots", "reduced_motion"):
                payload = motion_payload()
                payload[group]["emphasis"]["color_token"] = "colors.missing"
                (root / "motion.json").write_text(json.dumps(payload))
                with self.subTest(group=group), self.assertRaisesRegex(appearance.AppearanceError, "unresolved"):
                    appearance._resolve_parameters(closure, selections, "16:9", [])
            closure[-1]["metadata"]["contract_version"] = 1
            (root / "motion.json").write_text(json.dumps({"slots": {"exit": {"duration": 0.2, "easing": "linear"}}, "reduced_motion": {}}))
            selections["motion"] = {"reveal": {"asset": {"ref": "motion"}, "entry": "exit"}}
            appearance._resolve_parameters(closure, selections, "16:9", [])

    def test_versions_fields_and_ranges(self):
        metadata = {"kind": "motion", "contract_version": 2, "parameters": {}}
        payload = motion_payload()
        asset_contract.validate_declaration(payload, metadata, Path("."))
        invalid = [
            lambda p: p.update(capability_version=True),
            lambda p: p["slots"]["reveal"].update(opacity_from=-0.1),
            lambda p: p["slots"]["exit"].update(opacity_to=1),
            lambda p: p["slots"]["reveal"].update(scale=-1),
            lambda p: p["slots"]["reveal"].update(stagger=0),
            lambda p: p["slots"]["reveal"].update(hide_before=0),
            lambda p: p["slots"]["reveal"].update(easing="power2.out"),
            lambda p: p["slots"]["emphasis"].update(restore_duration=float("nan")),
            lambda p: p["slots"]["emphasis"].update(color_token="#ff0000"),
            lambda p: p["slots"]["transition"].update(effect="cut"),
            lambda p: p["reduced_motion"].pop("exit"),
            lambda p: p["reduced_motion"]["reveal"].update(y=1),
            lambda p: p["reduced_motion"]["reveal"].update(duration=0.5),
            lambda p: p["reduced_motion"]["exit"].update(duration=0.4),
            lambda p: p["reduced_motion"]["emphasis"].update(duration=1),
            lambda p: p["reduced_motion"]["transition"].update(effect="crossfade"),
        ]
        for change in invalid:
            changed = deepcopy(payload)
            change(changed)
            with self.subTest(payload=changed), self.assertRaises(component_harness.ComponentError):
                asset_contract.validate_declaration(changed, metadata, Path("."))
        for path in ("slots.reveal.effect", "slots.emphasis.color_token", "capability_version"):
            changed = {**metadata, "parameters": {path: {"type": "string", "default": "x"}}}
            with self.assertRaises(component_harness.ComponentError):
                asset_contract.validate_declaration(payload, changed, Path("."))
        with self.assertRaises(component_harness.ComponentError):
            asset_contract.validate_declaration(payload, {**metadata, "contract_version": 1}, Path("."))
        asset_contract.validate_declaration({"slots": {"reveal": {"duration": 1, "easing": "power2.out", "stagger": 0}}, "reduced_motion": {}}, {**metadata, "contract_version": 1}, Path("."))
        for kind, version in (("theme", 2), ("background", 2), ("motion", 3), ("motion", True)):
            with self.subTest(kind=kind, version=version), self.assertRaisesRegex(component_harness.ComponentError, "contract_version"):
                asset_contract._schema2(Path("."), {"kind": kind, "contract_version": version, "parameters": {}, "compatibility": {}})

    def test_real_pack_resolve_materialize_and_offline_verify(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            harness, store, project = (root / name for name in ("harness", "store", "project"))
            harness.mkdir()
            project.mkdir()
            shutil.copyfile(REPO / "windows-runtime.lock.json", harness / "windows-runtime.lock.json")
            with mock.patch.dict(os.environ, {"HYPERFRAMES_AI_ASSET_ROOT": str(store), "HYPERFRAMES_AI_ROOT": str(harness)}):
                account = {"motion": {}}
                for kind, payload in (("theme", {"tokens": {"colors": {"accent": "#ff2200"}}}), ("background", {"renderer": "transparent", "parameters": {}}), ("motion", motion_payload())):
                    source = root / kind
                    source.mkdir()
                    metadata = {"schema_version": 2, "id": f"test-{kind}", "kind": kind, "version": 1, "contract_version": 2 if kind == "motion" else 1, "parameters": {}, "compatibility": {}, "entry": "entry.json"}
                    if kind == "motion":
                        metadata["parameters"] = {"slots.reveal.duration": {"type": "number", "default": 0.4}, "slots.reveal.hide_before": {"type": "boolean", "default": True}}
                    (source / "asset.json").write_text(json.dumps(metadata))
                    (source / "entry.json").write_text(json.dumps(payload))
                    candidate = asset_store.pack_source(store, source)
                    asset_store.accept_component(store, candidate["component_ref"], candidate["package_sha256"], "Isolated Motion contract test", runtime_root=harness)
                    ref = {"ref": candidate["component_ref"], "kind": kind, "package_sha256": candidate["package_sha256"]}
                    if kind == "motion":
                        account["motion"] = {slot: {"asset": ref, "entry": slot} for slot in appearance.SLOTS}
                    else:
                        account[kind] = ref
                overrides = {"parameters": {"motion": {"reveal": {"slots.reveal.duration": 0, "slots.reveal.hide_before": False}}}}
                lock = appearance.resolve(harness, account, overrides)
                self.assertEqual((2, 2, 1), tuple(lock[key] for key in ("schema_version", "contract_version", "resolver_version")))
                self.assertEqual(0, lock["parameters"]["motion"]["reveal"]["slots.reveal.duration"])
                self.assertIs(False, lock["parameters"]["motion"]["reveal"]["slots.reveal.hide_before"])
                with self.assertRaisesRegex(appearance.AppearanceError, "selected slot"):
                    appearance.resolve(harness, account, {"motion": {"reveal": {**account["motion"]["reveal"], "entry": "exit"}}})
                with self.assertRaisesRegex(appearance.AppearanceError, "Unknown appearance parameter"):
                    appearance.resolve(harness, account, {"parameters": {"motion": {"reveal": {"slots.reveal.unknown": 1}}}})
                disabled = appearance.resolve(harness, account, {"motion": dict.fromkeys(appearance.SLOTS)})
                self.assertEqual(1, disabled["schema_version"])
                appearance.materialize(harness, project, lock)
                downgraded = {**lock, "schema_version": 1, "contract_version": 1}
                downgraded["sha256"] = appearance.digest({key: value for key, value in downgraded.items() if key != "sha256"})
                with self.assertRaisesRegex(appearance.AppearanceError, "capability"):
                    appearance.materialize(harness, project, downgraded)
                shutil.rmtree(store)
                appearance.verify(project, lock)
                (project / "appearance-lock.json").write_text(json.dumps(downgraded))
                with self.assertRaisesRegex(appearance.AppearanceError, "capability"):
                    appearance.verify(project, downgraded)


if __name__ == "__main__":
    unittest.main()
