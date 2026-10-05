"""Asset selection round trips use only isolated source/store/config fixtures."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import test_asset_discovery as fixtures
import work

STORE = fixtures.STORE


class AssetEntryTest(unittest.TestCase):
    setUp = fixtures.DiscoveryTest.setUp
    accept = fixtures.DiscoveryTest.accept
    reference_source = fixtures.DiscoveryTest.reference_source

    def call(self, *args, status=0):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = work.main(list(args), root=self.harness)
        self.assertEqual(status, result, stderr.getvalue())
        return json.loads(stdout.getvalue()) if status == 0 else stderr.getvalue()

    def references(self):
        directory, metadata = self.reference_source()
        recipe = {key: value for key, value in metadata.items() if key != 'entry'}
        recipe['source_ref'] = 'card-recipe'
        (directory / 'recipe.md').write_text('---\n' + json.dumps(recipe) + '\n---\n# Recipe\n')
        return directory, metadata

    def files(self):
        return {str(p): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob('*') if p.is_file()}

    def module(self, identity, version=1):
        source = self.root / f'{identity}-{version}'
        source.mkdir()
        (source/'asset.json').write_text(json.dumps({'schema_version':1,'id':identity,'version':version,
                                                    'kind':'module','entry':'main.js'}))
        (source/'main.js').write_text('window.fixture = 1;')
        packed = STORE.pack_source(self.store,source)
        STORE.accept_component(self.store,packed['component_ref'],packed['package_sha256'],
                               'Synthetic module',runtime_root=self.harness)
        return packed['component_ref']

    def test_explicit_types_and_overlapping_sources(self):
        directory, _ = self.references()
        child = directory / 'nested'
        child.mkdir()
        for name in ('manifest.json', 'index.html'):
            shutil.move(directory / name, child / name)
        STORE.register_source(self.store, child)
        for kind in ('scene-source', 'recipe'):
            rows = self.call('component', 'list', '--kind', kind, '--audit', '--json')['assets']
            self.assertEqual(1, len(rows))
            self.assertEqual(kind, rows[0]['asset_type'])
        self.assertFalse(self.call('component', 'list', '--audit', '--json')['assets'])
        self.assertFalse(self.call('component', 'list', '--kind', 'recipe', '--tag', 'missing', '--audit', '--json')['assets'])
        self.assertFalse(self.call('component', 'list', '--kind', 'recipe', '--asset-layer', 'content', '--audit', '--json')['assets'])

    def test_three_kinds_roundtrip_and_details_do_not_write(self):
        self.references()
        self.accept()
        rows = self.call('component', 'list', '--include-references', '--audit', '--json')['assets']
        before = self.files()
        seen = set()
        with patch.object(STORE, '_atomic_json', side_effect=AssertionError('detail wrote cache')), \
             patch.object(work, 'write_json', side_effect=AssertionError('detail wrote report')):
            for row in rows:
                card = self.call(*row['detail']['argv'], '--json')
                self.assertEqual(row['path'], card['path'])
                self.assertEqual(row['component_ref'], card['component_ref'])
                self.assertIn('check_scope', card)
                self.assertIn('next_step', card)
                seen.add(card['asset_type'])
            scene = self.call('component', 'interface', 'card-family-v1', '--json')
            self.assertEqual('derive-reference', scene['next_step']['action'])
            recipe = self.call('component', 'interface', 'card-recipe', '--json')
            self.assertIsNone(recipe['entry'])
            self.assertEqual('reference-only', recipe['next_step']['action'])
        self.assertEqual({'component', 'scene-source', 'recipe'}, seen)
        self.assertEqual(before, self.files())

    def test_reference_collisions_require_exact_path_without_changing_install(self):
        directory, metadata = self.reference_source()
        other = directory / 'other'
        other.mkdir()
        (other / 'manifest.json').write_text(json.dumps(metadata))
        (other / 'index.html').write_text('<main>second</main>')
        error = self.call('component', 'interface', metadata['source_ref'], status=2)
        self.assertIn('Ambiguous', error)
        self.assertIn(str(other / 'manifest.json'), error)
        card = self.call('component', 'interface', str(other / 'manifest.json'), '--json')
        self.assertEqual(str(other), card['source_directory'])
        self.accept()
        metadata['source_ref'] = self.ref
        (other / 'manifest.json').write_text(json.dumps(metadata))
        self.assertIn('Ambiguous', self.call('component', 'interface', self.ref, status=2))
        self.assertTrue(STORE.resolve_component(self.harness, self.ref)[0].is_relative_to(self.store / 'packages'))

    def test_long_catalog_and_audit_retain_identity_without_reports(self):
        directory, metadata = self.reference_source()
        for i in range(28):
            child = directory / f'item-{i}'
            child.mkdir()
            (child / 'manifest.json').write_text(json.dumps({**metadata, 'source_ref':f'item-{i}', 'purpose':'Long purpose ' * 50}))
            (child / 'index.html').write_text('<main>fixture</main>')
        before = self.files()
        with patch.object(STORE, '_atomic_json', side_effect=AssertionError('audit wrote cache')), \
             patch.object(work, 'write_json', side_effect=AssertionError('audit wrote report')):
            compact = self.call('component', 'list', '--kind', 'scene-source', '--audit')
            full = self.call('component', 'list', '--kind', 'scene-source', '--audit', '--json')
        self.assertEqual(29, compact['total'])
        self.assertEqual(len(compact['assets']), compact['shown'])
        self.assertEqual(compact['shown'] < compact['total'], compact['truncated'])
        self.assertIn('--json', compact['full_result'])
        for row in compact['assets']:
            original = next(r for r in full['assets'] if r['path'] == row['path'])
            for field in ('component_ref', 'asset_type', 'status', 'detail', 'next_step'):
                self.assertEqual(original[field], row[field])
        self.assertEqual(before, self.files())

    def test_candidate_details_never_promote_and_accepted_status_wins(self):
        candidate = STORE.import_component(self.store, self.source)
        path = Path(candidate['path']) / 'package'
        card = self.call('component', 'interface', str(path), '--candidate', '--json')
        self.assertFalse(card['installable'])
        self.assertEqual('candidate', card['next_step']['action'])
        with self.assertRaises(STORE.ComponentError):
            STORE.resolve_component(self.harness, self.ref)
        self.accept()
        card = self.call('component', 'interface', self.ref, '--json')
        self.assertEqual('accepted', card['status'])
        self.assertEqual('accepted', card['lifecycle'])
        self.assertTrue(card['installable'])
        self.assertIn('interface', card)
        self.assertIn('acceptance', card)

    def test_broken_reference_paths_fail_with_diagnostics(self):
        directory, metadata = self.reference_source()
        (directory / 'index.html').unlink()
        message = self.call('component', 'interface', str(directory / 'manifest.json'), status=2)
        self.assertIn('missing_reference_file', message)
        metadata['entry'] = '../outside.html'
        (directory / 'manifest.json').write_text(json.dumps(metadata))
        message = self.call('component', 'interface', str(directory / 'manifest.json'), status=2)
        self.assertIn('unsafe_reference_path', message)

    def test_accepted_package_candidate_view_roundtrips_without_writes(self):
        source = self.root / 'long-module'
        source.mkdir()
        usage = 'Synthetic usage. ' * 300
        (source / 'asset.json').write_text(json.dumps({
            'schema_version': 1, 'id': 'long-module', 'version': 1,
            'kind': 'module', 'entry': 'main.js', 'usage': 'USAGE.md',
        }))
        (source / 'main.js').write_text('window.fixture = 1;')
        (source / 'USAGE.md').write_text(usage)
        packed = STORE.pack_source(self.store, source)
        ref = packed['component_ref']
        STORE.accept_component(self.store, ref, packed['package_sha256'],
                               'Synthetic module', runtime_root=self.harness)
        accepted = self.call('component', 'interface', ref, '--json')
        before = self.files()
        with patch.object(STORE, '_atomic_json', side_effect=AssertionError('detail wrote state')), \
             patch.object(work, 'write_json', side_effect=AssertionError('detail wrote report')):
            compact = self.call(*accepted['detail']['argv'], '--candidate')
            self.assertIn('--candidate', compact['detail']['argv'])
            self.assertEqual([*compact['detail']['argv'], '--json'], compact['full_result'])
            for argv in (compact['detail']['argv'], compact['full_result']):
                card = self.call(*argv)
                for key in ('component_ref', 'package_sha256', 'path', 'origin',
                            'status', 'lifecycle', 'acceptance', 'installable', 'next_step', 'detail'):
                    self.assertEqual(compact[key], card[key], key)
                self.assertEqual('candidate', card['status'])
                self.assertFalse(card['installable'])
                self.assertIsNone(card['acceptance'])
            self.assertEqual(usage, self.call(*compact['full_result'])['interface']['usage'])
            self.assertEqual(accepted, self.call('component', 'interface', ref, '--json'))
        self.assertEqual(before, self.files())

    def test_ratio_fallback_requires_evidence_and_does_not_expand_declarations(self):
        source = self.root / 'module-source'
        source.mkdir()
        STORE.register_source(self.store, source)
        metadata = {'schema_version':1, 'id':'ratio-fixture', 'version':1, 'kind':'module', 'entry':'main.js'}
        (source / 'asset.json').write_text(json.dumps(metadata))
        (source / 'main.js').write_text('window.fixture = 1;')
        packed = STORE.pack_source(self.store, source)
        ref = packed['component_ref']
        STORE.accept_component(self.store, ref, packed['package_sha256'], 'Synthetic module', runtime_root=self.harness)
        selection = self.store / 'selection.json'
        selection.write_text(json.dumps({ref:{'ratios':['9:16'], 'ratios_basis':'Synthetic review fixture at 1080x1920'}}))
        rows = self.call('component','list','--ratio','9:16','--audit','--json')['assets']
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual('selection', row['ratio_source']['kind'])
        card = self.call('component','interface',ref,'--json')
        self.assertEqual(['9:16'],card['ratios'])
        self.assertIn('1080x1920',card['ratio_source']['evidence'])
        selection.write_text(json.dumps({ref:{'ratios':['9:16']}}))
        self.assertFalse(self.call('component','list','--ratio','9:16','--audit','--json')['assets'])
        self.assertTrue(self.call('component','list','--ratio','unknown','--audit','--json')['assets'])
        self.assertTrue(STORE.resolve_component(self.harness,ref)[0].is_dir())
        metadata['compatibility'] = {'ratios':['16:9']}
        (source / 'asset.json').write_text(json.dumps(metadata))
        selection.write_text(json.dumps({ref:{'ratios':['9:16'], 'ratios_basis':'Synthetic alternative'}}))
        card = self.call('component','interface',str(source),'--candidate','--json')
        self.assertEqual(['16:9'],card['ratios'])
        self.assertEqual('source',card['ratio_source']['kind'])
        report = self.call('component','list','--audit','--json')
        self.assertIn('conflicting_selection_ratios',[r['code'] for r in report['warnings']])

    def test_audit_classifies_approval_content_not_directory_names(self):
        directory, metadata = self.reference_source()
        for name, approval in (
            ('tests',{'component_ref':'test@v1','package_sha256':'a'*64,'status':'accepted'}),
            ('source-approval',{'source_ref':'missing-scene','status':'approved'}),
            ('unknown-approval',{}),
        ):
            child = directory/name
            child.mkdir()
            (child/'ACCEPTANCE.json').write_text(json.dumps(approval))
        broken = directory/'tests'/'real-scene'
        broken.mkdir()
        (broken/'manifest.json').write_text(json.dumps({'source_ref':'incomplete'}))
        report = self.call('component','list','--audit','--json')
        warnings = report['warnings']
        missing = {r['path'] for r in warnings if r['code']=='missing_discovery_fields'}
        self.assertEqual({str(directory/'source-approval'/'manifest.json'),str(broken/'manifest.json')},missing)
        self.assertTrue(any(r['code']=='unknown_source_approval' and 'unknown-approval' in r['path'] for r in warnings))

    def test_attachment_escape_and_long_detail(self):
        directory, metadata = self.reference_source()
        metadata['usage'] = 'usage.md'
        (directory/'manifest.json').write_text(json.dumps(metadata))
        (directory/'usage.md').write_text('# Usage\n'+'Long fixture description. '*300)
        before = self.files()
        compact = self.call('component','interface',metadata['source_ref'])
        self.assertIn('full_result',compact)
        full = self.call(*compact['full_result'])
        self.assertEqual((directory/'usage.md').read_text(),full['interface']['usage'])
        self.assertEqual(before,self.files())
        (directory/'usage.md').unlink()
        outside = self.root/'private.md'
        outside.write_text('DO_NOT_EXPOSE')
        (directory/'usage.md').symlink_to(outside)
        error = self.call('component','interface',metadata['source_ref'],status=2)
        self.assertIn('escapes',error)
        self.assertNotIn('DO_NOT_EXPOSE',error)

    def test_package_kind_cannot_impersonate_a_reference(self):
        source = self.root/'spoofed'
        source.mkdir()
        STORE.register_source(self.store,source)
        for kind in ('scene-source','recipe'):
            with self.subTest(kind=kind):
                (source/'asset.json').write_text(json.dumps({'id':'spoofed','version':1,
                                                           'kind':kind,'entry':'../../outside.html'}))
                report = self.call('component','list','--include-references','--audit','--json')
                self.assertFalse(report['assets'])
                self.assertTrue(report['errors'])
                message = self.call('component','interface',str(source),status=2)
                self.assertIn('Unsupported asset kind',message)

    def test_truncation_cannot_hide_identity_conflicts(self):
        for i in range(21):
            self.module(f'normal-{i}')
        self.accept()
        hashes = self.store/'candidates'/STORE._relative(self.ref)/'package/HASHES.json'
        data = json.loads(hashes.read_text())
        data['package_sha256'] = '0'*64
        hashes.write_text(json.dumps(data))
        compact = self.call('component','list','--audit')
        self.assertTrue(compact['truncated'])
        self.assertNotIn(self.ref,[r['component_ref'] for r in compact['assets']])
        self.assertEqual(1,compact['conflicts_total'])
        self.assertEqual(self.ref,compact['conflicts'][0]['component_ref'])
        with self.assertRaisesRegex(STORE.ComponentError,'Conflicting'):
            STORE.resolve_component(self.harness,self.ref)

    def test_exact_versions_and_reference_classification_remain_distinct(self):
        refs = [self.module('versioned',v) for v in (1,2)]
        for ref in refs:
            card = self.call('component','interface',ref,'--json')
            self.assertEqual(ref,card['component_ref'])
        self.call('component','interface','versioned',status=2)
        selection = self.store/'selection.json'
        selection.write_text(json.dumps({refs[0]:{'asset_layer':'reference'}}))
        card = self.call('component','interface',refs[0],'--json')
        self.assertEqual('accepted',card['status'])
        self.assertFalse(card['installable'])
        self.assertEqual('reference-only',card['next_step']['action'])
        with self.assertRaisesRegex(STORE.ComponentError,'Reference assets'):
            STORE.resolve_component(self.harness,refs[0])
        selection.write_text(json.dumps({refs[0]:{'asset_layer':'invalid'}}))
        card = self.call('component','interface',refs[0],'--json')
        self.assertFalse(card['installable'])
        self.assertEqual('blocked',card['next_step']['action'])


if __name__ == '__main__':
    unittest.main()
