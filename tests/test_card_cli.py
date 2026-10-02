"""Real isolated Work/AssetStore CLI flow, with only browser geometry mocked."""
import hashlib
import json
import os
import shutil
import unittest
from unittest import mock

import test_work_appearance as fixture
import card_build
from component_harness import ComponentError
from visual_plan import VisualPlanError

cli = fixture.cli
BODY = 'preset: F01\narea: full\ntitle: Heading @hello\n- Row @row\nnote: Note @note'


class CardCliTest(unittest.TestCase):
    asset = fixture.WorkAppearanceTest.asset
    invoke = fixture.WorkAppearanceTest.invoke

    def setUp(self):
        fixture.WorkAppearanceTest.setUp(self)
        cli.write_json(self.base / 'assets.json', {'asset_root': str(self.store)})
        shutil.copyfile(fixture.REPO / 'windows-runtime.lock.json', self.root / 'windows-runtime.lock.json')
        shutil.copytree(fixture.REPO / '.studio/runtime', self.root / '.studio/runtime')
        shutil.copyfile(fixture.REPO / '.studio/card_kit_check.mjs', self.root / '.studio/card_kit_check.mjs')
        (self.root / '.studio/spec').mkdir()
        shutil.copyfile(fixture.REPO / '.studio/spec/card-kit.md', self.root / '.studio/spec/card-kit.md')
        self.identity = self.invoke('new', 'Cards', '--workflow', 'hyperframes_video', '--account', 'a')
        work, _ = cli.locate_work(self.root, self.identity)
        self.variant = work / 'variants/main'
        self.project = self.variant / 'project'
        self.plan = self.variant / 'ANIMATION_PLAN.md'
        self.plan.write_text('---\n' + json.dumps({'plan_format': '3.5.2', 'status': 'approved', 'revision': 1})
                             + '\n---\n## S01\ncard-kit@v1\n```card C1 · P001\n' + BODY + '\n```\n')
        (self.project / 'index.html').write_text('<html><body><section id="S01" data-scene-id="S01" data-start="0" data-duration="10" '
                                                'style="position:absolute;width:1920px;height:1080px">'
                                                '<p>Handwriting</p></section></body></html>')
        spoken = 'hello row note'
        cli.write_json(self.project / 'runtime/cues.json', {'schema_version': 1, 'text': spoken, 'characters': [
            {'char': char, 'start': index / 3, 'end': (index + 1) / 3, 'aligned': True}
            for index, char in enumerate(spoken)]})
        self.source = self.base / 'card-source'
        self.invoke('component', 'card-kit-source', str(self.source))
        self.invoke('component', 'source-add', str(self.source))
        candidate = json.loads(self.invoke('component', 'pack', str(self.source)))
        self.invoke('component', 'accept', 'card-kit@v1', '--sha256', candidate['package_sha256'],
                    '--note', 'Synthetic CLI test')
        binding = self.base / 'binding.json'
        cli.write_json(binding, {'schema_version': 3, 'component_ref': 'card-kit@v1', 'scene': 'S01',
                                'usage': {'role': 'subject', 'required': True}})
        self.scoped('component', 'install', 'card-kit@v1', '--binding-file', str(binding))
        geometry = mock.patch.object(card_build, 'check_geometry')
        self.geometry = geometry.start()
        self.addCleanup(geometry.stop)
        self.geometry_patch = geometry

    def scoped(self, *args):
        return self.invoke('--work', self.identity, '--variant', 'main', *args)

    def snapshot(self):
        return {path.relative_to(self.variant).as_posix(): path.read_bytes()
                for path in self.variant.rglob('*') if path.is_file() and '.runtime' not in path.parts}

    def edit(self, body, digest=None):
        body_file = self.base / 'body.txt'
        body_file.write_text(body)
        return self.scoped('cards', 'edit', '--card', 'C1', '--body-file', str(body_file), '--plan-sha256',
                           digest or hashlib.sha256(self.plan.read_bytes()).hexdigest())

    def test_build_and_plan_first_edit_invalidates_acceptance(self):
        report = json.loads(self.scoped('cards', 'build'))
        self.assertEqual(1, report['cards'])
        self.geometry.assert_called_once()
        before = self.snapshot()
        self.scoped('cards', 'build')
        self.assertEqual(before, self.snapshot())
        state_path = self.variant / 'variant.yaml'
        state = cli.read_json(state_path)
        state.update(accepted_preview='draft-v001', current_final='final-v001')
        cli.write_json(state_path, state)
        self.edit(BODY.replace('Heading', 'Updated'))
        metadata = cli.read_frontmatter(self.plan)
        self.assertEqual(('draft', 2), (metadata['status'], metadata['revision']))
        state = cli.read_json(state_path)
        self.assertEqual(2, state['plan_revision'])
        self.assertIsNone(state['accepted_preview'])
        self.assertIsNone(state['current_final'])
        self.assertIn('Updated', self.plan.read_text())
        html = (self.project / 'index.html').read_text()
        self.assertIn('Updated', html)
        self.assertIn('Handwriting', html)
        self.scoped('cards', 'build')  # card defaults to direction approval off
        self.scoped('settings', 'set', 'direction_approval', 'true')
        with self.assertRaisesRegex(cli.HarnessError, 'approved'):
            self.scoped('cards', 'build')

    def test_invalid_edit_cas_and_scope_are_non_mutating(self):
        self.scoped('cards', 'build')
        before = self.snapshot()
        for body, digest in [('preset: BAD', None), (BODY, '0' * 64), (BODY.replace('@hello', '@absent'), None)]:
            with self.subTest(body=body, digest=digest), self.assertRaises(VisualPlanError):
                self.edit(body, digest)
            self.assertEqual(before, self.snapshot())
        for args in [('cards', 'build'), ('--work', self.identity, 'cards', 'build'),
                     ('--variant', 'main', 'cards', 'build')]:
            with self.subTest(args=args), self.assertRaisesRegex(cli.HarnessError, 'explicit'):
                self.invoke(*args)
        with self.assertRaises(ComponentError):
            self.invoke('cards', 'build', '--project', str(self.project), '--plan', str(self.plan))
        with self.assertRaisesRegex(cli.HarnessError, '--plan'):
            self.invoke('cards', 'build', '--project', str(self.source))
        self.assertEqual(before, self.snapshot())

    @unittest.skipUnless(os.environ.get('HF_CARD_BROWSER'), 'Set HF_CARD_BROWSER for real browser capacity validation')
    def test_real_browser_cli_build(self):
        self.geometry_patch.stop()
        with mock.patch.dict(os.environ, {'NODE_PATH': str(fixture.REPO / '.studio/remotion/node_modules')}):
            report = json.loads(self.scoped('cards', 'build', '--browser', os.environ['HF_CARD_BROWSER']))
        self.assertEqual(1, report['cards'])
        self.assertIn('data-hf-card-plan', (self.project / 'index.html').read_text())


if __name__ == '__main__':
    unittest.main()
