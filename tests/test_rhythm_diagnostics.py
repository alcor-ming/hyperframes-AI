"""Layer-specific event evidence and gap boundaries without a WorkStore."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from visual_diagnostics import rhythm_diagnostics


class RhythmTests(unittest.TestCase):
    scenes = [{'id': 'S01', 'start': 0, 'duration': 3}, {'id': 'S02', 'start': 3, 'duration': 3}]

    def event(self, at, *, kind='point', layer='overlay', visible=True, changed=True):
        candidate = dict(id=str(at), time=at, duration=.1, kind=kind, layer=layer, scene='S01', visible=visible)
        return [dict(time=max(0, at - .001), ready=True, texts=[], rhythm_candidates=[dict(candidate, signature='before')]),
                dict(time=at + .05, ready=True, texts=[], rhythm_candidates=[dict(candidate, signature='after' if changed else 'before')])]

    def gaps(self, report):
        return [(item['start'], item['end']) for item in report['findings'] if item['kind'] == 'rhythm_gap']

    def test_zero_single_boundary_and_cross_scene_gaps(self):
        report = rhythm_diagnostics([dict(time=0, ready=True)], self.scenes)
        self.assertEqual([(0, 6)], self.gaps(report))
        report = rhythm_diagnostics(self.event(1), self.scenes)
        self.assertEqual([(1, 6)], self.gaps(report))
        self.assertEqual(['S01', 'S02'], report['findings'][0]['scenes'])
        self.assertEqual([], self.gaps(rhythm_diagnostics(self.event(2) + self.event(4), self.scenes)))
        self.assertEqual([(0, 3), (3, 6)], self.gaps(rhythm_diagnostics(self.event(3), self.scenes)))

    def test_atmosphere_invisible_and_noop_are_not_events(self):
        for options in [dict(kind='idle'), dict(kind='talk'), dict(kind='pan'), dict(kind='zoom'),
                        dict(layer='background'), dict(layer='captions'), dict(visible=False), dict(changed=False)]:
            with self.subTest(options=options):
                self.assertEqual([], rhythm_diagnostics(self.event(1, **options), self.scenes)['events'])
        states = self.event(1)
        states[-1]['ready'] = False
        report = rhythm_diagnostics(states, self.scenes)
        self.assertEqual([], report['events'])
        self.assertIn('rhythm_event_not_sampled', [item['reason'] for item in report['unverified']])
        states = self.event(1, kind='state')
        for sample in states:
            sample['rhythm_candidates'][0]['state_signature'] = 'same image despite talk transform'
        self.assertEqual([], rhythm_diagnostics(states, self.scenes)['events'])

    def test_layer_four_content_is_observed_not_declared(self):
        for layer in ['text', 'captions', 'background']:
            samples = [dict(time=0, ready=True, texts=[]), dict(time=1, ready=True,
                       texts=[dict(scene='S01', selector='#a', text='changed', layer=layer)])]
            self.assertEqual(int(layer == 'text'), len(rhythm_diagnostics(samples, self.scenes)['events']))
        with patch('visual_diagnostics.plan_scene_rows', return_value={'S01': {'events': [{'cue': 1, 'layer': 2}]}}):
            self.assertEqual([], rhythm_diagnostics([dict(time=0, ready=True)], self.scenes, plan='intent')['events'])

    def test_declared_intervals_split_gaps_without_inventing_approval(self):
        rows = {'S01': {'exceptions': [{'start_cue': 'a', 'end_cue': 'b', 'kind': 'pause', 'reason': 'pause'}]},
                'S02': {'exceptions': [{'start_cue': 'c', 'end_cue': 'd', 'kind': 'talking_head', 'reason': 'host'}]}}
        with patch('visual_diagnostics.plan_scene_rows', return_value=rows), \
                patch('explainer.find_cue', side_effect=lambda cues, query: {'a': 1, 'b': 2, 'c': 3, 'd': 6}[query]):
            report = rhythm_diagnostics([dict(time=0, ready=True)], self.scenes, plan='intent', mode='talking_head')
            self.assertEqual([], self.gaps(report))
            self.assertEqual(2, len(report['declared_exceptions']))
            self.assertTrue(all(item['approval'] == 'not_inferred' for item in report['declared_exceptions']))
            report = rhythm_diagnostics([dict(time=0, ready=True)], self.scenes, plan='intent', mode='card')
            self.assertEqual([(2, 6)], self.gaps(report))
            self.assertIn('rhythm_exception_unresolved', [item['reason'] for item in report['unverified']])
            rows['S01']['exceptions'][0]['kind'] = 'anything'
            rows['S02']['exceptions'][0]['reason'] = ''
            report = rhythm_diagnostics([dict(time=0, ready=True)], self.scenes, plan='intent', mode='talking_head')
            self.assertEqual([], report['declared_exceptions'])
            self.assertEqual([(0, 6)], self.gaps(report))

    def test_no_samples_is_unverified_not_a_gap_verdict(self):
        report = rhythm_diagnostics([], self.scenes)
        self.assertEqual([], report['findings'])
        self.assertTrue(report['advisory_only'])

    def test_lay_out_requires_majority_visible_before_mapped_plan_cues(self):
        row = {'screens': {'I01': {'实际表达': 'first'}, 'I02': {'实际表达': 'second'}},
               'events': [{'layer': 4, 'cue': 'later', 'change': 'reveal I01 I02'}]}
        sample = dict(time=0, ready=True, texts=[dict(scene='S01', layer='text', text='first second')])
        with patch('visual_diagnostics.plan_scene_rows', return_value={'S01': row}), patch('explainer.find_cue', return_value=2.5):
            report = rhythm_diagnostics([sample], self.scenes, plan='intent')
            self.assertEqual(['I01', 'I02'], next(hit for hit in report['findings'] if hit['kind'] == 'suspected_lay_out_and_wait')['information_ids'])
            row['events'][0]['change'] = 'unmapped prose'
            report = rhythm_diagnostics([sample], self.scenes, plan='intent')
            self.assertFalse(any(hit['kind'] == 'suspected_lay_out_and_wait' for hit in report['findings']))


if __name__ == '__main__':
    unittest.main()
