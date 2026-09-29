import json
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.studio'))
import asset_contract
import asset_store
import component_harness
import math_chain
import math_kit
import math_kit_assets
import visual_plan


def plan_for(items, characters='x=0123456789total', **font):
    intent = {'units': [{'id': item['id'], 'symbol': 'x', 'graphic': 'square'} for item in items],
              'symbols': {'x': 'square'}, 'invariants': ['fixed slots'],
              'zero_basics': [{'relation': 'equal units', 'action': 'show units'}],
              'cues': [{'cue': 'x', 'keep': [], 'reveal': [i['id'] for i in items], 'remove': []}]}
    block = {'font': {'path': 'assets/font.ttf', 'sha256': 'a' * 64, 'characters': characters, **font},
             'items': items}
    return ('---\n{"plan_format":"3.5.2","series_binding":{"spec":"math-rap"}}\n---\n## S01\n'
            + '```math-plan\n' + json.dumps(intent) + '\n```\n'
            + '```math\n' + json.dumps(block) + '\n```\n')


class MathKitTest(unittest.TestCase):
    def setUp(self):
        self.item = {'id': 'U1', 'kind': 'unknown', 'box': [100, 100, 160, 160], 'label': 'x'}

    def test_all_primitives_and_plan_events_have_one_source(self):
        variants = [('formula', {'slots': ['x', '', '=', '2']}),
                    ('unknown', {'label': 'x'}),
                    ('units', {'count': 3, 'value': '2', 'label': 'total 6'}),
                    ('segment', {'count': 3, 'value': '2', 'label': 'total 6'}),
                    ('area', {'value': '4', 'label': 'total 4'}),
                    ('number-line', {'min': 0, 'max': 2, 'step': 1, 'labels': ['0', '1', '2']}),
                    ('strike', {'label': 'x', 'negate': True}),
                    ('edge', {'from': [100, 100], 'to': [300, 300], 'length': 100, 'duration': 1, 'label': 'x'}),
                    ('equals', {'to': [300, 300], 'duration': 1})]
        items = [dict(id=f'U{i}', kind=kind, box=[100, 100, 160, 160], **fields)
                 for i, (kind, fields) in enumerate(variants)]
        plan = plan_for(items, characters='x=0123456789total ')
        for ratio in ('16:9', '9:16'):
            self.assertEqual(items, math_kit.parse_plan(plan, ratio)['S01']['items'])
        row = visual_plan.plan_scene_rows(plan)['S01']
        self.assertEqual(16, len(row['events']))
        self.assertTrue(all(event['derived'] and event['cue'] == 'x' for event in row['events']))
        self.assertEqual(items, row['math']['items'])

    def test_invalid_contracts_rejected(self):
        cases = [dict(self.item, box=[0, 0, -1, 4]), dict(self.item, box=[1000, 100, 160, 160]),
                 dict(self.item, box=[1, 1, 100, 110]), dict(self.item, label='missing'),
                 dict(self.item, cue='second truth'), dict(self.item, id='bad id'),
                 dict(self.item, box=[True, 100, 160, 160]), dict(self.item, kind='unimplemented')]
        for item in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                math_kit.parse_plan(plan_for([item]), '9:16')
        for path in ('../font.ttf', '/tmp/font.ttf', 'https://font.ttf', 'a\\font.ttf', 'a/./font.ttf'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                math_kit.parse_plan(plan_for([self.item], path=path))
        for replacement in ('"id": "U2"', '"id": "U1", "extra": true'):
            plan = plan_for([self.item]).replace('"id": "U1"', replacement, 1)
            with self.assertRaises(ValueError):
                math_kit.parse_plan(plan)

    def test_fences_and_legacy_plan_are_not_misparsed(self):
        plan = plan_for([self.item])
        self.assertEqual({}, math_kit.parse_plan('## S01\nNo mathematics\n'))
        self.assertEqual({'S01'}, set(math_chain.parse_plan(plan)))
        with self.assertRaises(ValueError):
            math_kit.parse_plan(plan + '```math\n{}\n```\n')
        with self.assertRaises(ValueError):
            math_kit.parse_plan(plan.rsplit('```', 1)[0])
        with self.assertRaises(visual_plan.VisualPlanError):
            visual_plan.plan_scene_rows(plan.replace('math-rap', 'other'))

    def test_export_pack_exact_accept_and_offline_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, store, project = (root / name for name in ('source', 'store', 'project'))
            exported = math_kit_assets.export_math_kit(REPO, source)
            self.assertEqual(exported, math_kit_assets.export_math_kit(REPO, source))
            candidate = asset_store.pack_source(store, source)
            asset_contract.validate_asset(Path(candidate['path']) / 'package', expected_ref='math-kit@v1')
            with self.assertRaises(component_harness.ComponentError):
                asset_store.accept_component(store, 'math-kit@v1', '0' * 64, 'Wrong test hash', runtime_root=REPO)
            accepted = asset_store.accept_component(store, 'math-kit@v1', candidate['package_sha256'],
                                                     'Isolated math module fixture only', runtime_root=REPO)
            project.mkdir()
            component_harness.install_component(store / 'packages/math-kit/v1', project,
                {'schema_version': 3, 'component_ref': 'math-kit@v1', 'scene': 'S01',
                 'usage': {'role': 'subject', 'required': True}}, acceptance=accepted)
            (project / 'index.html').write_text('<link rel="stylesheet" href="vendor/components/math-kit/v1/math-kit.css">'
                '<script src="vendor/components/math-kit/v1/math-kit.js"></script>', encoding='utf-8')
            import shutil
            shutil.rmtree(store)
            component_harness.verify_installation(project, public_root=REPO)
            (source / 'math-kit.js').write_text('manual source edit', encoding='utf-8')
            with self.assertRaises(component_harness.ComponentError):
                math_kit_assets.export_math_kit(REPO, source)
            self.assertEqual('manual source edit', (source / 'math-kit.js').read_text())


if __name__ == '__main__':
    unittest.main()
