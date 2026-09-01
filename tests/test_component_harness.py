from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPONENT = load_module("component_harness", REPO / ".studio" / "component_harness.py")
WORK = load_module("work_cli_for_component_tests", REPO / ".studio" / "work.py")


class ComponentHarnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.public = REPO / ".studio" / "components" / "chapter-intro" / "v1"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def binding(scene: str = "S02", title: str = "选题雷达", offset: float = 5.32) -> dict:
        return {
            "schema_version": 1,
            "component_ref": "chapter-intro@v1",
            "scene": scene,
            "slots": {
                "chapter_index": "01",
                "chapter_total": 10,
                "title": title,
                "summary": "热点先筛选，再成为选题池",
                "progress": 0.1,
            },
            "placement": {"width": 1440, "height": 1080},
            "timing": {"offset": offset, "time_scale": 1, "hero_hold": 0, "handoff_hold": 0},
            "surfaces": {
                "evidence_primary": {
                    "kind": "active_media_card",
                    "mode": "none",
                    "fallback": "programmatic",
                }
            },
            "assets": {},
        }

    def test_package_hash_ignores_enumeration_order(self) -> None:
        first = self.root / "first"
        second = self.root / "second"
        for directory in (first, second):
            (directory / "nested").mkdir(parents=True)
        (first / "z.txt").write_bytes(b"z")
        (first / "nested" / "a.txt").write_bytes(b"a")
        (second / "nested" / "a.txt").write_bytes(b"a")
        (second / "z.txt").write_bytes(b"z")
        self.assertEqual(COMPONENT.package_sha256(first), COMPONENT.package_sha256(second))
        self.assertEqual("nested/a.txt", COMPONENT.package_entries(first)[0]["path"])

    def test_gap_first_selection_release_validates(self) -> None:
        release = COMPONENT.validate_component_release(
            REPO / ".studio" / "components" / "gap-first-selection" / "v1"
        )
        self.assertEqual("gap-first-selection@v1", release["component_ref"])

    def test_install_hash_lock_and_tamper_fail_closed(self) -> None:
        project = self.root / "project"
        project.mkdir()
        result = COMPONENT.install_component(self.public, project, self.binding())
        self.assertEqual(
            COMPONENT.component_package_sha256(self.public),
            COMPONENT.component_package_sha256(project / "vendor" / "components" / "chapter-intro" / "v1"),
        )
        self.assertTrue((project / "COMPONENT_LOCK.json").is_file())
        self.assertEqual("chapter-intro@v1", result["component"]["component_ref"])
        COMPONENT.verify_installation(project)

        vendor_html = project / "vendor" / "components" / "chapter-intro" / "v1" / "component.html"
        vendor_html.write_bytes(vendor_html.read_bytes() + b"\n")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)

    def test_binding_tamper_fails_lock_validation(self) -> None:
        project = self.root / "project"
        project.mkdir()
        COMPONENT.install_component(self.public, project, self.binding())
        binding_path = project / "component-bindings" / "S02.chapter-intro.json"
        binding_path.write_text(binding_path.read_text(encoding="utf-8").replace("选题雷达", "别的内容"), encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)

    def test_binding_contract_rejects_bad_placement_timing_scale_and_assets(self) -> None:
        release = COMPONENT.validate_component_release(self.public)
        invalid_cases = []
        invalid = copy.deepcopy(self.binding())
        invalid["placement"]["width"] = 0
        invalid_cases.append(invalid)
        invalid = copy.deepcopy(self.binding())
        del invalid["timing"]["offset"]
        invalid_cases.append(invalid)
        invalid = copy.deepcopy(self.binding())
        invalid["timing"]["time_scale"] = 2
        invalid_cases.append(invalid)
        for asset_path in ("/absolute/image.png", "../outside.png", "https://example.test/image.png"):
            invalid = copy.deepcopy(self.binding())
            invalid["assets"] = {"image": asset_path}
            invalid_cases.append(invalid)
        invalid = copy.deepcopy(self.binding())
        invalid["assets"] = []
        invalid_cases.append(invalid)
        for binding in invalid_cases:
            with self.assertRaises(COMPONENT.ComponentError):
                COMPONENT.validate_binding(binding, release)

    def test_requested_ref_must_match_source_and_lock_schema_is_strict(self) -> None:
        project = self.root / "project"
        project.mkdir()
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.install_component(self.public, project, self.binding(), expected_ref="chapter-intro@v2")
        COMPONENT.install_component(self.public, project, self.binding())
        lock_path = project / "COMPONENT_LOCK.json"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["schema_version"] = 2
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)
        lock["schema_version"] = 1
        lock["algorithm"] = "wrong"
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)

    def test_animation_plan_component_ref_check_reads_body_and_matches_exact_ref(self) -> None:
        plan = self.root / "ANIMATION_PLAN.md"
        plan.write_text(
            '---\n{"status":"approved","component_ref":"chapter-intro@v1"}\n---\n\n## Components\n- `chapter-intro@v10`\n',
            encoding="utf-8",
        )
        self.assertFalse(WORK.animation_plan_contains_component_ref(plan, "chapter-intro@v1"))
        plan.write_text(plan.read_text(encoding="utf-8") + "- `chapter-intro@v1`\n", encoding="utf-8")
        self.assertTrue(WORK.animation_plan_contains_component_ref(plan, "chapter-intro@v1"))

    def test_lock_rejects_duplicate_refs_and_release_time_scale_drift(self) -> None:
        project = self.root / "project"
        project.mkdir()
        COMPONENT.install_component(self.public, project, self.binding())
        lock_path = project / "COMPONENT_LOCK.json"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["components"].append(copy.deepcopy(lock["components"][0]))
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)

        release = self.root / "release"
        shutil.copytree(self.public, release)
        metadata_path = release / "COMPONENT.md"
        lines = metadata_path.read_text(encoding="utf-8").splitlines()
        end = lines.index("---", 1)
        metadata = json.loads("\n".join(lines[1:end]))
        metadata["motion_recipe"]["allowed_time_scale"]["max"] = 2
        metadata_path.write_text(
            "---\n" + json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n---\n" + "\n".join(lines[end + 1 :]) + "\n",
            encoding="utf-8",
        )
        COMPONENT.write_hashes(release)
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_component_release(release)

    def test_same_release_supports_multiple_sorted_bindings_and_is_idempotent(self) -> None:
        project = self.root / "project"
        project.mkdir()
        COMPONENT.install_component(self.public, project, self.binding())
        COMPONENT.install_component(self.public, project, self.binding("S03", "结构拆解", 12.76))
        lock = json.loads((project / "COMPONENT_LOCK.json").read_text(encoding="utf-8"))
        bindings = lock["components"][0]["bindings"]
        self.assertEqual(
            ["component-bindings/S02.chapter-intro.json", "component-bindings/S03.chapter-intro.json"],
            [item["path"] for item in bindings],
        )
        COMPONENT.install_component(self.public, project, self.binding("S03", "结构拆解", 12.76))
        lock_after = json.loads((project / "COMPONENT_LOCK.json").read_text(encoding="utf-8"))
        self.assertEqual(bindings, lock_after["components"][0]["bindings"])
        report = COMPONENT.verify_installation(project)
        self.assertEqual(2, len(report["components"][0]["bindings"]))
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.install_component(self.public, project, self.binding("S02", "冲突内容"))

    def test_direct_mount_must_match_binding_and_release(self) -> None:
        project = self.root / "project"
        project.mkdir()
        binding = self.binding()
        COMPONENT.install_component(self.public, project, binding)
        values = {
            **binding["slots"],
            "time_scale": 1,
            "evidence_primary_mode": "none",
        }
        mount = (
            '<div data-component-ref="chapter-intro@v1" '
            'data-component-binding="component-bindings/S02.chapter-intro.json" '
            'data-composition-id="chapter-intro" '
            'data-composition-src="vendor/components/chapter-intro/v1/component.html" '
            f"data-variable-values='{json.dumps(values, ensure_ascii=False, separators=(',', ':'))}' "
            'data-start="5.32" data-width="1440" data-height="1080"></div>'
        )
        (project / "index.html").write_text(mount, encoding="utf-8")
        self.assertEqual(
            ["component-bindings/S02.chapter-intro.json"],
            COMPONENT.verify_installation(project)["components"][0]["mounts"],
        )
        (project / "index.html").write_text(mount.replace('data-composition-id="chapter-intro"', 'data-composition-id="chapter-intro-01"'), encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)

    def test_work_surface_inventory_checks_dom_and_local_payload(self) -> None:
        project = self.root / "project"
        (project / "compositions").mkdir(parents=True)
        (project / "assets").mkdir()
        (project / "assets" / "icon.svg").write_text('<svg viewBox="0 0 1 1"/>', encoding="utf-8")
        (project / "index.html").write_text(
            '<div id="s01-p001" data-composition-src="compositions/p001.html"></div>', encoding="utf-8"
        )
        (project / "compositions" / "p001.html").write_text(
            '<img data-visual-surface="s01.icon_node.01" data-surface-kind="icon_node" '
            'data-surface-modes="none,icon" data-surface-fallback="none">',
            encoding="utf-8",
        )
        inventory = {
            "scenes": {
                "S01": {
                    "prototype": "P001",
                    "surfaces": [
                        {
                            "surface_id": "s01.icon_node.01",
                            "kind": "icon_node",
                            "selector": "img",
                            "modes": ["none", "icon"],
                            "mode": "icon",
                            "fallback": "none",
                            "path": "assets/icon.svg",
                        }
                    ],
                }
            }
        }
        (project / "scene-slots.json").write_text(json.dumps(inventory), encoding="utf-8")
        self.assertEqual(1, len(COMPONENT.validate_work_surface_inventory(project)["surfaces"]))
        inventory["scenes"]["S01"]["surfaces"][0]["path"] = "https://invalid.test/icon.svg"
        (project / "scene-slots.json").write_text(json.dumps(inventory), encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_work_surface_inventory(project)

    def test_surface_payload_modes_probe_hash_and_tamper(self) -> None:
        project = self.root / "project"
        project.mkdir()
        assets = project / "assets"
        assets.mkdir()
        (assets / "evidence-fallback.svg").write_text('<svg viewBox="0 0 16 16"/>', encoding="utf-8")
        shutil.copy2(self.public / "assets" / "fallback.mp4", assets / "evidence-fallback.mp4")
        release = COMPONENT.validate_component_release(self.public)
        for mode, name in (("image", "evidence-fallback.svg"), ("video", "evidence-fallback.mp4")):
            binding = self.binding(scene=f"S{mode}")
            binding["surfaces"]["evidence_primary"] = {
                "kind": "active_media_card",
                "mode": mode,
                "path": f"assets/{name}",
            }
            records = COMPONENT.validate_surface_payloads(project, binding, release)
            self.assertEqual(mode, records["evidence_primary"]["mode"])
            self.assertRegex(records["evidence_primary"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(records["evidence_primary"]["probe_sha256"], r"^[0-9a-f]{64}$")
        invalid = self.binding()
        invalid["surfaces"]["evidence_primary"] = {
            "kind": "active_media_card", "mode": "image", "path": "https://invalid.test/a.png"
        }
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_binding(invalid, release)
        missing = self.binding()
        missing["surfaces"]["evidence_primary"] = {
            "kind": "active_media_card", "mode": "image", "path": "assets/missing.png"
        }
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_surface_payloads(project, missing, release)
        image_binding = self.binding(scene="Simage")
        image_binding["surfaces"]["evidence_primary"] = {
            "kind": "active_media_card", "mode": "image", "path": "assets/evidence-fallback.svg"
        }
        COMPONENT.install_component(self.public, project, image_binding)
        tampered = assets / "evidence-fallback.svg"
        tampered.write_text(tampered.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.verify_installation(project)

    def test_surface_dom_and_snapshot_closure_fail_closed(self) -> None:
        release = COMPONENT.validate_component_release(self.public)
        dom_report = COMPONENT.validate_surface_dom(self.public / "component.html", release["surface_specs"])
        self.assertEqual(["evidence_primary"], dom_report["surfaces"])
        broken = self.root / "broken.html"
        broken.write_text('<div data-visual-surface="evidence_primary" data-surface-kind="icon_node"></div>', encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_surface_dom(broken, release["surface_specs"])

        source = self.root / "source"
        snapshot = self.root / "snapshot"
        source.mkdir()
        (source / "compositions").mkdir()
        (source / "compositions" / "main.html").write_text("main", encoding="utf-8")
        (source / "assets").mkdir()
        (source / "assets" / "evidence.svg").write_text("<svg/>", encoding="utf-8")
        for name in ("index.html", "DESIGN.md", "project-config.json", "scene-slots.json"):
            (source / name).write_text(name, encoding="utf-8")
        WORK.copy_snapshot(source, snapshot)
        self.assertTrue(COMPONENT.validate_snapshot_closure(source, snapshot)["closed"])
        (snapshot / "scene-slots.json").write_text("tampered", encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_snapshot_closure(source, snapshot)
        asset_snapshot = self.root / "snapshot-assets"
        WORK.copy_snapshot(source, asset_snapshot)
        (asset_snapshot / "assets" / "evidence.svg").write_text("<svg><!-- tampered --></svg>", encoding="utf-8")
        with self.assertRaises(COMPONENT.ComponentError):
            COMPONENT.validate_snapshot_closure(source, asset_snapshot)

    def test_snapshot_copies_optional_component_inputs_without_changing_legacy(self) -> None:
        project = self.root / "project"
        project.mkdir()
        for name in WORK.SNAPSHOT_ITEMS:
            target = project / name
            if name == "compositions":
                target.mkdir(parents=True)
                (target / "main.html").write_text("main", encoding="utf-8")
            elif name.endswith(".json"):
                target.write_text("{}\n", encoding="utf-8")
            else:
                target.write_text(name, encoding="utf-8")
        self.assertEqual(WORK.SNAPSHOT_ITEMS, WORK.snapshot_items(project))
        legacy_snapshot = self.root / "legacy-snapshot"
        WORK.copy_snapshot(project, legacy_snapshot)
        self.assertFalse((legacy_snapshot / "vendor").exists())

        (project / "vendor" / "components").mkdir(parents=True)
        (project / "vendor" / "components" / "marker.txt").write_text("vendor", encoding="utf-8")
        (project / "component-bindings").mkdir()
        (project / "component-bindings" / "S01.json").write_text("{}\n", encoding="utf-8")
        (project / "COMPONENT_LOCK.json").write_text("{}\n", encoding="utf-8")
        self.assertIn("vendor", WORK.snapshot_items(project))
        snapshot = self.root / "component-snapshot"
        WORK.copy_snapshot(project, snapshot)
        self.assertEqual("vendor", (snapshot / "vendor" / "components" / "marker.txt").read_text())
        self.assertTrue((snapshot / "component-bindings" / "S01.json").is_file())
        self.assertTrue((snapshot / "COMPONENT_LOCK.json").is_file())


if __name__ == "__main__":
    unittest.main()
