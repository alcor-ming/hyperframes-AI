"""Offline source cache and borrowed-provenance regression tests."""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDIO_DIR = REPO_ROOT / ".studio"
ENV_KEYS = (
    "HYPERFRAMES_AI_HOME",
    "HYPERFRAMES_AI_WORK_ROOT",
    "HYPERFRAMES_AI_CONFIG",
    "HYPERFRAMES_AI_ASSET_CONFIG",
    "HYPERFRAMES_AI_RESOLVED_CONFIG",
)

sys.path.insert(0, str(STUDIO_DIR))
import designs
import design_sources


def _force_rmtree(path):
    path = Path(path)
    if not path.exists():
        return
    for current in sorted(path.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        try:
            os.chmod(current, 0o755 if current.is_dir() and not current.is_symlink() else 0o644)
        except OSError:
            pass
    try:
        os.chmod(path, 0o755)
    except OSError:
        pass
    shutil.rmtree(path, ignore_errors=True)


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_tar(output, entries):
    """Write a synthetic (possibly hostile) tar archive to ``output``."""
    with tarfile.open(output, "w") as packed:
        for entry in entries:
            kind = entry.get("kind", "file")
            info = tarfile.TarInfo(entry["name"])
            if kind == "dir":
                info.type = tarfile.DIRTYPE
                packed.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = entry.get("link", "target")
                packed.addfile(info)
            else:
                payload = entry.get("data", "").encode("utf-8")
                info.size = len(payload)
                packed.addfile(info, io.BytesIO(payload))


class SourceTestCase(unittest.TestCase):
    url = "https://example.com/acme/source.git"
    commit = "a" * 40

    def setUp(self):
        self._env = {key: os.environ.pop(key, None) for key in ENV_KEYS}
        self._temp_roots = []
        self.design_root = self._make_temp("design-root-")
        self.config = {"design_root": str(self.design_root)}

    def tearDown(self):
        for root in reversed(self._temp_roots):
            _force_rmtree(root)
        for key, value in self._env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _make_temp(self, prefix):
        path = Path(os.path.realpath(tempfile.mkdtemp(prefix=prefix)))
        self._temp_roots.append(path)
        return path

    def _cache_dir(self, commit=None):
        return (Path(self.config["design_root"]) / ".sources"
                / design_sources.identity(self.url, commit or self.commit))

    def _add_source(self, entries, *, commit=None):
        commit = self.commit if commit is None else commit
        with mock.patch.object(design_sources, "_archive",
                               lambda url, given, directory, output: _write_tar(output, entries)):
            return design_sources.source_add(self.url, commit, config=self.config)


class IdentityTests(SourceTestCase):
    def test_identity_is_url_digest_and_full_commit(self):
        first = design_sources.identity(self.url, self.commit)
        prefix, _, commit = first.partition("@")
        self.assertEqual(len(prefix), 24)
        self.assertEqual(commit, self.commit)
        self.assertEqual(design_sources.identity(self.url, self.commit), first)

    def test_identity_rejects_incomplete_or_uppercase_commit(self):
        for commit in ("a" * 39, "a" * 41, "A" * 40, "g" * 40, "", None, 7):
            with self.subTest(commit=commit):
                with self.assertRaises(designs.DesignError):
                    design_sources.identity(self.url, commit)

    def test_identity_rejects_credentials_and_plain_http(self):
        urls = (
            "http://example.com/a.git",
            "ssh://git@example.com/a.git",
            "https://user@example.com/a.git",
            "https://user:secret@example.com/a.git",
            "https://example.com/a.git?ref=main",
            "https://example.com/a.git#frag",
            "https://example.com",
            "https://example.com/",
            "https:///a.git",
        )
        for url in urls:
            with self.subTest(url=url):
                with self.assertRaises(designs.DesignError):
                    design_sources.identity(url, self.commit)


class CacheTests(SourceTestCase):
    def test_published_cache_is_read_only_and_stable(self):
        entries = [
            {"name": "README.md", "data": "hello"},
            {"name": "LICENSE", "data": "MIT"},
            {"name": "src", "kind": "dir"},
            {"name": "src/app.js", "data": "code"},
        ]
        record = self._add_source(entries)
        destination = Path(record["path"])
        self.assertEqual(destination, self._cache_dir())
        self.assertEqual(sorted(record["files"]), ["LICENSE", "README.md", "src/app.js"])
        self.assertEqual(record["files"]["README.md"]["sha256"], _sha("hello"))
        self.assertEqual(record["files"]["README.md"]["license"], "unreviewed")
        self.assertIn("LICENSE", record["files"]["README.md"]["license_files"])
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o555)
        self.assertEqual(stat.S_IMODE((destination / "source.json").stat().st_mode), 0o444)
        self.assertEqual(stat.S_IMODE((destination / "files" / "README.md").stat().st_mode), 0o444)
        self.assertEqual(stat.S_IMODE((destination / "files" / "src").stat().st_mode), 0o555)
        self.assertEqual(stat.S_IMODE((destination / "files" / "src" / "app.js").stat().st_mode), 0o444)
        first = design_sources.manifest(self.url, self.commit, config=self.config)
        second = design_sources.manifest(self.url, self.commit, config=self.config)
        self.assertEqual(first, second)
        self.assertEqual(first, {key: value for key, value in record.items() if key != "path"})

    def test_published_cache_is_not_refetched(self):
        record = self._add_source([{"name": "a.txt", "data": "one"}])

        def refuse(*args, **kwargs):
            raise AssertionError("_archive ran for a published cache")

        with mock.patch.object(design_sources, "_archive", refuse):
            again = design_sources.source_add(self.url, self.commit, config=self.config)
        self.assertEqual(again["path"], record["path"])
        self.assertEqual(again["files"], record["files"])

    def test_changed_cached_bytes_are_rejected(self):
        self._add_source([{"name": "a.txt", "data": "one"}])
        target = self._cache_dir() / "files" / "a.txt"
        os.chmod(target, 0o644)
        target.write_text("tampered", encoding="utf-8")
        with self.assertRaises(designs.DesignError):
            design_sources.manifest(self.url, self.commit, config=self.config)

    def test_deleted_cached_file_is_rejected(self):
        self._add_source([{"name": "a.txt", "data": "one"}])
        directory = self._cache_dir() / "files"
        os.chmod(directory, 0o755)
        os.chmod(directory / "a.txt", 0o644)
        (directory / "a.txt").unlink()
        with self.assertRaises(designs.DesignError):
            design_sources.manifest(self.url, self.commit, config=self.config)

    def test_tampered_manifest_is_rejected(self):
        self._add_source([{"name": "a.txt", "data": "one"}])
        path = self._cache_dir() / "source.json"
        os.chmod(path, 0o644)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["files"]["a.txt"]["sha256"] = _sha("other")
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(designs.DesignError):
            design_sources.manifest(self.url, self.commit, config=self.config)

    def test_missing_cache_is_rejected(self):
        with self.assertRaises(designs.DesignError):
            design_sources.manifest(self.url, self.commit, config=self.config)

    def test_fixture_is_offline(self):
        def refuse(*args, **kwargs):
            raise AssertionError("subprocess launched while adding a source")

        with mock.patch.object(design_sources, "_archive",
                               lambda url, commit, directory, output: _write_tar(
                                   output, [{"name": "a.txt", "data": "x"}])), \
                mock.patch.object(design_sources.subprocess, "run", refuse):
            record = design_sources.source_add(self.url, self.commit, config=self.config)
        self.assertEqual(record["files"]["a.txt"]["sha256"], _sha("x"))


