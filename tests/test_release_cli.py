from __future__ import annotations

from importlib.machinery import SourceFileLoader
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
