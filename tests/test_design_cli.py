"""User card CLI and offline card asset installation regression."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import work
import component_harness
import designs
import design_snapshot


def _git(cwd, *args):
    subprocess.run(['git', '-c', 'user.email=t@x', '-c', 'user.name=t', *args], cwd=cwd, check=True,
                   capture_output=True)


class DesignCliTest(unittest.TestCase):
    def test_user_card_authoring_install_and_offline_verify(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root, cards = base / 'tool', base / 'cards'
            (root / '.studio/.runtime').mkdir(parents=True)
            config = root / '.studio/.runtime/assets.json'
            config.write_text(json.dumps({'design_root': str(cards)}))
            with patch.dict(os.environ, {'HYPERFRAMES_AI_CONFIG': '', 'HYPERFRAMES_AI_ASSET_CONFIG': str(config),
                                        'HYPERFRAMES_AI_RESOLVED_CONFIG': '', 'HYPERFRAMES_AI_HOME': '',
                                        'HYPERFRAMES_AI_REVIEW': '0'}):
                def call(*args, status=0):
                    output, errors = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                        self.assertEqual(status, work.main(['--json', *args], root=root), errors.getvalue())
                    return json.loads(output.getvalue()) if status == 0 else errors.getvalue()
                call('design', 'new', 'owner')
                call('design', 'new', 'kit', '--type', 'material')
                asset = cards / 'kit/assets/marker'
                asset.mkdir()
                (asset / 'asset.json').write_text(json.dumps({'schema_version': 1, 'id': 'marker', 'version': 1,
                                                           'kind': 'module', 'entry': 'main.js'}))
                (asset / 'main.js').write_text('window.fixture = 1;')
                declaration = cards / 'owner/design.json'
                data = json.loads(declaration.read_text()); data['references'] = ['kit/marker']
                declaration.write_text(json.dumps(data))
                call('design', 'localize', 'owner', 'kit/marker')
                self.assertFalse(call('design', 'compare', 'owner')['marker']['source_changed'])
                self.assertTrue(call('design', 'validate', 'owner')['ok'])
                rows = call('design', 'list')
                self.assertEqual('material', next(row for row in rows if row['id'] == 'kit')['type'])
                self.assertEqual('localized', next(row for row in rows if row['id'] == 'owner')['assets'][0]['state'])
                project = cards / 'owner/example'
                (project / 'index.html').write_text('<html><body>Fixture<script src="vendor/components/owner/marker/v1/main.js"></script></body></html>')
                binding = base / 'binding.json'
                binding.write_text(json.dumps({'schema_version': 3, 'component_ref': 'owner/marker', 'scene': 'one',
                                               'usage': {'role': 'auxiliary', 'required': True}}))
                self.assertIn('identity', call('component', 'install', 'owner/marker', '--source', 'kit/marker',
                                              '--project', str(project), '--binding-file', str(binding), status=2))
                call('component', 'install', 'owner/marker', '--project', str(project), '--binding-file', str(binding))
                lock = json.loads((project / 'COMPONENT_LOCK.json').read_text())['components'][0]
                self.assertEqual('owner/marker', lock['card_ref'])
                self.assertNotIn('acceptance', lock)
                shutil.rmtree(cards / 'owner/assets')
                shutil.rmtree(cards / 'kit')
                self.assertTrue(component_harness.verify_installation(project))
                (project / lock['vendor_path'] / 'main.js').write_text('tampered')
                with self.assertRaises(component_harness.ComponentError):
                    component_harness.verify_installation(project)

    def test_card_appearance_has_no_store_dependency(self):
        import asset_store
        import appearance
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            card = root / '.studio/designs/palette'
            (card / 'assets').mkdir(parents=True)
            (card / 'design.json').write_text(json.dumps({'id': 'palette', 'version': 1, 'type': 'material',
                                                        'assets': {'directory': 'assets'}, 'runtime': {}}))
            payloads = {'theme': {'tokens': {'colors': {'text': '#121212'}}},
                        'background': {'renderer': 'solid', 'parameters': {'color': '#ffffff'}}}
            for kind, payload in payloads.items():
                source = card / 'assets' / kind; source.mkdir()
                (source / 'asset.json').write_text(json.dumps({'schema_version': 2, 'id': kind, 'version': 1,
                    'kind': kind, 'entry': 'preset.json', 'contract_version': 1, 'parameters': {}, 'compatibility': {}}))
                (source / 'preset.json').write_text(json.dumps(payload))
            with patch.object(asset_store, 'asset_store_root', side_effect=AssertionError('legacy store read')):
                options = work.appearance_options(root, SimpleNamespace(theme='palette/theme', background='palette/background'))
                lock = appearance.resolve(root, {}, options)
                project = root / 'project'; project.mkdir()
                appearance.materialize(root, project, lock)
                shutil.rmtree(card)
                self.assertTrue(appearance.verify(project, lock))


    def test_design_root_reports_git_state_read_only(self):
        if shutil.which('git') is None:
            self.skipTest('git unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root, cards = base / 'tool', base / 'cards'
            (root / '.studio/.runtime').mkdir(parents=True)
            config = root / '.studio/.runtime/assets.json'
            config.write_text(json.dumps({'design_root': str(cards)}))
            with patch.dict(os.environ, {'HYPERFRAMES_AI_CONFIG': '', 'HYPERFRAMES_AI_ASSET_CONFIG': str(config),
                                        'HYPERFRAMES_AI_RESOLVED_CONFIG': '', 'HYPERFRAMES_AI_HOME': '',
                                        'HYPERFRAMES_AI_REVIEW': '0'}):
                def call(*args, status=0):
                    output, errors = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                        self.assertEqual(status, work.main(['--json', *args], root=root), errors.getvalue())
                    return json.loads(output.getvalue()) if status == 0 else errors.getvalue()

                self.assertFalse(call('design', 'root')['exists'])
                call('design', 'new', 'owner')
                self.assertEqual('none', call('design', 'root')['vcs']['vcs'])
                subprocess.run(['git', 'init', '-q'], cwd=cards, check=True)
                subprocess.run(['git', '-c', 'user.email=t@x', '-c', 'user.name=t',
                                'commit', '-q', '--allow-empty', '-m', 'init'], cwd=cards, check=True)
                state = call('design', 'root')
                self.assertTrue(state['exists'])
                self.assertEqual('git', state['vcs']['vcs'])
                self.assertTrue(state['vcs']['nested'])
                self.assertTrue(state['vcs']['branch'])
                self.assertGreaterEqual(state['vcs']['untracked'], 1)
                self.assertEqual(0, state['vcs']['dirty'])
                self.assertIsNone(state['vcs']['remote'])
                subprocess.run(['git', 'add', '-A'], cwd=cards, check=True)
                subprocess.run(['git', '-c', 'user.email=t@x', '-c', 'user.name=t',
                                'commit', '-q', '-m', 'cards'], cwd=cards, check=True)
                self.assertEqual(0, call('design', 'root')['vcs']['untracked'])
                self.assertIn('owner', [card['id'] for card in call('design', 'list')])


    def test_compare_since_reports_changed_files_and_version_bump(self):
        if shutil.which('git') is None:
            self.skipTest('git unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root, cards = base / 'tool', base / 'cards'
            (root / '.studio/.runtime').mkdir(parents=True)
            config = root / '.studio/.runtime/assets.json'
            config.write_text(json.dumps({'design_root': str(cards)}))
            with patch.dict(os.environ, {'HYPERFRAMES_AI_CONFIG': '', 'HYPERFRAMES_AI_ASSET_CONFIG': str(config),
                                        'HYPERFRAMES_AI_RESOLVED_CONFIG': '', 'HYPERFRAMES_AI_HOME': '',
                                        'HYPERFRAMES_AI_REVIEW': '0'}):
                def call(*args, status=0):
                    output, errors = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                        self.assertEqual(status, work.main(['--json', *args], root=root), errors.getvalue())
                    return json.loads(output.getvalue()) if status == 0 else errors.getvalue()

                def git(*args):
                    subprocess.run(['git', '-c', 'user.email=t@x', '-c', 'user.name=t', *args],
                                   cwd=cards, check=True, capture_output=True)
                call('design', 'new', 'owner')
                self.assertIn('not a Git working tree', call('design', 'compare', 'owner', '--since', 'HEAD', status=2))
                git('init', '-q')
                git('add', '-A')
                git('commit', '-q', '-m', 'cards')
                self.assertIn('CHANGELOG.md', ' '.join(call('design', 'validate', 'owner')['cards']['owner']['warnings']))
                (cards / 'owner/GUIDE.md').write_text('changed guide')
                report = call('design', 'compare', 'owner', '--since', 'HEAD')
                self.assertIn('owner/GUIDE.md', [item['path'] for item in report['files']])
                self.assertFalse(report['version']['bumped'])
                self.assertTrue(report['warning'])
                self.assertFalse(report['changelog'])
                declaration = cards / 'owner/design.json'
                data = json.loads(declaration.read_text())
                data['version'] = int(data['version']) + 1
                declaration.write_text(json.dumps(data))
                (cards / 'owner/CHANGELOG.md').write_text('- v2: changed guide\n')
                report = call('design', 'compare', 'owner', '--since', 'HEAD')
                self.assertTrue(report['version']['bumped'])
                self.assertIsNone(report['warning'])
                self.assertTrue(report['changelog'])
                self.assertNotIn('CHANGELOG.md', ' '.join(call('design', 'validate', 'owner')['cards']['owner']['warnings']))
                self.assertIn('cannot combine', call('design', 'compare', 'owner', 'x', '--since', 'HEAD', status=2))



class DesignRootRepoTest(unittest.TestCase):
    def setUp(self):
        if shutil.which('git') is None:
            self.skipTest('git unavailable')

    def test_catalog_validate_and_snapshot_ignore_study_notes_in_a_git_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root, cards = base / 'tool', base / 'cards'
            (root / '.studio/.runtime').mkdir(parents=True)
            config = root / '.studio/.runtime/assets.json'
            config.write_text(json.dumps({'design_root': str(cards)}))
            env = {'HYPERFRAMES_AI_CONFIG': '', 'HYPERFRAMES_AI_ASSET_CONFIG': str(config),
                   'HYPERFRAMES_AI_RESOLVED_CONFIG': '', 'HYPERFRAMES_AI_HOME': '', 'HYPERFRAMES_AI_REVIEW': '0'}
            with patch.dict(os.environ, env):
                def call(*args):
                    output, errors = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                        self.assertEqual(0, work.main(['--json', *args], root=root), errors.getvalue())
                    return json.loads(output.getvalue())
                call('design', 'new', 'owner')
                # Research notes live next to the cards but are not cards.
                (cards / 'studies/reference-video').mkdir(parents=True)
                (cards / 'studies/reference-video/notes.md').write_text('mechanism breakdown')
                (cards / 'owner/study').mkdir()
                (cards / 'owner/study/palette.md').write_text('palette study')
                _git(cards, 'init', '-q')
                _git(cards, 'add', '-A')
                _git(cards, 'commit', '-q', '-m', 'cards')
                rows = call('design', 'list')
                self.assertEqual(['owner'], [row['id'] for row in rows if row.get('origin') == 'user'])
                self.assertFalse([row for row in rows if row.get('error')])
                self.assertTrue(call('design', 'validate', 'owner')['ok'])
                state = call('design', 'root')
                self.assertEqual('git', state['vcs']['vcs'])
                self.assertEqual(0, state['vcs']['dirty'])
                # Snapshot content comes from the working tree, even when it is uncommitted (REQ-008).
                (cards / 'owner/GUIDE.md').write_text('uncommitted guide edit')
                (cards / 'owner/study/palette.md').write_text('more notes')
                receipt, sources = design_snapshot.inventory('owner')
                self.assertIn('card/GUIDE.md', receipt['files'])
                self.assertFalse([name for name in receipt['files'] if name.startswith('card/study/')])
                self.assertEqual('uncommitted guide edit', sources['card/GUIDE.md'].read_text())
                self.assertEqual(2, call('design', 'root')['vcs']['dirty'])  # GUIDE.md and the tracked study note


if __name__ == '__main__':
    unittest.main()