class ArchiveSafetyTests(SourceTestCase):
    def _rejected_add(self, entries):
        with mock.patch.object(design_sources, "_archive",
                               lambda url, commit, directory, output: _write_tar(output, entries)):
            with self.assertRaises(designs.DesignError):
                design_sources.source_add(self.url, self.commit, config=self.config)
        self.assertFalse(self._cache_dir().exists())
        self.assertEqual(list((self.design_root / ".sources").iterdir()), [])

    def test_parent_traversal_entry_is_rejected(self):
        self._rejected_add([{"name": "../escape.txt", "data": "boom"}])

    def test_absolute_entry_is_rejected(self):
        self._rejected_add([{"name": "/etc/escape.txt", "data": "boom"}])

    def test_symlink_entry_is_rejected(self):
        self._rejected_add([{"name": "link", "kind": "symlink", "link": "target"}])

    def test_duplicate_entry_is_rejected(self):
        self._rejected_add([
            {"name": "dup.txt", "data": "one"},
            {"name": "dup.txt", "data": "two"},
        ])


class ExternalRecordTests(SourceTestCase):
    def _record(self):
        return {
            "kind": "external",
            "url": self.url,
            "commit": self.commit,
            "files": {
                "src/app.js": {"sha256": _sha("code"), "license": "MIT", "attribution": "Acme"},
            },
        }

    def test_valid_record_passes(self):
        self.assertIsNone(design_sources.validate_record(self._record()))

    def test_record_must_be_external(self):
        record = self._record()
        record["kind"] = "local"
        with self.assertRaises(designs.DesignError):
            design_sources.validate_record(record)

    def test_record_must_carry_per_file_files(self):
        for files in ({}, None, [], "src/app.js"):
            with self.subTest(files=files):
                record = self._record()
                record["files"] = files
                with self.assertRaises(designs.DesignError):
                    design_sources.validate_record(record)

    def test_record_rejects_non_mapping_file_entry(self):
        record = self._record()
        record["files"]["src/app.js"] = "MIT"
        with self.assertRaises(designs.DesignError):
            design_sources.validate_record(record)

    def test_record_rejects_unsafe_path(self):
        record = self._record()
        record["files"] = {
            "../escape.js": {"sha256": _sha("x"), "license": "MIT", "attribution": "Acme"},
        }
        with self.assertRaises(designs.DesignError):
            design_sources.validate_record(record)

    def test_record_requires_hash_license_and_attribution(self):
        mutations = {
            "missing sha256": lambda item: item.pop("sha256"),
            "short sha256": lambda item: item.__setitem__("sha256", "abc"),
            "uppercase sha256": lambda item: item.__setitem__("sha256", "A" * 64),
            "missing license": lambda item: item.pop("license"),
            "blank license": lambda item: item.__setitem__("license", "   "),
            "unreviewed license": lambda item: item.__setitem__("license", "unreviewed"),
            "missing attribution": lambda item: item.pop("attribution"),
            "blank attribution": lambda item: item.__setitem__("attribution", " \t"),
        }
        for label, mutate in mutations.items():
            with self.subTest(case=label):
                record = self._record()
                mutate(record["files"]["src/app.js"])
                with self.assertRaises(designs.DesignError):
                    design_sources.validate_record(record)


