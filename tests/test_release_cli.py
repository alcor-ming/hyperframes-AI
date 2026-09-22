from __future__ import annotations

from importlib.machinery import SourceFileLoader
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
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
    def test_staged_checks_use_pinned_wsl_parser(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            parser = repo / ".studio/.runtime/dependency-parser"
            for package in ("acorn", "esbuild"):
                (parser / "node_modules" / package).mkdir(parents=True)
            with mock.patch.object(RELEASE, "REPO", repo), mock.patch.object(RELEASE.subprocess, "run") as run:
                RELEASE.release_checks(repo / "staging")
            self.assertEqual(2, run.call_count)
            self.assertTrue(all(call.kwargs["env"]["HYPERFRAMES_DEPENDENCY_MODULE_ROOT"] == str(parser)
                                for call in run.call_args_list))

    @unittest.skipUnless(sys.platform == "linux" and os.environ.get("HF_DEPLOY_NATIVE_TEST_ROOT"),
                         "Set HF_DEPLOY_NATIVE_TEST_ROOT to a Windows-mounted isolated test parent")
    def test_native_deployment_entrypoint(self):
        parent = Path(os.environ["HF_DEPLOY_NATIVE_TEST_ROOT"])
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="deploy-fixture-", dir=parent) as temporary:
            base = Path(temporary)
            root = base / "\u90e8\u7f72 root"
            for name in ("works/active", "works/parked", "works/archive", "assets"):
                (root / name).mkdir(parents=True)
            win = lambda path: RELEASE.run("wslpath", "-w", str(path), capture=True)
            config = base / "config.json"
            config.write_text(json.dumps({"work_root": win(root), "asset_root": win(root / "assets")}))
            real_lock = json.loads(RELEASE.RUNTIME_LOCK.read_text())
            python_asset = next(asset for asset in real_lock["assets"] if asset["kind"] == "python")
            lock = base / "fixture-lock.json"
            lock.write_text(json.dumps({"target": "windows-x64", "assets": [python_asset],
                                       "required_files": ["runtime/python/python.exe"]}))
            args = RELEASE.parser().parse_args(["deploy", "--root", win(root), "--config", win(config),
                                               "--output-dir", str(base / "artifacts")])
            def fixture_candidate(build_id, output, cache, includes, *, channel, runtime_files):
                source = base / ("source-" + build_id)
                (source / ".studio").mkdir(parents=True)
                for name in ("root_deploy.py", "windows_runtime.py"):
                    shutil.copy2(REPO / ".studio" / name, source / ".studio" / name)
                shutil.copy2(REPO / "release", source / "release")
                shutil.copy2(lock, source / "windows-runtime.lock.json")
                (source / "work.cmd").write_text(build_id)
                if runtime_files is None:
                    binary = source / "runtime/python/python.exe"
                    binary.parent.mkdir(parents=True)
                    binary.write_bytes(b"fixture dependency, never executed")
                manifest = {"release": "local-" + build_id, "channel": "local", "layout": "root-v1", "target": "windows-x64",
                            "package_kind": "full" if runtime_files is None else "tools",
                            "files": {p.relative_to(source).as_posix(): RELEASE.sha256(p) for p in source.rglob("*") if p.is_file()}}
                if runtime_files is not None:
                    manifest.update(runtime_files=runtime_files, runtime_lock_sha256=RELEASE.sha256(lock))
                (source / ".release.json").write_text(json.dumps(manifest))
                archive = output / "fixture.zip"
                RELEASE.write_zip(source, archive, manifest["release"], 1)
                archive.with_suffix(".zip.sha256").write_text(f"{RELEASE.sha256(archive)}  {archive.name}\n")
                return archive
            with mock.patch.object(RELEASE, "RUNTIME_LOCK", lock), \
                 mock.patch.object(RELEASE, "candidate", side_effect=fixture_candidate):
                first = RELEASE.deploy_windows(args)
                self.assertEqual(first["package_kind"], "full")
                for _ in range(3):
                    result = RELEASE.deploy_windows(args)
                    self.assertEqual(result["package_kind"], "tools")
                    self.assertFalse((root / result["backup"] / "runtime").exists())
                self.assertEqual(len(list((root / ".studio/.runtime/deploy-backups").iterdir())), 2)
                self.assertEqual(len(list((base / "artifacts").rglob("receipt.json"))), 3)
                self.assertFalse(list((base / ".hyperframes-deploy").iterdir()))
                (root / "work.cmd").write_text("user edit")
                with self.assertRaisesRegex(RELEASE.ReleaseError, "Native deployment failed"):
                    RELEASE.deploy_windows(args)
                self.assertEqual((root / "work.cmd").read_text(), "user edit")
                self.assertEqual(len(list((base / ".hyperframes-deploy").iterdir())), 1)

    def test_deploy_arguments_and_runtime_selection(self):
        args = RELEASE.parser().parse_args(["deploy", "--root", r"D:\AI\AI+hyperframes"])
        self.assertEqual(args.keep, 2)
        self.assertFalse(args.full)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock = root / "lock.json"
            lock.write_text(json.dumps({"required_files": ["runtime/python/python.exe"]}))
            self.assertIsNone(RELEASE.reusable_runtime(root, lock))
            state = root / ".studio/.runtime/deployment.json"
            state.parent.mkdir(parents=True)
            files = {"runtime/python/python.exe": "a" * 64, "windows-runtime.lock.json": RELEASE.sha256(lock)}
            state.write_text(json.dumps({"files": files}))
            self.assertEqual(RELEASE.reusable_runtime(root, lock), {"runtime/python/python.exe": "a" * 64})
            lock.write_text("{}")
            self.assertIsNone(RELEASE.reusable_runtime(root, lock))

    def test_artifact_retention_only_removes_verified_owned_successes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("01", "02", "03", "04", "05"):
                directory = root / name
                directory.mkdir()
                archive = directory / "package.zip"
                archive.write_bytes(b"archive")
                (directory / "receipt.json").write_text(json.dumps({"owner": "release-deploy-v1", "target": "fixture",
                    "artifacts": {"package.zip": RELEASE.sha256(archive)}}))
            (root / "02" / "user.txt").write_text("unknown")
            (root / "03" / "package.zip").write_bytes(b"changed")
            removed = RELEASE.prune_artifacts(root, "fixture", 2)
            self.assertEqual(removed, [str(root / "01")])
            self.assertTrue((root / "02" / "user.txt").exists())
            self.assertTrue((root / "03").exists())
            # Current must survive even if wall time moved backwards or its UUID sorts first.
            removed = RELEASE.prune_artifacts(root, "fixture", 1, root / "04")
            self.assertEqual(removed, [str(root / "05")])
            self.assertTrue((root / "04" / "receipt.json").exists())
            (root / "03" / "receipt.json").write_text("[]")
            RELEASE.prune_artifacts(root, "fixture", 1, root / "04")

    def test_tools_candidate_omits_runtime_but_keeps_exact_requirement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def freeze(staging, includes):
                (staging / "windows-runtime.lock.json").write_text("locked")
                return {"windows-runtime.lock.json": RELEASE.sha256(staging / "windows-runtime.lock.json")}
            runtime = {"runtime/python/python.exe": "a" * 64}
            with mock.patch.object(RELEASE, "run", side_effect=["head", "dirty"]), \
                 mock.patch.object(RELEASE, "freeze_sources", side_effect=freeze), \
                 mock.patch.object(RELEASE, "stage_skills", return_value={}), \
                 mock.patch.object(RELEASE, "stage_windows_rules"), \
                 mock.patch.object(RELEASE, "release_checks"), \
                 mock.patch.object(RELEASE, "stage_runtime") as stage:
                archive = RELEASE.candidate("fixture", root / "out", root / "cache", [], channel="local", runtime_files=runtime)
            stage.assert_not_called()
            with zipfile.ZipFile(archive) as bundle:
                manifest = json.loads(bundle.read("local-fixture/.release.json"))
                self.assertEqual(manifest["package_kind"], "tools")
                self.assertEqual(manifest["runtime_files"], runtime)
                self.assertFalse(any("/runtime/" in name for name in bundle.namelist()))

    def test_development_harness_cannot_enter_any_product_archive(self) -> None:
        forbidden = (".trellis/project.json", ".trellis/tasks/example/prd.md",
                     ".trellis/plans/example.md", "AGENTS.override.md", "BOARD.md",
                     ".codex/agents/local.toml", ".claude/settings.json",
                     ".agents/skills/trellis-start/SKILL.md", ".agents/skills/gitnexus/SKILL.md")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            for name in forbidden:
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("development only")
                self.assertFalse(RELEASE.public_source(name))
                with self.assertRaises(RELEASE.ReleaseError):
                    RELEASE.freeze_sources(root / "explicit", [name], repo)
            for name in (".studio/component_harness.py", ".agents/skills/hyperframes-codex-workflow/SKILL.md",
                         "docs/PRD/product.md"):
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("product")
                self.assertTrue(RELEASE.public_source(name))
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            staged = root / "candidate"
            sources = RELEASE.freeze_sources(staged, [], repo)
            self.assertFalse(set(sources) & set(forbidden))
            RELEASE.write_zip(staged, root / "candidate.zip", "candidate-test", 1)
            for name in forbidden:
                with self.subTest(name=name):
                    leaked = staged / name
                    leaked.parent.mkdir(parents=True, exist_ok=True)
                    leaked.write_text("leaked")
                    with self.assertRaisesRegex(RELEASE.ReleaseError, "Development Harness"):
                        RELEASE.write_zip(staged, root / "leaked.zip", "local-test", 1)
                    leaked.unlink()
                    # Empty development directories are also forbidden.
                    while leaked.parent != staged and not any(leaked.parent.iterdir()):
                        leaked = leaked.parent
                        leaked.rmdir()
            with mock.patch.object(RELEASE, "run", side_effect=["", "head", "head", "head", ""]), \
                 mock.patch.object(RELEASE.tarfile, "open") as bundle, \
                 mock.patch.object(RELEASE, "stage_skills") as skills:
                def contaminate(destination, **kwargs):
                    (destination / "AGENTS.override.md").write_text("development only")
                bundle.return_value.__enter__.return_value.extractall.side_effect = contaminate
                with self.assertRaisesRegex(RELEASE.ReleaseError, "Development Harness"):
                    RELEASE.build("2026.09.1", root / "stable", root / "cache")
                skills.assert_not_called()

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
        local = RELEASE.parser().parse_args(["local", "root-001", "--runtime-cache", "/tmp/cache"])
        self.assertEqual(local.command, "local")

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
