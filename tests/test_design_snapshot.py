import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import designs
import design_snapshot
import lines


class SnapshotTests(unittest.TestCase):
    def test_snapshot_is_closed_and_reports_reference_and_owned_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            card = designs.get('stage-full')
            card['references'] = ['common/3d-icon']
            own = root / 'stage-full'
            foreign = root / 'common/assets/3d-icon'
            own.mkdir()
            foreign.mkdir(parents=True)
            (own / 'design.json').write_text(json.dumps(card))
            (own / 'GUIDE.md').write_text('original guide')
            (foreign / 'asset.json').write_text('{}')
            (foreign / 'icon.svg').write_text('<svg/>')
            variant = root / 'variant'
            variant.mkdir()
            with patch.object(designs, 'require', return_value=card), \
                 patch.object(designs, 'card_path', side_effect=lambda identity: root / identity, create=True):
                receipt = design_snapshot.freeze(variant, 'stage-full')
                self.assertIsNone(design_snapshot.changes(receipt)['message'])
                (own / 'GUIDE.md').write_text('changed guide')
                (foreign / 'icon.svg').write_text('<svg><path/></svg>')
                change = design_snapshot.changes(receipt)
                self.assertEqual(['card/GUIDE.md', 'references/common/3d-icon/icon.svg'], change['files'])
                self.assertEqual(['common/3d-icon'], change['reinstall_assets'])
                self.assertIn('2 个文件、1 个引用资产', change['message'])
                design_snapshot.verify(variant / receipt['path'], receipt)
                newer = design_snapshot.freeze(variant, 'stage-full')
                self.assertNotEqual(receipt['path'], newer['path'])
                design_snapshot.verify(variant / receipt['path'], receipt)
                (variant / receipt['path'] / 'card/GUIDE.md').write_text('tampered')
                with self.assertRaisesRegex(ValueError, 'Frozen card files changed'):
                    design_snapshot.verify(variant / receipt['path'], receipt)

    def test_snapshot_skips_study_and_dot_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            card = designs.get('stage-full')
            card['references'] = []
            own = root / 'stage-full'
            own.mkdir()
            (own / 'design.json').write_text(json.dumps(card))
            (own / 'GUIDE.md').write_text('original guide')
            (own / 'study').mkdir()
            (own / 'study/notes.md').write_text('notes')
            (own / '.git').mkdir()
            (own / '.git/HEAD').write_text('ref: refs/heads/main')
            (own / '__pycache__').mkdir()
            (own / '__pycache__/x.pyc').write_text('bytecode')
            variant = root / 'variant'
            variant.mkdir()
            with patch.object(designs, 'require', return_value=card), \
                 patch.object(designs, 'card_path', side_effect=lambda identity: root / identity, create=True):
                receipt = design_snapshot.freeze(variant, 'stage-full')
                ignored = ('card/study/', 'card/.git/', 'card/__pycache__/')
                self.assertFalse([name for name in receipt['files'] if name.startswith(ignored)])
                (own / 'study/notes.md').write_text('changed notes')
                self.assertIsNone(design_snapshot.changes(receipt)['message'])
                (own / 'GUIDE.md').write_text('changed guide')
                self.assertIsNotNone(design_snapshot.changes(receipt)['message'])

    def test_json_only_legacy_snapshot_does_not_consult_catalog(self):
        card = designs.get('stage-full')
        state = {'line': {'id': card['id'], 'version': card['version']},
                 'design_snapshot': card, 'design_sha256': lines.card_digest(card)}
        with patch.object(designs, 'catalog', side_effect=AssertionError('must remain offline')):
            self.assertEqual(card, lines.frozen(state))

    def test_snapshot_rejects_linked_card(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'outside').write_text('private')
            directory = root / 'card'
            directory.mkdir()
            (directory / 'leak').symlink_to(root / 'outside')
            with patch.object(designs, 'require', return_value={'id': 'card'}), \
                 patch.object(designs, 'card_path', return_value=directory, create=True):
                with self.assertRaisesRegex(ValueError, 'links'):
                    design_snapshot.inventory('card')


if __name__ == '__main__':
    unittest.main()
