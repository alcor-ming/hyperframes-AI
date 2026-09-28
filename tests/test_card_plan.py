"""Approved card slots and allocation checks, using synthetic content only."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from visual_plan import (VisualPlanError, card_rows, parse_card, plan_scene_rows,
                         validate_card_layout, validate_plan_cards)


def card(preset='F01', area='full', body='title: Heading @hello\n- Row @hello'):
    return parse_card('card C1 · P001', f'preset: {preset}\narea: {area}\n{body}'.splitlines())


class CardPlanTest(unittest.TestCase):
    def test_semantic_rows_and_derived_events(self):
        value = card('F04', body='- Row @hello\n  indexKey: Role @hello')
        self.assertEqual(['1:indexKey', 1], [slot for slot, _ in card_rows(value)])
        value = card('F06', body='- Row @hello\n  key: Role @hello [test:plug@1]')
        self.assertEqual('test:plug@1', value['lines'][0]['key']['svg'])
        body = ('preset: F07\narea: full\ninputLabel: Prompt @hello\ninput: Request @hello\n'
                'outputLabel: Answer @hello [test:plug@1]\ntitle: Heading @hello\n- Row @hello\nemphasis: hello')
        plan = '---\n{"plan_format":"3.5.2"}\n---\n## S01\n```card C1 · P001\n' + body + '\n```\n'
        row = plan_scene_rows(plan)['S01']
        self.assertEqual('Prompt\nRequest\nAnswer\nHeading\nRow', row['screens']['C1']['实际表达'])
        self.assertEqual(['C1:inputLabel', 'C1:input', 'C1:outputLabel', 'C1:title', 'C1:1', 'C1'],
                         [event['target'] for event in row['events']])
        figure = plan.replace(body, 'preset: F03\narea: full\n- Row @hello\nfigure: custom:f.svg @hello')
        self.assertEqual('C1:figure', plan_scene_rows(figure)['S01']['events'][-1]['target'])

    def test_unsupported_slots_and_duplicates(self):
        for preset, body in [
            ('F01', 'input: Wrong @hello'), ('F01', 'figure: custom:f.svg @hello'),
            ('F01', '- Row @hello\n  key: Wrong @hello'),
            ('F06', '- Row @hello [test:plug@1]'),
            ('F05', '- Row @hello [test:plug@1]'),
            ('F07', '- Row @hello [test:plug@1]'),
            ('F01', 'note: Wrong @hello [test:plug@1]'),
            ('F04', '- Row @hello\n  indexKey: Wrong @hello [test:plug@1]'),
            ('F04', '  indexKey: Orphan @hello'),
            ('F04', '- Row @hello\n  indexKey: A @hello\n  indexKey: B @hello'),
            ('F07', 'inputLabel: Wrong @hello [test:plug@1]'),
            ('F03', '- Row @hello\nfigure: test:plug@1 @hello'),
        ]:
            with self.subTest(preset=preset, body=body), self.assertRaises(VisualPlanError):
                card(preset, body=body)
        with self.assertRaises(VisualPlanError):
            card(area='invented')
        for preset in ('F04', 'F06', 'F07'):
            self.assertEqual(1, len(card(preset)['lines']))

    def test_all_allocations_and_capacity(self):
        for ratio, full in [('16:9', (1776, 936)), ('9:16', (936, 1776))]:
            for preset in [f'F0{i}' for i in range(1, 9)]:
                for area in ('full', 'left', 'right', 'top', 'bottom'):
                    layout = validate_card_layout(card(preset, area), ratio)
                    if area == 'full':
                        self.assertEqual(full, (layout['width'], layout['height']))
                    max_lines = layout['max_lines']
                    validate_card_layout(card(preset, area, '\n'.join(['- Row @hello'] * max_lines)), ratio)
                    with self.assertRaisesRegex(VisualPlanError, 'overflow'):
                        validate_card_layout(card(preset, area, '\n'.join(['- Row @hello'] * (max_lines + 1))), ratio)
        self.assertEqual(984, validate_card_layout(card(area='right'), '16:9')['x'])
        self.assertEqual(564, validate_card_layout(card(area='bottom'), '16:9')['y'])
        self.assertEqual(72, validate_card_layout(card(area='800px x 600px'), '16:9')['x'])
        with self.assertRaisesRegex(VisualPlanError, 'safe frame'):
            validate_card_layout(card(area='1900x1000'), '16:9')
        with self.assertRaises(VisualPlanError):
            validate_card_layout(card(), '4:3')

    def test_figure_cue_closure_and_safety(self):
        plan = ('---\n{"plan_format":"3.5.2"}\n---\n## S01\n```card C1 · P001\n'
                'preset: F03\narea: full\n- Row @hello\nfigure: custom:f.svg @hello\nemphasis: hello\n```')
        cues = {'text': 'hello', 'characters': [
            {'char': ch, 'start': i / 10, 'end': (i + 1) / 10, 'aligned': True}
            for i, ch in enumerate('hello')]}
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            path = project / 'f.svg'
            path.write_text('<svg viewBox="0 0 640 180"><path d="M16 16L32 32"/></svg>')
            validate_plan_cards(plan, cues, project=project, closure=['f.svg'])
            with self.assertRaisesRegex(VisualPlanError, 'outside snapshot'):
                validate_plan_cards(plan, cues, project=project, closure=[])
            with self.assertRaisesRegex(VisualPlanError, 'cue resolution failed'):
                validate_plan_cards(plan.replace('emphasis: hello', 'emphasis: absent'), cues,
                                    project=project, closure=['f.svg'])
            path.write_text('<svg><script>alert(1)</script></svg>')
            with self.assertRaisesRegex(VisualPlanError, 'unsafe SVG'):
                validate_plan_cards(plan, cues, project=project, closure=['f.svg'])


if __name__ == '__main__':
    unittest.main()
