from __future__ import annotations

from importlib.machinery import SourceFileLoader
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import unittest
import zipfile
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
LOADER = SourceFileLoader("release_cli", str(REPO / "release"))
SPEC = importlib.util.spec_from_loader("release_cli", LOADER)
assert SPEC
RELEASE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(RELEASE)


class ReleaseCliTest(unittest.TestCase):
    def test_windows_zip_is_deterministic_and_checksum_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "file.txt").write_text("fixed\n", encoding="utf-8")
            first = root / "first.zip"
            second = root / "second.zip"
            RELEASE.write_zip(source, first, "harness-2026.09.1", 1)
            RELEASE.write_zip(source, second, "harness-2026.09.1", 1)
            self.assertEqual(RELEASE.sha256(first), RELEASE.sha256(second))
            with self.assertRaises(RELEASE.ReleaseError):
                RELEASE.verified_archive(first)
            first.with_suffix(first.suffix + ".sha256").write_text(
                f"{RELEASE.sha256(first)}  {first.name}\n", encoding="ascii"
            )
            self.assertEqual("harness-2026.09.1", RELEASE.verified_archive(first))

    def test_version(self) -> None:
        self.assertEqual(("2026.09.1", "harness-2026.09.1"), RELEASE.version_tag("2026.09.1"))
        with self.assertRaises(RELEASE.ReleaseError):
            RELEASE.version_tag("v1")

    def test_build_rejects_any_upstream_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(RELEASE, "run", side_effect=["", "head", "head", "other"]):
                with self.assertRaisesRegex(RELEASE.ReleaseError, "not synchronized"):
                    RELEASE.build("2026.09.1", Path(temporary) / "out", Path(temporary) / "cache")

    def test_candidate_freezes_dirty_bytes_and_only_explicit_new_product_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo, staging = root / "repo", root / "staging"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "work").write_text("old")
            subprocess.run(["git", "add", "work"], cwd=repo, check=True)
            (repo / "work").write_text("dirty implementation")
            (repo / ".studio").mkdir()
            (repo / ".studio" / "new.py").write_text("new implementation")
            (repo / ".studio" / "private.json").write_text("do not include")
            (repo / ".studio" / ".env").write_text("secret")
            hashes = RELEASE.freeze_sources(staging, [".studio/new.py"], repo)
            self.assertEqual(set(hashes), {"work", ".studio/new.py"})
            self.assertEqual((staging / "work").read_text(), "dirty implementation")
            (repo / "work").write_text("later edit")
            self.assertEqual(RELEASE.sha256(staging / "work"), hashes["work"])
            with self.assertRaises(RELEASE.ReleaseError):
                RELEASE.freeze_sources(root / "unsafe", [".studio/.env"], repo)
            (repo / ".studio" / "link.py").symlink_to(repo / "work")
            with self.assertRaises(RELEASE.ReleaseError):
                RELEASE.freeze_sources(root / "linked", [".studio/link.py"], repo)

    def test_runtime_zip_rejects_windows_escape_and_extracts_locked_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "asset.zip"
            for name in ("../escape", "C:/escape", "dir\\escape"):
                with zipfile.ZipFile(archive, "w") as bundle:
                    bundle.writestr(name, "invalid")
                with self.assertRaises(RELEASE.ReleaseError):
                    RELEASE.extract_zip(archive, root / "out")
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("node-fixed/node.exe", b"locked")
            RELEASE.extract_zip(archive, root / "out", "node-fixed")
            self.assertEqual((root / "out" / "node.exe").read_bytes(), b"locked")

    def test_release_omits_finished_library_but_keeps_contracts_and_profile_routing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = (".studio/components/example/v1/component.html", ".studio/backgrounds/example/v1/background.html",
                     ".studio/component_harness.py", ".studio/asset_store.py",
                     ".agents/skills/hyperframes-codex-workflow/profile-registry.json")
            for name in paths:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture")
            RELEASE.strip_bundled_assets(root)
            self.assertFalse((root / ".studio/components").exists())
            self.assertFalse((root / ".studio/backgrounds").exists())
            self.assertTrue(all((root / name).is_file() for name in paths[2:]))

    def test_incomplete_native_lock_cannot_produce_a_python_only_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "windows-runtime.lock.json").write_text(json.dumps({
                "target": "windows-x64", "assets": [{}], "pending_assets": ["Windows Node archive"]
            }))
            with self.assertRaisesRegex(RELEASE.ReleaseError, "closure incomplete"):
                RELEASE.stage_runtime(root, root / "cache")


if __name__ == "__main__":
    unittest.main()
