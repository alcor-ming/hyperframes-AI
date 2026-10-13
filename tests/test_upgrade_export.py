import json
from pathlib import Path
from unittest import mock
import test_work_cli as fixtures
import exports
api = fixtures.WORK_CLI


class UpgradeExportTest(fixtures.WorkCliTest):
    def test_export_stays_active_and_copy_failure_retries_without_render(self):
        work_id, work = self.new_work()
        draft = self.prepare_preview(work)
        self.invoke('preview', 'register', str(draft))
        self.invoke('preview', 'accept', 'draft-v001')
        final = self.root / 'render.mp4'
        final.write_bytes(b'encoded-fixture')
        with mock.patch.object(exports, 'publish', side_effect=OSError('copy full')):
            error = self.invoke('finalize', str(final), '--qa-passed', expected=2)
        self.assertIn('copy failed', error)
        variant = work / 'variants/main'
        self.assertEqual('active', api.locate_work(self.root, work_id)[1])
        self.assertNotEqual('archived', api.read_json(variant / 'variant.yaml').get('lifecycle'))
        self.assertEqual(b'encoded-fixture', (variant / 'final/final.mp4').read_bytes())
        with mock.patch.object(api, 'command_preview_render', side_effect=AssertionError('rendered twice')):
            self.invoke('finalize')
            self.invoke('finalize')
        receipt = api.read_json(variant / '.runtime/finalize.json')
        self.assertEqual('complete', receipt['state'])
        leaf = Path(receipt['export']['directory'])
        self.assertEqual(1, len(list(leaf.glob('*.mp4'))))
        self.assertEqual(b'encoded-fixture', (leaf / receipt['export']['files']['video']).read_bytes())
        self.assertEqual('active', api.locate_work(self.root, work_id)[1])


# Only collect this change's behavior; helpers are shared with the CLI fixture.
for name in tuple(vars(fixtures.WorkCliTest)):
    if name.startswith('test_'):
        setattr(UpgradeExportTest, name, None)
