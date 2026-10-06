"""Synthetic scene-local Plan checks; no production inputs."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from visual_plan import VisualPlanError, plan_cue, plan_scene_rows
from visual_diagnostics import plan_information, source_sections
from explainer import ExplainerError, find_cue


HEADER = '---\n{"plan_format":"3.5.2"}\n---\n'
PLAN = '''## S01
One sentence.
| cue | 层 | 目标 | 变化 |
|---|---|---|---|
| hello#1 | 3 | emphasis | highlight |
| hello#2 | 2 | | pan |
| 例外 | hello#1 | hello#2 | pause | reading |
### I01 · P001
```screen
Contact @home [today]
```
### I02 · P001
```screen
Independent text
```
## S02
**延续信息：** I01, I02
'''


class PlanV352Test(unittest.TestCase):
    def test_events_information_and_continuation(self):
        rows = plan_scene_rows(HEADER + PLAN)
        self.assertEqual(rows['S01']['screens'], rows['S02']['screens'])
        self.assertEqual('Contact @home [today]', rows['S01']['screens']['I01']['实际表达'])
        self.assertEqual({'token': 'hello', 'nth': 1}, rows['S01']['events'][0]['cue'])
        self.assertEqual(['emphasis', ''], [event['target'] for event in rows['S01']['events']])
        self.assertEqual('pause', rows['S01']['exceptions'][0]['kind'])
        information, _ = plan_information(HEADER + PLAN)
        self.assertEqual('Independent text', information['I02']['实际表达'])
        sources = source_sections('<!-- P001 -->Source narration', '', information)
        for identity in ('I01', 'I02'):
            self.assertEqual('Source narration', sources[information[identity]['信息 ID / 来源']])
        self.assertEqual(['S01'], list(plan_scene_rows(HEADER + '## S01\nMedia only.')))

    def test_invalid_version_and_scene_syntax(self):
        self.assertEqual({'token': 'hello', 'edge': 'end', 'within': [0, 2]},
                         plan_cue('{"token":"hello","edge":"end","within":[0,2]}'))
        with self.assertRaisesRegex(VisualPlanError, 'invalid cue query'):
            plan_cue('{"token":"hello","unknown":1}')
        for plan in [PLAN, HEADER.replace('3.5.2', '3.5.1') + PLAN,
                     HEADER + PLAN.replace('### I02', '### I01'),
                     HEADER + PLAN.replace('hello#1 | 3', 'hello#1 | 5'),
                     HEADER + PLAN.replace('## S02', '## S01'),
                     HEADER + PLAN.replace('### I01 · P001', '### I01 · P001\n```rhythm\n{}\n```'),
                     HEADER + PLAN.replace('I01, I02', 'I99')]:
            with self.subTest(plan=plan), self.assertRaises(VisualPlanError):
                plan_scene_rows(plan)

    def test_repeated_cues_resolve_from_formal_alignment_only(self):
        text = 'hello hello'
        cues = {'text': text, 'characters': [{'char': char, 'start': i / 10, 'end': (i + 1) / 10, 'aligned': True}
                                            for i, char in enumerate(text)]}
        events = plan_scene_rows(HEADER + PLAN)['S01']['events']
        self.assertEqual([0, .6], [find_cue(cues, event['cue']) for event in events])
        with self.assertRaisesRegex(ExplainerError, 'cue_ambiguous'):
            find_cue(cues, plan_cue('hello'))
        with self.assertRaisesRegex(ExplainerError, 'cue_not_found'):
            find_cue(cues, plan_cue('absent'))
        cues['characters'][6]['aligned'] = False
        with self.assertRaisesRegex(ExplainerError, 'cue_unaligned'):
            find_cue(cues, events[1]['cue'])


if __name__ == '__main__':
    unittest.main()
