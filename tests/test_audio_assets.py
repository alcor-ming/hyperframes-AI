import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / ".studio"))
import asset_contract
import asset_store
import component_harness


class AudioAssetTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.store = self.root / "store"
        self.harness = self.root / "harness"
        self.harness.mkdir()
        self.metadata = {"schema_version": 1, "id": "test-sound", "version": 1,
                         "kind": "media", "entry": "sound.mp3", "license": "LICENSE",
                         "source_url": "https://example.invalid/synthetic", "collection_id": "fixture"}
        (self.source / "asset.json").write_text(json.dumps(self.metadata))
        (self.source / "LICENSE").write_text("Synthetic fixture, no external source")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                        "sine=frequency=440:duration=0.1", "-c:a", "libmp3lame", str(self.source / "sound.mp3")], check=True)
        env = patch.dict(os.environ, {"HYPERFRAMES_AI_ASSET_ROOT": str(self.store),
                         "HYPERFRAMES_AI_ASSET_CONFIG": str(self.root / "config.json"), "HYPERFRAMES_AI_REVIEW": "0"})
        env.start()
        self.addCleanup(env.stop)

    def test_pack_accept_install_verify_preserves_bytes_and_metadata(self):
        original = (self.source / "sound.mp3").read_bytes()
        candidate = asset_store.pack_source(self.store, self.source)
        ref, digest = candidate["component_ref"], candidate["package_sha256"]
        acceptance = asset_store.accept_component(self.store, ref, digest, "Synthetic test", runtime_root=self.harness)
        package, _ = asset_store.resolve_component(self.harness, ref)
        report = asset_contract.validate_asset(package)
        self.assertEqual("audio", report["metadata"]["media_type"])
        self.assertEqual("mp3", report["metadata"]["audio"]["codec"])
        self.assertGreater(report["metadata"]["audio"]["sample_rate"], 0)
        project = self.root / "project"
        project.mkdir()
        (project / "index.html").write_text('<div data-scene-id="S01"><audio src="vendor/components/test-sound/v1/sound.mp3"></audio></div>')
        binding = {"schema_version": 3, "component_ref": ref, "scene": "S01",
                   "usage": {"role": "auxiliary", "required": True}}
        component_harness.install_component(package, project, binding, acceptance=acceptance)
        component_harness.verify_installation(project)
        self.assertEqual(original, (project / "vendor/components/test-sound/v1/sound.mp3").read_bytes())
        self.assertEqual(original, (self.source / "sound.mp3").read_bytes())
        self.assertEqual(self.metadata, json.loads((package / "asset.json").read_text()))
        (project / "vendor/components/test-sound/v1/sound.mp3").write_bytes(b"damaged")
        with self.assertRaises(component_harness.ComponentError):
            component_harness.verify_installation(project)

    def test_invalid_disguised_missing_and_unavailable_decoder_fail(self):
        path = self.source / "sound.mp3"
        original = path.read_bytes()
        path.write_bytes(b"not audio")
        with self.assertRaisesRegex(component_harness.ComponentError, "MP3"):
            asset_store.pack_source(self.store, self.source)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "sine=duration=0.1", "-f", "wav", str(path)], check=True)
        with self.assertRaisesRegex(component_harness.ComponentError, "MP3"):
            asset_store.pack_source(self.store, self.source)
        path.write_bytes(original)
        with patch.dict(os.environ, {"HYPERFRAMES_FFMPEG_PATH": str(self.root / "missing-ffmpeg")}):
            with self.assertRaisesRegex(component_harness.ComponentError, "ffprobe/ffmpeg required"):
                asset_store.pack_source(self.store, self.source)
        path.unlink()
        with self.assertRaises(component_harness.ComponentError):
            asset_store.pack_source(self.store, self.source)

    def test_acceptance_failure_is_not_available_and_explicit_retry_recovers(self):
        candidate = asset_store.pack_source(self.store, self.source)
        atomic = asset_store._atomic_json

        def fail_acceptance(path, value):
            if Path(path).name == "acceptance.json":
                raise OSError("injected acceptance write failure")
            return atomic(path, value)

        with patch.object(asset_store, "_atomic_json", side_effect=fail_acceptance):
            with self.assertRaisesRegex(OSError, "injected"):
                asset_store.accept_component(self.store, candidate["component_ref"], candidate["package_sha256"],
                                             "Synthetic test", runtime_root=self.harness)
        assets = asset_store.discover_components(self.harness)["assets"]
        self.assertFalse(any(row["available"] for row in assets))
        asset_store.accept_component(self.store, candidate["component_ref"], candidate["package_sha256"],
                                     "Explicit retry", runtime_root=self.harness)
        package, _ = asset_store.resolve_component(self.harness, candidate["component_ref"])
        self.assertEqual(candidate["package_sha256"], asset_contract.validate_asset(package)["package_sha256"])


if __name__ == "__main__":
    unittest.main()
