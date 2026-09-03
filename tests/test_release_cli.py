from __future__ import annotations

from contextlib import redirect_stdout
from importlib.machinery import SourceFileLoader
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
LOADER = SourceFileLoader("release_cli", str(REPO / "release"))
SPEC = importlib.util.spec_from_loader("release_cli", LOADER)
assert SPEC
RELEASE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(RELEASE)


class ReleaseCliTest(unittest.TestCase):
    def test_archive_is_deterministic_and_checksum_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "file.txt").write_text("fixed\n", encoding="utf-8")
            first = root / "first.tar.gz"
            second = root / "second.tar.gz"
            RELEASE.write_archive(source, first, "harness-2026.09.0", 1)
            RELEASE.write_archive(source, second, "harness-2026.09.0", 1)
            self.assertEqual(RELEASE.sha256(first), RELEASE.sha256(second))
            with self.assertRaises(RELEASE.ReleaseError):
                RELEASE.verified_archive(first)
            first.with_suffix(first.suffix + ".sha256").write_text(
                f"{RELEASE.sha256(first)}  {first.name}\n", encoding="ascii"
            )
            self.assertEqual("harness-2026.09.0", RELEASE.verified_archive(first))

    def test_version_and_atomic_rollback(self) -> None:
        self.assertEqual(("2026.09.0", "harness-2026.09.0"), RELEASE.version_tag("2026.09.0"))
        with self.assertRaises(RELEASE.ReleaseError):
            RELEASE.version_tag("v1")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "releases" / "harness-2026.09.0"
            second = root / "releases" / "harness-2026.09.1"
            first.mkdir(parents=True)
            second.mkdir()
            RELEASE.activate(root, first)
            RELEASE.activate(root, second)
            self.assertEqual(second, (root / "current").resolve())
            self.assertEqual(first, (root / "previous").resolve())
            with redirect_stdout(io.StringIO()):
                RELEASE.rollback(root)
            self.assertEqual(first, (root / "current").resolve())


if __name__ == "__main__":
    unittest.main()
