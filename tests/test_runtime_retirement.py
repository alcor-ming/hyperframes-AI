from __future__ import annotations

import copy
from importlib.machinery import SourceFileLoader
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / ".studio"))
import root_deploy

LOADER = SourceFileLoader("retirement_release", str(REPO / "release"))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC
RELEASE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(RELEASE)

RETIRED_SKILLS = ("podcast-quote-image", "xiaohongshu-article-copy", "native-subtitle-quote-image")
RETIRED_MODULES = ("youtube_transcript_api", "imageio_ffmpeg", "defusedxml", "requests",
                   "certifi", "charset_normalizer", "idna", "urllib3")
SITE_PACKAGES = "runtime/python/Lib/site-packages/"


class RuntimeRetirementTests(unittest.TestCase):
    def test_retired_skills_templates_and_dependencies_are_absent(self):
        skills = json.loads((REPO / "skills-lock.json").read_text())["skills"]
        for name in RETIRED_SKILLS:
            self.assertFalse((REPO / ".agents/skills" / name).exists(), name)
            self.assertNotIn(name, skills)
            self.assertNotIn(name, RELEASE.LOCAL_SKILLS)
        self.assertFalse(list((REPO / ".studio/templates").glob("PODCAST_QUOTE*")))
        lock = json.loads((REPO / "windows-runtime.lock.json").read_text())
        wheels = {asset["file"].split("-", 1)[0] for asset in lock["assets"] if asset["kind"] == "wheel"}
        self.assertFalse(wheels.intersection(RETIRED_MODULES))
        self.assertIn("pillow", wheels)
        self.assertIn("runtime/ffmpeg/bin/ffmpeg.exe", lock["required_files"])
        self.assertIn("runtime/ffmpeg/bin/ffprobe.exe", lock["required_files"])

    def test_runtime_lock_change_rebuilds_and_upgrade_rollback_keep_one_closure(self):
        """Use the real staging/deployment path with tiny, never executed archives."""
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            lock = json.loads((REPO / "windows-runtime.lock.json").read_text())
            old_lock = copy.deepcopy(lock)
            old_lock["assets"].extend({"kind": "wheel", "file": f"{name}-fixture.whl"}
                                      for name in RETIRED_MODULES)

            def package(name, definition):
                package_root, cache = base / name, base / (name + "-cache")
                package_root.mkdir()
                cache.mkdir()
                definition = copy.deepcopy(definition)
                for asset in definition["assets"]:
                    archive = cache / asset["file"]
                    if asset["kind"] == "python":
                        members = {"python.exe": b"fixture Python, never executed",
                                   "python314._pth": b"python314.zip\n.\n#import site\n"}
                    elif asset["kind"] == "wheel":
                        module = asset["file"].split("-", 1)[0]
                        module = "PIL" if module == "pillow" else module
                        members = {f"{module}/__init__.py": module.encode()}
                    else:
                        target = asset["target"] + "/"
                        members = {item[len(target):]: b"fixture native file, never executed"
                                   for item in definition["required_files"] if item.startswith(target)}
                    prefix = asset.get("strip_prefix", "")
                    with zipfile.ZipFile(archive, "w") as bundle:
                        for member, content in members.items():
                            bundle.writestr(f"{prefix}/{member}" if prefix else member, content)
                    asset["sha256"] = RELEASE.sha256(archive)
                (package_root / "windows-runtime.lock.json").write_text(json.dumps(definition))
                staged = RELEASE.stage_runtime(package_root, cache)
                self.assertEqual({asset["file"] for asset in definition["assets"]}, set(staged))
                (package_root / "work.cmd").write_text(name)
                files = {path.relative_to(package_root).as_posix(): RELEASE.sha256(path)
                         for path in package_root.rglob("*") if path.is_file()}
                root_deploy.write_json(package_root / ".release.json", {
                    "release": "candidate-" + name, "channel": "candidate", "target": "windows-x64",
                    "layout": "root-v1", "package_kind": "full", "files": files,
                })
                return package_root

            old_package, new_package = package("old", old_lock), package("new", lock)
            retired = {SITE_PACKAGES + name + "/__init__.py" for name in RETIRED_MODULES}
            shared = SITE_PACKAGES + "PIL/__init__.py"
            new_files = root_deploy.verify_package(new_package)["files"]
            self.assertFalse(retired.intersection(new_files))
            self.assertIn(shared, new_files)
            archive = base / "candidate.zip"
            RELEASE.write_zip(new_package, archive, "candidate-new", 1)
            with zipfile.ZipFile(archive) as bundle:
                packaged = {name.removeprefix("candidate-new/") for name in bundle.namelist()}
            self.assertFalse(retired.intersection(packaged))
            self.assertIn(shared, packaged)

            root = base / "root"
            for name in ("works/active", "works/parked", "works/archive",
                         "asset-library/store", "asset-library/sources/demo"):
                (root / name).mkdir(parents=True)
            config = base / "config.json"
            config.write_text(json.dumps({
                "work_root": str(root), "asset_root": str(root / "asset-library/store"),
                "asset_review_root": str(root / "asset-library"),
                "asset_source_roots": [str(root / "asset-library/sources/demo")],
                "review": True, "review_protected_roots": [str(base / "production-never-used")],
            }))
            old_state = root_deploy.deploy(old_package, root, config)
            self.assertTrue(retired.issubset(old_state["files"]))
            self.assertIsNotNone(RELEASE.reusable_runtime(root, old_package / "windows-runtime.lock.json"))
            self.assertIsNone(RELEASE.reusable_runtime(root, new_package / "windows-runtime.lock.json"))
            state = root_deploy.deploy(new_package, root, None)
            self.assertFalse(retired.intersection(state["files"]))
            self.assertTrue(all(not (root / path).exists() for path in retired))
            self.assertEqual(RELEASE.sha256(root / shared), old_state["files"][shared])
            self.assertIsNotNone(RELEASE.reusable_runtime(root, new_package / "windows-runtime.lock.json"))
            root_deploy.recover(root, rollback=True)
            restored = root_deploy.verify_root(root)
            self.assertEqual(old_state["files"], restored["files"])
            self.assertTrue(all((root / path).is_file() for path in retired))


if __name__ == "__main__":
    unittest.main()
