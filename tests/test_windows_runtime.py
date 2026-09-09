import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess


spec = importlib.util.spec_from_file_location("windows_runtime", Path(__file__).resolve().parents[1] / ".studio/windows_runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
seed_spec = importlib.util.spec_from_file_location("prepare_windows_runtime", Path(__file__).resolve().parents[1] / ".studio/prepare_windows_runtime.py")
seed = importlib.util.module_from_spec(seed_spec)
seed_spec.loader.exec_module(seed)


class WindowsSessionTest(unittest.TestCase):
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

    def test_session_pins_code_config_and_review_without_writing_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "spaces \u4e2d\u6587"
            release = home / "releases/harness-2026.09.1"
            release.mkdir(parents=True)
            (release / ".release.json").write_text(json.dumps({"release": release.name, "channel": "stable"}))
            (release / "windows-runtime.lock.json").write_text('{"python":"3.14.0","versions":{"node":"22.22.2"}}')
            production = home / "production"
            review = home / "review"
            for root in (production, review):
                for name in ("active", "parked", "archive"):
                    (root / "works" / name).mkdir(parents=True)
            (review / ".runtime").mkdir()
            (review / ".runtime/review.json").write_text('{}')
            (home / "config").mkdir()
            config = home / "config/local.json"
            with patch.object(runtime.subprocess, "run", return_value=CompletedProcess([], 0, "v0.0.0", "")):
                self.assertEqual(runtime.doctor(release, runtime.environment(release, home))["work_root"], "not-configured")
            config.write_text(json.dumps({"work_root": str(production), "providers": {"asr": "external"}}))
            original = {p.name: p.read_bytes() for p in release.iterdir()}
            session_dir = runtime.start_session(release, home)
            session = runtime.read_json(session_dir / "session.json")
            env = runtime.environment(release, home, session)
            self.assertEqual(env["HYPERFRAMES_AI_WORK_ROOT"], str(production))
            self.assertEqual(env["HYPERFRAMES_AI_REVIEW"], "0")
            self.assertTrue(env["TEMP"].startswith(str(session_dir)))
            with patch.object(runtime.subprocess, "run", return_value=CompletedProcess([], 0, "v0.0.0", "")):
                diagnostic = runtime.doctor(release, env)
            self.assertEqual(diagnostic["checks"]["node"]["status"], "version-mismatch")
            self.assertEqual(diagnostic["checks"]["encoders"]["status"], "failed")
            self.assertEqual(diagnostic["checks"]["HYPERFRAMES_CLI"], "not-installed")
            self.assertIn(str(release / "work.ps1"), (session_dir / "work.ps1").read_text(encoding="utf-8-sig"))
            launcher = (session_dir / "work.cmd").read_text(encoding="ascii")
            self.assertIn('set "HYPERFRAMES_AI_SESSION=%~dp0session.json"', launcher)
            self.assertIn('"%~dp0..\\..\\releases\\harness-2026.09.1\\runtime\\python\\python.exe" -B', launcher)
            self.assertIn('\\.studio\\windows_runtime.py" %*', launcher)
            self.assertIn('exit /b %ERRORLEVEL%', launcher)
            self.assertNotIn("powershell", launcher.lower())
            self.assertNotIn("work.ps1", launcher)
            self.assertNotIn("current", launcher)
            config.write_text(json.dumps({"work_root": "later-workstore"}))
            self.assertEqual(runtime.environment(release, home, session)["HYPERFRAMES_AI_WORK_ROOT"], str(production))
            with self.assertRaisesRegex(ValueError, "differs"):
                runtime.environment(home / "another-release", home, session)
            self.assertEqual(original, {p.name: p.read_bytes() for p in release.iterdir()})
            config.write_text(json.dumps({"work_root": str(production)}))
            (release / ".release.json").write_text(json.dumps({"release": "candidate-test", "channel": "candidate"}))
            with self.assertRaisesRegex(ValueError, "require"):
                runtime.start_session(release, home)
            with self.assertRaisesRegex(ValueError, "requires"):
                runtime.start_session(release, home, production)
            review_session = runtime.start_session(release, home, review)
            review_env = runtime.environment(release, home, runtime.read_json(review_session / "session.json"))
            self.assertEqual(review_env["HYPERFRAMES_AI_REVIEW"], "1")
            self.assertEqual(review_env["HYPERFRAMES_AI_WORK_ROOT"], str(review))
            self.assertEqual(runtime.read_json(config)["work_root"], str(production))


if __name__ == "__main__":
    unittest.main()
