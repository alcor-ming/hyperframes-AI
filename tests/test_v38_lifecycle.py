"""v3.8 lifecycle regressions; all content lives in isolated fixtures."""
import json
from pathlib import Path
from unittest import mock
import test_work_cli as fixtures
api = fixtures.WORK_CLI


class LifecycleTest(fixtures.WorkCliTest):
    # Reuse the fixture helpers without collecting the parent suite twice.
    def test_v38_park_preserves_wait_and_path(self):
        work_id, work = self.new_work()
        self.invoke('wait', 'voiceover')
        before = (work / 'variants/main/variant.yaml').read_bytes()
        self.invoke('park')
        self.assertTrue(work.is_dir())
        self.assertEqual(before, (work / 'variants/main/variant.yaml').read_bytes())
        self.invoke('resume')
        self.assertEqual(before, (work / 'variants/main/variant.yaml').read_bytes())
        self.assertFalse((work / '.runtime/parked.json').exists())

    def test_v38_export_archives_and_reopen_preserves_sibling(self):
        work_id, work = self.new_work()
        self.invoke('variant', 'add', 'wide')
        self.invoke('variant', 'use', 'main')
        draft = self.prepare_preview(work)
        self.invoke('preview', 'register', str(draft))
        self.invoke('preview', 'accept', 'draft-v001')
        final = self.root / 'final.mp4'
        final.write_bytes(b'encoded-one')
        self.invoke('finalize', str(final), '--qa-passed')
        state = api.read_json(work / 'variants/main/variant.yaml')
        self.assertEqual('archived', state.get('lifecycle'))
        self.assertEqual('active', api.locate_work(self.root, work_id)[1])
        self.invoke('--variant', 'wide', 'archive', '--outcome', 'abandoned')
        self.assertEqual('archive', api.locate_work(self.root, work_id)[1])
        self.invoke('reopen', work_id, '--variant-id', 'main')
        self.assertEqual('active', api.locate_work(self.root, work_id)[1])
        self.assertEqual('archived', api.read_json(work / 'variants/wide/variant.yaml')['lifecycle'])
        self.assertEqual(b'encoded-one', (work / 'variants/main/final/final.mp4').read_bytes())

    def test_v38_export_receipt_recovers_without_render(self):
        work_id, work = self.new_work()
        draft = self.prepare_preview(work)
        self.invoke('preview', 'register', str(draft))
        self.invoke('preview', 'accept', 'draft-v001')
        final = self.root / 'final.mp4'
        final.write_bytes(b'encoded-one')
        with mock.patch.object(api, 'move_to_archive', side_effect=OSError('archive write failed')):
            with self.assertRaises(OSError):
                self.invoke('finalize', str(final), '--qa-passed')
        self.assertEqual(b'encoded-one', (work / 'variants/main/final/final.mp4').read_bytes())
        with mock.patch.object(api, 'command_preview_render', side_effect=AssertionError('must not render')):
            self.invoke('--work', work_id, 'finalize')
        self.assertEqual('archive', api.locate_work(self.root, work_id)[1])

    def export(self, work, marker=b'one'):
        draft = self.prepare_preview(work, content=marker)
        preview = self.invoke('preview', 'register', str(draft))
        self.invoke('preview', 'accept', preview)
        final = self.root / 'export.mp4'
        final.write_bytes(marker)
        self.invoke('finalize', str(final), '--qa-passed')
        return preview, final

    def test_v38_two_drafts_keep_receipt_and_accepted_proof(self):
        work_id, work = self.new_work()
        first, _ = self.export(work)
        variant = work / 'variants/main'
        manifest = (variant / 'final/manifest.json').read_bytes()
        self.invoke('reopen', work_id)
        second, final = self.export(work, b'two')
        history = list((variant / 'final/history').glob('*/manifest.json'))
        self.assertEqual(1, len(history))
        self.assertEqual(manifest, history[0].read_bytes())
        self.assertEqual(b'one', (history[0].parent / 'final.mp4').read_bytes())
        preview, _ = api.work_successor._accepted_source(work, 'main', first, api.SimpleNamespace(**vars(api)))
        self.assertEqual(first, preview.name)
        self.invoke('finalize', str(final), '--qa-passed')
        self.assertEqual(1, len(list((variant / 'final/history').iterdir())))
        self.assertEqual(second, api.read_json(variant / 'final/manifest.json')['source_preview'])

    def test_v38_history_rotation_failure_preserves_current_and_retry_is_unique(self):
        work_id, work = self.new_work()
        self.export(work)
        variant = work / 'variants/main'
        old_manifest = (variant / 'final/manifest.json').read_bytes()
        self.invoke('reopen', work_id)
        final = self.root / 'export.mp4'
        final.write_bytes(b'two')
        original = api.write_json
        def fail(path, value):
            if path == variant / 'final/manifest.json':
                raise OSError('manifest failure')
            return original(path, value)
        with mock.patch.object(api, 'write_json', side_effect=fail):
            with self.assertRaises(OSError):
                self.invoke('finalize', str(final), '--qa-passed')
        self.assertEqual(b'one', (variant / 'final/final.mp4').read_bytes())
        self.assertEqual(old_manifest, (variant / 'final/manifest.json').read_bytes())
        self.invoke('finalize', str(final), '--qa-passed')
        self.assertEqual(1, len(list((variant / 'final/history').glob('*/manifest.json'))))

    def test_v38_pending_archive_cannot_swallow_a_new_export(self):
        work_id, work = self.new_work()
        with mock.patch.object(api, 'move_to_archive', side_effect=OSError('archive failure')):
            with self.assertRaises(OSError):
                self.export(work)
        different = self.root / 'different.mp4'
        different.write_bytes(b'different')
        result = self.invoke('finalize', str(different), '--qa-passed', expected=2)
        self.assertIn('different candidate', result)
        self.invoke('reopen', work_id)
        self.export(work, b'two')
        self.assertEqual(b'two', (work / 'variants/main/final/final.mp4').read_bytes())

    def test_v38_archived_preview_is_readable_current_is_not(self):
        work_id, work = self.new_work()
        preview, _ = self.export(work)
        args = api.build_parser().parse_args(['--work', work_id, 'preview', 'open', preview])
        path, state = api.selected_variant(self.root, work, args)
        self.assertEqual('archived', state['lifecycle'])
        args.preview_id = 'current'
        with self.assertRaisesRegex(api.HarnessError, 'Variant is archived'):
            api.selected_variant(self.root, work, args)

    def test_v38_add_to_archived_work_and_navigation(self):
        work_id, work = self.new_work()
        self.export(work)
        self.assertEqual([], json.loads(self.invoke('list')))
        self.assertEqual(work_id, json.loads(self.invoke('list', '--archived'))[0]['id'])
        self.invoke('--work', work_id, 'variant', 'add', 'wide', '--account', 'wide')
        row = json.loads(self.invoke('list'))[0]
        self.assertEqual((1, 2), (row['archived_variants'], row['variant_count']))
        self.assertEqual('archived', row['variants'][0]['lifecycle'])
        self.invoke('browser', 'rebuild')
        browser = (self.root / '浏览目录.md').read_text()
        self.assertIn('1/2 已归档', browser)
        self.assertIn('variants/main/final/final.mp4', browser)
        self.assertIn('variants/wide/project', browser)
        self.assertIsNone(row['usage']['bytes'])

    def test_v38_retired_and_broken_objects_are_isolated(self):
        _, old = self.new_work('old')
        self.update_frontmatter(old / 'WORK.md', workflow='podcast_quote_image')
        (old / 'variants/main/variant.yaml').write_text('broken')
        _, new = self.new_work('new')
        rows = api.list_work_rows(self.root)
        self.assertEqual(2, len(rows))
        self.assertIn('error', next(row for row in rows if row['id'] == old.name))
        self.assertTrue(new.is_dir())
        self.assertIn('Unknown workflow', self.invoke('--work', old.name, 'status', expected=2))

    def test_v38_park_write_failure_leaves_wait_current_and_path(self):
        work_id, work = self.new_work()
        self.invoke('wait', 'voiceover')
        before = (work / 'variants/main/variant.yaml').read_bytes()
        writer = api.write_json
        def fail(path, value):
            if path.name == 'parked.json':
                raise OSError('park failed')
            return writer(path, value)
        with mock.patch.object(api, 'write_json', side_effect=fail):
            with self.assertRaises(OSError):
                self.invoke('park')
        self.assertEqual(before, (work / 'variants/main/variant.yaml').read_bytes())
        self.assertEqual(work_id, api.read_pointer(self.root, 'current-work'))
        self.assertEqual('active', api.locate_work(self.root, work_id)[1])
        self.assertFalse((work / '.runtime/parked.json').exists())

    def test_v38_park_keeps_live_studio_binding(self):
        import os
        _, work = self.new_work()
        variant = work / 'variants/main'
        session = {'work': work.name, 'variant': 'main', 'target': 'current',
                   'project': str(variant / 'project'), 'pid': os.getpid(), 'port': 3100}
        api.write_json(api.studio_record(variant, 'current'), session)
        self.invoke('park')
        self.assertEqual(session, api.bound_studio(variant, 'current'))
        self.invoke('resume')
        self.assertEqual(session, api.bound_studio(variant, 'current'))

    def test_v38_storage_preview_protects_unknown_live_and_corrupt_history(self):
        import os
        work_id, work = self.new_work()
        self.export(work)
        variant = work / 'variants/main'
        job = variant / '.runtime/finalize-fixture'
        job.mkdir(parents=True)
        candidate = job / 'candidate.mp4'
        candidate.write_bytes(b'one')
        digest = api.file_sha256(candidate)
        api.write_json(job / 'qa.json', {'passed': True, 'sha256': digest})
        api.reclaim_final_candidates(variant, candidate, apply=False)
        (job / 'notes.txt').write_text('keep me')
        unknown = variant / '.runtime/unknown.mp4'
        unknown.write_bytes(b'unknown')
        report = json.loads(self.invoke('storage', 'cleanup'))
        self.assertEqual(3, report['reclaimable_bytes'])
        self.assertTrue(candidate.exists())
        api.write_json(api.studio_record(variant, 'current'), {'pid': os.getpid()})
        self.assertEqual(0, json.loads(self.invoke('storage', 'inspect'))['reclaimable_bytes'])
        api.studio_record(variant, 'current').unlink()
        self.invoke('reopen', work_id)
        self.export(work, b'two')
        old_video = next((variant / 'final/history').glob('*/final.mp4'))
        old_video.write_bytes(b'corrupt')
        report = json.loads(self.invoke('storage', 'cleanup', '--apply'))
        self.assertIsNone(report['reclaimable_bytes'])
        self.assertTrue(report['cleanup_errors'])
        self.assertTrue(candidate.exists())
        old_video.write_bytes(b'one')
        self.invoke('storage', 'cleanup', '--apply')
        self.assertFalse(candidate.exists())
        self.assertEqual('keep me', (job / 'notes.txt').read_text())
        self.assertEqual(b'unknown', unknown.read_bytes())
        self.assertEqual(b'one', old_video.read_bytes())


    def test_v38_legacy_resume_recovers_wait_after_interrupted_write(self):
        import shutil
        work_id, work = self.new_work()
        self.invoke('variant', 'add', 'wide')
        self.invoke('--variant', 'main', 'wait', 'voiceover')
        self.invoke('--variant', 'wide', 'archive', '--outcome', 'abandoned')
        original = {path.name: api.read_json(path / 'variant.yaml') for path in api.variant_paths(work)}
        api.write_json(work / '.runtime/parked.json', {'variants': original})
        for path in api.variant_paths(work):
            state = api.read_json(path / 'variant.yaml')
            state.update(status='parked', wait_for='none')
            api.write_variant(path, state)
        legacy = self.root / 'works/parked' / work_id
        shutil.move(work, legacy)
        writer = api.write_variant
        def fail(path, state):
            if path.name == 'wide':
                raise OSError('interrupted resume')
            writer(path, state)
        with mock.patch.object(api, 'write_variant', side_effect=fail):
            with self.assertRaises(OSError):
                self.invoke('resume')
        self.assertTrue((legacy / '.runtime/parked.json').exists())
        self.invoke('resume')
        self.assertEqual((legacy, 'active'), api.locate_work(self.root, work_id))
        for path in api.variant_paths(legacy):
            self.assertEqual(original[path.name], api.read_json(path / 'variant.yaml'))
        self.assertFalse((legacy / '.runtime/parked.json').exists())
        self.assertEqual(work_id, api.read_pointer(self.root, 'current-work'))



for name in list(fixtures.WorkCliTest.__dict__):
    if name.startswith('test_'):
        setattr(LifecycleTest, name, None)