class CompareTests(SourceTestCase):
    commit_a = "1" * 40
    commit_b = "2" * 40

    def _record(self, manifest):
        return {
            "kind": "external",
            "url": self.url,
            "commit": self.commit_a,
            "files": {
                path: {"sha256": info["sha256"], "license": "MIT", "attribution": "Acme"}
                for path, info in manifest["files"].items()
            },
        }

    def test_compare_reports_changed_and_deleted_files(self):
        before = self._add_source(
            [
                {"name": "keep.txt", "data": "keep"},
                {"name": "edit.txt", "data": "before"},
                {"name": "gone.txt", "data": "gone"},
            ],
            commit=self.commit_a,
        )
        self._add_source(
            [
                {"name": "keep.txt", "data": "keep"},
                {"name": "edit.txt", "data": "after"},
                {"name": "added.txt", "data": "new"},
            ],
            commit=self.commit_b,
        )
        result = design_sources.compare(self._record(before), self.commit_b, config=self.config)
        self.assertEqual(result["source"], {"url": self.url, "commit": self.commit_b})
        self.assertTrue(result["source_changed"])
        self.assertEqual(sorted(result["files"]), ["edit.txt", "gone.txt"])
        self.assertEqual(result["files"]["edit.txt"],
                         {"recorded": _sha("before"), "source": _sha("after")})
        self.assertEqual(result["files"]["gone.txt"],
                         {"recorded": _sha("gone"), "source": None})

    def test_compare_defaults_to_recorded_commit(self):
        before = self._add_source([{"name": "keep.txt", "data": "keep"}], commit=self.commit_a)
        result = design_sources.compare(self._record(before), config=self.config)
        self.assertEqual(result["source"], {"url": self.url, "commit": self.commit_a})
        self.assertFalse(result["source_changed"])
        self.assertEqual(result["files"], {})

    def test_compare_requires_valid_external_record(self):
        before = self._add_source([{"name": "keep.txt", "data": "keep"}], commit=self.commit_a)
        record = self._record(before)
        record["files"]["keep.txt"].pop("attribution")
        with self.assertRaises(designs.DesignError):
            design_sources.compare(record, self.commit_a, config=self.config)


class SourcesNotCardsTests(SourceTestCase):
    def test_source_cache_is_not_a_design_card(self):
        self._add_source([{"name": "README.md", "data": "hello"}])
        cache = self.design_root / ".sources"
        self.assertTrue(cache.is_dir())
        self.assertTrue(any(cache.iterdir()))
        self.assertFalse(self.design_root.is_relative_to(designs.REPO))
        self.assertEqual(designs._scan(self.design_root), {})
        repo = self._make_temp('source-tool-root-')
        self.assertEqual(designs.design_ids(root=repo, config=self.config), ())
        self.assertIn(self.design_root, designs.card_roots(root=repo, config=self.config))


if __name__ == "__main__":
    unittest.main()
