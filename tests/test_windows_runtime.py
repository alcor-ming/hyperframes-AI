import importlib.util
import json
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
spec = importlib.util.spec_from_file_location("windows_runtime", Path(__file__).resolve().parents[1] / ".studio/windows_runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
seed_spec = importlib.util.spec_from_file_location("prepare_windows_runtime", Path(__file__).resolve().parents[1] / ".studio/prepare_windows_runtime.py")
seed = importlib.util.module_from_spec(seed_spec)
seed_spec.loader.exec_module(seed)


class WindowsRootTest(unittest.TestCase):
    def make_root(self, base, *, review=False):
        root = base / "root"
        (root / ".studio/.runtime").mkdir(parents=True)
        (root / ".release.json").write_text(json.dumps({"release": "candidate-test" if review else "local-test",
                                                       "channel": "candidate" if review else "local"}))
        (root / "windows-runtime.lock.json").write_text("{}")
        for name in ("active", "parked", "archive"):
            (root / "works" / name).mkdir(parents=True)
        for name in ("store", "sources"):
            (root / "asset-library" / name).mkdir(parents=True)
        config = {"work_root": str(root), "asset_root": str(root / "asset-library/store"),
                  "asset_source_roots": [str(root / "asset-library/sources")], "review": review}
        if review:
            config.update(asset_review_root=str(root / "asset-library"),
                          review_protected_roots=[str(base / "production")])
            (root / ".runtime").mkdir()
            (root / ".runtime/review.json").write_text(json.dumps({"mode": "review", "review_id": root.name}))
        path = root / ".studio/.runtime/local.json"
        path.write_text(json.dumps(config))
        return root, config, path

    def test_physical_root_ignores_inherited_identity_and_freezes_config(self):
        import asset_store
        with tempfile.TemporaryDirectory() as temporary:
            root, config, path = self.make_root(Path(temporary))
            pollution = {key: "missing.json" for key in ("HYPERFRAMES_AI_SESSION", "HYPERFRAMES_AI_ROOT",
                         "HYPERFRAMES_AI_HOME", "HYPERFRAMES_AI_ASSET_CONFIG", "HYPERFRAMES_AI_ASSET_ROOT")}
            with patch.dict(os.environ, pollution):
                env = runtime.environment(root)
            self.assertNotIn("HYPERFRAMES_AI_SESSION", env)
            self.assertEqual(env["HYPERFRAMES_AI_ROOT"], str(root))
            self.assertEqual(env["HYPERFRAMES_AI_CONFIG"], str(path))
            self.assertEqual(env["HYPERFRAMES_AI_ASSET_ROOT"], config["asset_root"])
            path.write_text(json.dumps({**config, "asset_source_roots": []}))
            with patch.dict(os.environ, env, clear=True):
                self.assertEqual(asset_store._configured_sources(root, Path(config["asset_root"])),
                                 config["asset_source_roots"])
                project = Path(config["asset_source_roots"][0]) / "sample"
                project.mkdir()
                self.assertEqual(asset_store.authoring_project(root, project), project)
            with patch.object(runtime, "__file__", str(root / ".studio/windows_runtime.py")), \
                 patch.dict(os.environ, pollution), patch.object(runtime.subprocess, "call", return_value=0) as call:
                self.assertEqual(runtime.main(["list"]), 0)
                self.assertEqual(call.call_args.kwargs["env"]["HYPERFRAMES_AI_ROOT"], str(root))
            self.assertFalse((root / "sessions").exists())
            self.assertFalse((root / ".harness").exists())

    def test_review_rejects_production_sources_and_accepts_independent_identity(self):
        import work_requests
        with tempfile.TemporaryDirectory() as temporary:
            root, config, path = self.make_root(Path(temporary), review=True)
            env = runtime.environment(root)
            with patch.dict(os.environ, env, clear=True):
                self.assertEqual(work_requests.review_identity(root)["review_id"], root.name)
            config["asset_source_roots"] = [str(Path(temporary) / "production/sources")]
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "Review"):
                runtime.environment(root)
            config["review"] = False
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "Candidate"):
                runtime.environment(root)

    def test_pending_update_and_running_command_block_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, _, _ = self.make_root(Path(temporary))
            with runtime.command_lock(root):
                with self.assertRaisesRegex(ValueError, "busy"):
                    with runtime.command_lock(root):
                        self.fail("Second writer acquired the root")
            (root / ".studio/.runtime/deploy-pending.json").write_text("{}")
            with patch.object(runtime, "__file__", str(root / ".studio/windows_runtime.py")):
                with self.assertRaisesRegex(ValueError, "incomplete"):
                    runtime.main(["list"])

    @unittest.skipUnless(os.name == "nt", "Native Windows CMD")
    def test_no_argument_cmd_explains_its_purpose(self):
        result = runtime.subprocess.run([os.environ["COMSPEC"], "/d", "/c",
                                         str(Path(__file__).resolve().parents[1] / "work.cmd")],
                                        input="\n", capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Codex App", result.stdout)

    def test_launcher_loads_siblings_under_isolated_python(self):
        code = ("import importlib.util,sys; "
                "s=importlib.util.spec_from_file_location('launcher',sys.argv[1]); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "from work_requests import review_identity")
        result = runtime.subprocess.run([sys.executable, "-I", "-S", "-c", code, str(spec.origin)],
                                        capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_seed_checks_locked_registry_and_cached_bytes_without_network(self):
        lock = seed.read(Path(__file__).resolve().parents[1] / "windows-npm.lock.json")
        seed.validate_npm_lock(lock)
        lock["packages"]["node_modules/gsap"]["resolved"] = "https://untrusted.invalid/package.tgz"
        with self.assertRaisesRegex(ValueError, "registry URL"):
            seed.validate_npm_lock(lock)
        with tempfile.TemporaryDirectory() as temporary:
            asset = Path(temporary) / "asset.zip"
            asset.write_bytes(b"locked")
            expected = seed.digest(asset)
            self.assertEqual(seed.download("", asset, expected), expected)
            asset.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                seed.download("", asset, expected)



if __name__ == "__main__":
    unittest.main()
