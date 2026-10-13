import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import exports


class ExportTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.work = self.base / 'work001'
        self.variant = self.work / 'variants/variant1'
        self.variant.mkdir(parents=True)
        self.video = self.variant / 'final.mp4'
        self.video.write_bytes(b'video fixture')
        self.cover = self.variant / 'cover.png'
        self.cover.write_bytes(b'cover fixture')
        self.root = self.base / 'exports'

    def publish(self, **kwargs):
        return exports.publish(self.root, self.work, self.variant, {'video': self.video, 'cover': self.cover}, **kwargs)

    def test_pairing_dedup_and_revision_preservation(self):
        first = self.publish(series='测试系列')
        self.assertEqual(first, self.publish(series='测试系列'))
        leaf = Path(first['directory'])
        self.assertEqual(2, len(list(leaf.glob('variant1-*'))))
        self.cover.write_bytes(b'new cover')
        second = exports.publish(self.root, self.work, self.variant, {'cover': self.cover}, series='测试系列', revision=2)
        self.assertEqual(2, second['sequence'])
        self.assertEqual(3, len(list(leaf.glob('variant1-*'))))
        self.assertEqual((leaf / first['files']['cover']).read_bytes(), b'cover fixture')

    def test_retry_only_copies_missing_files(self):
        real = exports.shutil.copyfileobj
        def fail(source, target):
            if source.name.endswith('cover.png'):
                raise OSError('disk full')
            return real(source, target)
        with patch.object(exports.shutil, 'copyfileobj', fail), self.assertRaises(OSError):
            self.publish()
        result = self.publish()
        self.assertEqual(result['sequence'], 1)
        self.assertIn('未分系列', result['directory'])
        target = Path(result['directory']) / result['files']['video']
        target.write_bytes(b'user changed')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            self.publish()
        self.assertEqual(target.read_bytes(), b'user changed')

    def test_review_escape_and_links_rejected(self):
        with self.assertRaises(ValueError): self.publish(review=True)
        with self.assertRaises(ValueError): self.publish(series='../escape')
        self.root.symlink_to(self.work, target_is_directory=True)
        with self.assertRaises(Exception): self.publish()

    def test_interrupted_index_write_does_not_block_retry_or_erase_unknown_files(self):
        with patch.object(exports.os, 'replace', side_effect=OSError('interrupted index promotion')):
            with self.assertRaises(OSError):
                self.publish()
        leaf = self.root / '未分系列' / self.work.name / self.variant.name
        for name in ('.exports.pending.json', '.exports-old.pending.json'):
            (leaf / name).write_bytes(b'unknown interrupted write')
        result = self.publish()
        self.assertEqual(1, result['sequence'])
        self.assertEqual(result, self.publish())
        self.video.write_bytes(b'new video')
        self.assertEqual(2, self.publish()['sequence'])
        for name in ('.exports.pending.json', '.exports-old.pending.json'):
            self.assertEqual(b'unknown interrupted write', (leaf / name).read_bytes())


if __name__ == '__main__': unittest.main()
