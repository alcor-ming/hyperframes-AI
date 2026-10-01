"""Isolated CLI ownership and generated-preview integration."""
import json
import shutil
import unittest
from unittest.mock import patch

import test_work_appearance as fixture
from test_math_kit import plan_for
import math_build
from visual_plan import VisualPlanError

cli = fixture.cli


class MathCliTest(unittest.TestCase):
    asset = fixture.WorkAppearanceTest.asset
    invoke = fixture.WorkAppearanceTest.invoke

    def setUp(self):
        fixture.WorkAppearanceTest.setUp(self)
        shutil.copyfile(fixture.REPO / 'windows-runtime.lock.json', self.root / 'windows-runtime.lock.json')
        shutil.copytree(fixture.REPO / '.studio/runtime', self.root / '.studio/runtime')
        (self.root / '.studio/spec').mkdir()
        shutil.copyfile(fixture.REPO / '.studio/spec/math-kit.md', self.root / '.studio/spec/math-kit.md')
        cli.account_service(self.root).put('series', 'fixture', {'name': 'Math', 'mode': 'explainer', 'spec': 'math-rap'})
        self.identity = self.invoke('new', 'Math', '--workflow', 'hyperframes_video', '--account', 'a')
        work, _ = cli.locate_work(self.root, self.identity)
        self.variant = work / 'variants/main'
        self.project = self.variant / 'project'
        self.plan = self.variant / 'ANIMATION_PLAN.md'
        self.metadata = cli.read_frontmatter(self.plan)
        self.metadata['status'] = 'approved'
        font = self.project / 'assets/font.ttf'
        font.parent.mkdir(exist_ok=True)
        font.write_bytes(b'font fixture; browser is separately tested')
        body = plan_for([{'id': 'U1', 'kind': 'unknown', 'box': [100, 100, 160, 160], 'label': 'x'}],
                        sha256=cli.file_sha256(font)).split('## S01', 1)[1]
        self.plan.write_text('---\n' + json.dumps(self.metadata) + '\n---\n## S01\nmath-kit@v1\n' + body)
        (self.project / 'index.html').write_text('<html><body><section id="S01" data-start="0" data-duration="5">Keep</section></body></html>')
        (self.project / 'DESIGN.md').write_text('Isolated mathematical fixture')
        cli.write_json(self.project / 'runtime/cues.json', {'schema_version': 1, 'text': 'x',
            'characters': [{'char': 'x', 'aligned': True, 'start': 1, 'end': 2}]})
        source = self.base / 'math-source'
        self.invoke('component', 'math-kit-source', str(source))
        candidate = json.loads(self.invoke('component', 'pack', str(source)))
        self.invoke('component', 'accept', 'math-kit@v1', '--sha256', candidate['package_sha256'], '--note', 'Isolated CLI fixture')
        binding = self.base / 'binding.json'
        cli.write_json(binding, {'schema_version': 3, 'component_ref': 'math-kit@v1', 'scene': 'S01',
                                'usage': {'role': 'subject', 'required': True}})
        self.scoped('component', 'install', 'math-kit@v1', '--binding-file', str(binding))

    def scoped(self, *args):
        return self.invoke('--work', self.identity, '--variant', 'main', *args)

    def test_cli_build_snapshot_and_preview_consistency(self):
        with patch.object(math_build, 'check_geometry'):
            self.assertEqual(1, json.loads(self.scoped('math', 'build'))['items'])
        plan = self.plan.read_text()
        cli.validate_project_cards(self.project, plan, cli.snapshot_items(self.project))
        snapshot = self.base / 'snapshot'
        cli.copy_snapshot(self.project, snapshot)
        cli.validate_snapshot_closure(self.project, snapshot)
        math_build.verify_generated(snapshot, plan)
        self.assertEqual((self.project / 'assets/font.ttf').read_bytes(), (snapshot / 'assets/font.ttf').read_bytes())
        with self.assertRaisesRegex(VisualPlanError, 'differs from Plan'):
            cli.validate_project_cards(self.project, plan.replace('"label": "x"', '"label": "xx"'), [])
        with self.assertRaisesRegex(cli.HarnessError, 'explicit'):
            self.invoke('math', 'build')
        self.plan.write_text(plan.replace('"status": "approved"', '"status": "draft"'))
        with self.assertRaisesRegex(cli.HarnessError, 'approved'):
            self.scoped('math', 'build')


if __name__ == '__main__':
    unittest.main()
