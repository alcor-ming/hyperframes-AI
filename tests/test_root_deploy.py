import json
import os
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
import root_deploy as deploy
from windows_runtime import command_lock


class RootDeploymentTests(unittest.TestCase):
    def test_idle_ignores_host_cwd_but_blocks_root_children(self):
        root = r'D:\AI\AI+hyperframes'
        host = {'ProcessId': 987654, 'CommandLine': 'node kernel.js --working-dir ' + root,
                'ExecutablePath': r'C:\Codex\node.exe'}
        with patch.object(deploy.os, 'name', 'nt'), patch.object(deploy.subprocess, 'run') as run:
            run.return_value.stdout = json.dumps([host])
            deploy.idle(root)
            for command in (root + r'\runtime\node\node.exe', 'node ' + root + r'\works\build.js'):
                run.return_value.stdout = json.dumps([{**host, 'CommandLine': command}])
                with self.assertRaisesRegex(ValueError, 'is active'):
                    deploy.idle(root)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "root"
        for name in ("works/active", "works/parked", "works/archive", "asset-library/store", "asset-library/sources/demo"):
            (self.root / name).mkdir(parents=True)
        self.config = self.base / "config.json"
        self.settings = {"work_root": str(self.root), "asset_root": str(self.root / "asset-library/store"), "asset_review_root": str(self.root / "asset-library"), "asset_source_roots": [str(self.root / "asset-library/sources/demo")], "review": True, "review_protected_roots": [str(self.base / "production")]}
        self.config.write_text(json.dumps(self.settings))

    def package(self, name):
        root = self.base / name
        root.mkdir()
        (root / "work.cmd").write_text(name)
        deploy.write_json(root / ".release.json", {"release": "candidate-" + name, "channel": "candidate", "target": "windows-x64", "layout": "root-v1", "files": {"work.cmd": deploy.digest(root / "work.cmd")}})
        return root

    def test_update_rollback_preserves_user_content_and_config(self):
        first = self.package("one")
        deploy.deploy(first, self.root, self.config)
        user = self.root / ".agents/skills/user/SKILL.md"
        user.parent.mkdir(parents=True)
        user.write_text("user content")
        content = self.root / "works/active/scene.html"
        content.write_text("M2-M3 content")
        config = (self.root / deploy.CONFIG).read_bytes()
        deploy.deploy(self.package("two"), self.root, None)
        self.assertEqual(deploy.verify_root(self.root)["release"], "candidate-two")
        deploy.recover(self.root, rollback=True)
        self.assertEqual(deploy.verify_root(self.root)["release"], "candidate-one")
        self.assertEqual(user.read_text(), "user content")
        self.assertEqual(content.read_text(), "M2-M3 content")
        self.assertEqual((self.root / deploy.CONFIG).read_bytes(), config)
        self.assertFalse((self.root / ".harness").exists())

    def test_strict_package_and_managed_root_are_different(self):
        package = self.package("one")
        (package / "extra.txt").write_text("x")
        with self.assertRaisesRegex(ValueError, "Unmanifested"):
            deploy.verify_package(package)
        (package / "extra.txt").unlink()
        deploy.deploy(package, self.root, self.config)
        (self.root / "extra.txt").write_text("x")
        deploy.verify_root(self.root)
        (self.root / "work.cmd").write_text("user edit")
        with self.assertRaisesRegex(ValueError, "Locally modified"):
            deploy.deploy(self.package("two"), self.root, None)
        with self.assertRaisesRegex(ValueError, "Locally modified"):
            deploy.recover(self.root, rollback=True)

    def test_unmanaged_collision_and_links_rejected(self):
        package = self.package("one")
        (self.root / "work.cmd").write_text("old entry")
        with self.assertRaisesRegex(ValueError, "Unmanaged"):
            deploy.deploy(package, self.root, self.config)
        (self.root / "work.cmd").unlink()
        link = self.root / "asset-library/sources/demo/link"
        if os.name == "nt":
            subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(link), str(self.base)], check=True, capture_output=True)
            self.addCleanup(lambda: os.rmdir(link))
        else:
            link.symlink_to(self.base, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Links"):
            deploy.deploy(package, self.root, self.config)

    def test_failed_copy_restores_and_pending_recovery(self):
        deploy.deploy(self.package("one"), self.root, self.config)
        package = self.package("two")
        replace = deploy.os.replace
        def fail(source, target):
            if Path(source).name.startswith("work.cmd.deploy-") and Path(source).read_text() == "two":
                raise OSError("injected copy failure")
            return replace(source, target)
        with patch.object(deploy.os, "replace", side_effect=fail):
            with self.assertRaisesRegex(OSError, "injected"):
                deploy.deploy(package, self.root, None)
        self.assertEqual(deploy.verify_root(self.root)["release"], "candidate-one")
        deploy.deploy(package, self.root, None)
        state = deploy.verify_root(self.root)
        transaction = deploy.read(self.root / state["backup"] / "transaction.json")
        deploy.write_json(self.root / deploy.PENDING, transaction)
        with self.assertRaisesRegex(ValueError, "Interrupted"):
            deploy.verify_root(self.root)
        deploy.recover(self.root)
        self.assertEqual(deploy.verify_root(self.root)["release"], "candidate-one")

    def test_candidate_scope_and_lock(self):
        package = self.package("one")
        self.settings["review"] = False
        self.config.write_text(json.dumps(self.settings))
        with self.assertRaisesRegex(ValueError, "review=true"):
            deploy.deploy(package, self.root, self.config)
        with command_lock(self.root):
            with self.assertRaisesRegex(ValueError, "busy"):
                deploy.deploy(package, self.root, self.config)
        with self.assertRaisesRegex(ValueError, "case-colliding"):
            deploy.managed({"work.cmd": "a" * 64, "WORK.CMD": "b" * 64})
        with self.assertRaisesRegex(ValueError, "user/runtime"):
            deploy.managed({"works/a": "a" * 64})

    def test_installer_runs_with_isolated_python_imports(self):
        package = self.package("isolated")
        result = subprocess.run([sys.executable, "-I", "-S", "-B", deploy.__file__, "deploy",
                                 "--package", str(package), "--root", str(self.root),
                                 "--config", str(self.config)], capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["release"], "candidate-isolated")

    def test_config_edits_block_rollback_and_protected_root_is_rejected(self):
        package = self.package("one")
        self.settings["review_protected_roots"] = [str(self.root)]
        self.config.write_text(json.dumps(self.settings))
        with self.assertRaisesRegex(ValueError, "overlaps"):
            deploy.deploy(package, self.root, self.config)
        self.settings["review_protected_roots"] = [str(self.base / "production")]
        self.config.write_text(json.dumps(self.settings))
        deploy.deploy(package, self.root, self.config)
        deploy.deploy(self.package("two"), self.root, None)
        (self.root / deploy.CONFIG).write_text("{}")
        with self.assertRaisesRegex(ValueError, "configuration edit"):
            deploy.recover(self.root, rollback=True)
        self.assertEqual((self.root / "work.cmd").read_text(), "two")
        self.assertFalse((self.root / deploy.PENDING).exists())


if __name__ == "__main__":
    unittest.main()
