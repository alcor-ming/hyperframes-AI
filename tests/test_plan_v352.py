"""Synthetic new-format Plan checks; no production inputs."""
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from visual_plan import VisualPlanError, plan_cue, plan_scene_rows, validate_plan_cards
from visual_diagnostics import plan_information, source_sections


HEADER = '---\n{"plan_format":"3.5.2"}\n---\n'
CARD = r'''## S01
One sentence.
```card C1 · P001
preset: F01
area: 800x600
title: Contact \@home \[today] @hello#2 [test:plug@1]
- First row @hello
note: Remember @hello
exit: hello#2
```
| cue | 层 | 目标 | 变化 |
|---|---|---|---|
| hello | 3 | emphasis | highlight |
| hello | 2 | | pan |
| 例外 | hello | hello#2 | pause | reading |
### I01 · P001
```screen
Independent text
```
## S02
**延续信息：** C1, I01
'''


class PlanV352Test(unittest.TestCase):
    def test_cards_events_information_and_continuation(self):
        rows = plan_scene_rows(HEADER + CARD)
        self.assertEqual(rows['S01']['screens'], rows['S02']['screens'])
        card = rows['S01']['cards']['C1']
        self.assertEqual('Contact @home [today]', card['title']['text'])
        self.assertEqual({'token': 'hello', 'nth': 2}, card['title']['cue'])
        self.assertEqual(['C1:title', 'C1:1', 'C1:note', 'C1', 'emphasis', ''],
                         [event['target'] for event in rows['S01']['events']])
        self.assertEqual('pause', rows['S01']['exceptions'][0]['kind'])
        information, _ = plan_information(HEADER + CARD)
        self.assertIn('First row', information['C1']['实际表达'])
        sources = source_sections('<!-- P001 -->Source narration', '', information)
        for identity in ('I01', 'C1'):
            self.assertEqual('Source narration', sources[information[identity]['信息 ID / 来源']])
        self.assertEqual(['S01'], list(plan_scene_rows(HEADER + '## S01\nMedia only.')))

    def test_invalid_version_and_card_syntax(self):
        self.assertEqual({'token': 'hello', 'edge': 'end', 'within': [0, 2]},
                         plan_cue('{"token":"hello","edge":"end","within":[0,2]}'))
        with self.assertRaisesRegex(VisualPlanError, 'invalid cue query'):
            plan_cue('{"token":"hello","unknown":1}')
        for plan in [CARD, HEADER.replace('3.5.2', '3.5.1') + CARD,
                     HEADER + CARD.replace('F01', 'F09'),
                     HEADER + CARD.replace('800x600', '0x600'),
                     HEADER + CARD.replace(r'\@home', '@home'),
                     HEADER + CARD.replace('## S02', '```card C1 · P002\npreset: F02\narea: left\n- again @hello\n```\n## S02'),
                     HEADER + CARD.replace('### I01 · P001', '### I01 · P001\n```rhythm\n{}\n```'),
                     HEADER + CARD.replace('C1, I01', 'C9')]:
            with self.subTest(plan=plan), self.assertRaises(VisualPlanError):
                plan_scene_rows(plan)

    def test_cue_resolution_and_svg_closure(self):
        text = 'hello hello'
        cues = {'text': text, 'characters': [{'char': char, 'start': i / 10, 'end': (i + 1) / 10, 'aligned': True}
                                            for i, char in enumerate(text)]}
        plan = (HEADER + CARD).replace('@hello\n', '@hello#1\n')
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            validate_plan_cards(plan, cues, project=project, closure=[], icon_refs=['test:plug@1'])
            validate_plan_cards(plan.replace('test:plug@1', 'test:plug'), cues,
                                project=project, closure=[], icon_refs=['test:plug@1'])
            with self.assertRaisesRegex(VisualPlanError, 'SVG icon reference outside'):
                validate_plan_cards(plan.replace('test:plug@1', 'test:plug'), cues,
                                    project=project, closure=[], icon_refs=['test:plug@1', 'test:plug@2'])
            validate_plan_cards(plan, None, project=project, closure=[], scene_ids=['S02'])
            with self.assertRaisesRegex(VisualPlanError, 'cue resolution failed'):
                validate_plan_cards(plan.replace('@hello#1', '@absent'), cues, project=project, closure=[], icon_refs=['test:plug@1'])
            with self.assertRaisesRegex(VisualPlanError, 'SVG icon reference outside'):
                validate_plan_cards(plan, cues, project=project, closure=[])
            (project / 'diagram.svg').write_text('<svg/>')
            custom = plan.replace('test:plug@1', 'custom:diagram.svg')
            with self.assertRaisesRegex(VisualPlanError, 'SVG reference outside'):
                validate_plan_cards(custom, cues, project=project, closure=[])
            validate_plan_cards(custom, cues, project=project, closure=['diagram.svg'])
            with self.assertRaisesRegex(VisualPlanError, 'SVG reference outside'):
                validate_plan_cards(custom.replace('custom:diagram.svg', 'custom:../diagram.svg'), cues,
                                    project=project, closure=['../diagram.svg'])


if __name__ == '__main__':
    unittest.main()
