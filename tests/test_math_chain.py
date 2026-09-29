import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import explainer
import math_chain


def fixture():
    cues = explainer.build_cues('a!b', b'{"characters":[{"char":"a","start":0,"end":0.2},{"char":"b","start":2,"end":2.2}]}')
    cues['beat_grid'] = math_chain.make_beat_grid([0, .5, 1, 1.5, 2, 2.5, 3, 3.5], 'a' * 64, 3, 1)
    queries = [({'bar': 1, 'beat': 1}, .5), ({'bar': 2, 'beat': 3}, 3),
               ({'bar': 3, 'beat': 2}, 'beat_not_found'), ({'bar': 0, 'beat': 1}, 'invalid_beat_query'),
               ({'bar': True, 'beat': 1}, 'invalid_beat_query'), ({'bar': 1, 'beat': 4}, 'invalid_beat_query'),
               ({'bar': 1, 'beat': 1, 'token': 'a'}, 'invalid_beat_query'),
               ({'bar': 1}, 'invalid_beat_query'), ('a', 0), ('!', 'cue_unaligned')]
    return {'cues': cues, 'queries': queries}


def contract():
    return dict(units=[dict(id='u1', symbol='x', graphic='red point')], symbols={'x': 'red point'},
                invariants=['length'], zero_basics=[dict(relation='equal', action='overlay')],
                cues=[dict(cue={'bar': 2, 'beat': 3}, keep=[], reveal=['u1'], remove=[])])


def plan(value, scene='S01'):
    return f'## {scene}\n```math-plan\n{json.dumps(value)}\n```\n'


class MathChainTests(unittest.TestCase):
    def test_shared_timing_fixture(self):
        data = fixture()
        explainer.validate_cues(data['cues'])
        for query, expected in data['queries']:
            with self.subTest(query=query):
                if isinstance(expected, str):
                    with self.assertRaisesRegex(ValueError, expected):
                        explainer.find_cue(data['cues'], query)
                else:
                    self.assertEqual(expected, explainer.find_cue(data['cues'], query))
        self.assertIsNone(data['cues']['characters'][1]['start'])
        del data['cues']['beat_grid']
        with self.assertRaisesRegex(ValueError, 'missing_beat_grid'):
            explainer.find_cue(data['cues'], {'bar': 1, 'beat': 1})

    def test_grid_validation(self):
        grid = fixture()['cues']['beat_grid']
        for key, value in [('times', [0, 0]), ('times', [0, float('nan')]), ('times', [-1, 1]),
                           ('times', [False, 1]), ('times', []), ('audio_sha256', 'no'),
                           ('first_downbeat', None), ('first_downbeat', 8), ('first_downbeat', True),
                           ('beats_per_bar', 0), ('beats_per_bar', True), ('schema_version', True)]:
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, 'invalid_beat_grid'):
                math_chain.validate_beat_grid({**grid, key: value})

    def test_plan_shape_and_diagnostics(self):
        value = contract()
        self.assertEqual({'S01': value}, math_chain.parse_plan(plan(value)))
        self.assertEqual([], math_chain.plan_findings(plan(value), fixture()['cues'], 5))
        inconsistent = copy.deepcopy(value)
        inconsistent['units'].append(dict(id='u2', symbol='x', graphic='blue line'))
        self.assertIn('math_symbol_inconsistent', {v['code'] for v in math_chain.plan_findings(plan(inconsistent), fixture()['cues'], 5)})
        other = copy.deepcopy(value)
        other['units'][0]['graphic'] = ''
        other['symbols']['x'] = 'blue line'
        other['invariants'] = []
        other['zero_basics'][0]['action'] = ''
        codes = {v['code'] for v in math_chain.plan_findings(plan(value) + plan(other, 'S02'), fixture()['cues'], 5.01)}
        self.assertEqual({'math_missing_graphic', 'math_symbol_inconsistent', 'math_missing_invariants',
                          'math_missing_zero_basics', 'math_trailing_gap'}, codes)
        value['cues'][0]['reveal'] = ['unknown']
        with self.assertRaises(ValueError):
            math_chain.parse_plan(plan(value))
        for text in ('', '## S01\n', plan(contract()) + plan(contract()), '```text\n' + plan(contract()) + '```'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                math_chain.parse_plan(text)
        value = contract()
        value['cues'][0]['cue'] = '!'
        self.assertIn('math_unresolved_cue', {v['code'] for v in math_chain.plan_findings(plan(value), fixture()['cues'], 5)})
        value = contract()
        value['cues'][0].update(keep=['u1'], reveal=[])
        self.assertIn('math_trailing_gap', {v['code'] for v in math_chain.plan_findings(plan(value), fixture()['cues'], 5)})


if __name__ == '__main__':
    if '--fixture' in sys.argv:
        print(json.dumps(fixture()))
    else:
        unittest.main()
