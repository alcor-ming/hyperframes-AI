"""Synthetic vocabulary, trustworthy timing and deliberate recall pauses."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import english_plan
from visual_plan import VisualPlanError, plan_scene_rows


def lesson():
    return {'words': [{'word': 'cat', 'sense': '猫（动物）', 'spelling': 'cat',
                      'pronunciation': {'source': 'Synthetic pronunciation reference', 'language': 'en-US'},
                      'example': {'text': 'My cat is my boss.', 'meaning': '我的猫是我的老板。', 'fictional': True}}],
            'cues': [{'word': 'cat', 'cue': 'cat', 'target': 'I01', 'action': 'pronounce'}],
            'recall': [{'word': 'cat', 'task': 'spelling', 'prompt': 'Recall spelling', 'answer': 'cat',
                        'target': 'I01', 'start_cue': '试', 'end_cue': '答'}]}


def plan(value=None):
    return ('---\n{"plan_format":"3.7.0","mode":"english","line":{"id":"english","version":1}}\n---\n'
            '## S01\n```english-plan\n' + json.dumps(value if value is not None else lesson()) + '\n```\n'
            '### I01 · P001\n```screen\ncat\n猫\n```\n')


def cues():
    text = 'cat试答'
    return {'schema_version': 1, 'text': text,
            'characters': [{'char': char, 'aligned': True, 'start': i, 'end': i + .5}
                           for i, char in enumerate(text)], 'speech_intervals': [[0, 4.5]]}


class EnglishPlanTest(unittest.TestCase):
    def test_lesson_projects_without_storyboard_and_preserves_recall_pause(self):
        text = plan()
        row = plan_scene_rows(text)['S01']
        self.assertEqual([], row['segments'])
        self.assertEqual(['english_pronounce', 'english_hide', 'english_answer'],
                         [event['change'] for event in row['events']])
        self.assertEqual('pause', row['exceptions'][0]['kind'])
        self.assertEqual([], english_plan.check(text, cues(), [{'id': 'S01', 'start': 0, 'duration': 5}]))
        self.assertEqual('english_timing_unverified', english_plan.check(text)[0]['code'])

    def test_blank_spelling_source_and_mnemonic_cannot_claim_completion(self):
        cases = [('spelling', 'cta', 'spelling_mismatch'), ('sense', '<sense>', 'invalid_english_word'),
                 ('pronunciation', {'source': '', 'language': 'en-US'}, 'pronunciation_source'),
                 ('mnemonic', {'kind': 'etymology', 'text': 'sounds similar'}, 'invalid_english_mnemonic')]
        for key, value, message in cases:
            data = lesson()
            data['words'][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, message):
                english_plan.parse_plan(plan(data))
        with self.assertRaisesRegex(ValueError, 'invalid_english_plan'):
            english_plan.parse_plan(plan({'words': [], 'cues': [], 'recall': []}))

    def test_declared_targets_and_recall_answers_are_checked(self):
        data = lesson()
        data['cues'][0]['target'] = 'I99'
        with self.assertRaisesRegex(VisualPlanError, 'english_unknown_screen'):
            plan_scene_rows(plan(data))
        data = lesson()
        data['recall'][0]['answer'] = 'cta'
        with self.assertRaisesRegex(ValueError, 'english_recall_spelling_mismatch'):
            english_plan.parse_plan(plan(data))
        data = lesson()
        data['recall'] = []
        with self.assertRaisesRegex(ValueError, 'english_missing_recall'):
            english_plan.parse_plan(plan(data))
        data = lesson()
        data['cues'][0]['cue'] = 'dog'
        with self.assertRaisesRegex(ValueError, 'english_pronunciation_cue_mismatch'):
            english_plan.parse_plan(plan(data))

    def test_cues_need_real_alignment_and_positive_recall_interval(self):
        data = cues()
        data['characters'][0].update(aligned=False, start=None, end=None)
        self.assertEqual('english_unresolved_cue', english_plan.check(plan(), data)[0]['code'])
        data = lesson()
        data['recall'][0]['end_cue'] = '试'
        self.assertEqual('english_recall_interval', english_plan.check(plan(data), cues())[0]['code'])
        bounds = [{'id': 'S01', 'start': 0, 'duration': 2}]
        self.assertEqual('english_unresolved_cue', english_plan.check(plan(), cues(), bounds)[0]['code'])
        data = lesson()
        data['cues'][0]['cue'] = {'token': 'cat', 'within': [0, 3]}
        self.assertEqual([], english_plan.check(plan(data), cues()))
        data['cues'][0]['cue']['within'] = [0, float('nan')]
        with self.assertRaisesRegex(ValueError, 'invalid_english_cue'):
            english_plan.parse_plan(plan(data))

    def test_later_scene_can_hold_recall_without_fixed_ab_or_word_quota(self):
        first, second = lesson(), lesson()
        first['recall'] = []
        second['cues'][0].update(action='reveal', target='I02')
        second['recall'][0]['target'] = 'I02'
        text = plan(first) + '\n## S02\n```english-plan\n' + json.dumps(second) + '\n```\n### I02 · P002\n```screen\ncat\n```\n'
        self.assertEqual({'S01', 'S02'}, set(plan_scene_rows(text)))
        second['words'][0]['sense'] = 'Different sense'
        with self.assertRaisesRegex(ValueError, 'english_word_definition_changed'):
            english_plan.parse_plan(plan(first) + '\n## S02\n```english-plan\n' + json.dumps(second) + '\n```\n')


if __name__ == '__main__':
    unittest.main()
