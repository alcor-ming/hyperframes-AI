"""Small advisory text checks, without browser, WorkStore or rendering."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from visual_diagnostics import normalize, static_inventory, text_diagnostics
from visual_plan import VisualPlanError


SOURCE = '系统首先读取用户提供的原始材料然后提取关键事实并保留必要条件最后生成简洁清楚且便于理解的上屏文字'


def plan(expression=SOURCE, info='I01'):
    return f'''| 原 Scene ID | 使用信息 ID |
| --- | --- |
| S01 | {info} |

| 信息 ID / 来源 | 实际表达 | 视觉职责 |
| --- | --- | --- |
| I01 · P001 | {expression} | 定义 |
'''


def samples(*parts, info='I01'):
    return [{'time': index * 0.5, 'ready': True, 'texts': [
        {'scene': 'S01', 'info': info, 'text': part, 'selector': '#card'}]}
        for index, part in enumerate(parts)]


class VisualTextTests(unittest.TestCase):
    def diagnose(self, parts, **kwargs):
        return text_diagnostics(parts, '<!-- P001 -->\n' + SOURCE, '', kwargs.pop('plan', plan()), **kwargs)

    def test_copy_split_cards_and_distributed_rewording(self):
        changed = SOURCE.replace('首先', '先行').replace('然后', '随后').replace('最后', '最终')
        for states in (samples(SOURCE), samples(SOURCE[:16], SOURCE[16:32], SOURCE[32:]), samples(changed)):
            with self.subTest(states=states):
                report = self.diagnose(states)
                hits = [hit for hit in report['findings'] if hit['kind'] == 'suspected_copy']
                self.assertEqual(1, len(hits))
                self.assertGreaterEqual(hits[0]['coverage'], 0.8)

    def test_persistent_text_is_not_repeated_and_progressive_reveal_is_merged(self):
        report = self.diagnose(samples(SOURCE[:15], SOURCE[:30], SOURCE, SOURCE))
        self.assertEqual(SOURCE, report['findings'][0]['text'])

    def test_short_cards_with_shared_source_anchor_aggregate(self):
        expression = plan(SOURCE[:16], info='I01 I02 I03')
        expression += f'| I02 · P001 | {SOURCE[16:32]} | 解释 |\n| I03 · P001 | {SOURCE[32:]} | 解释 |\n'
        states = samples(SOURCE[:16], SOURCE[16:32], SOURCE[32:])
        for index, sample in enumerate(states):
            sample['texts'][0]['info'] = f'I0{index + 1}'
        report = self.diagnose(states, plan=expression)
        self.assertEqual(['suspected_split_copy'], [item['kind'] for item in report['findings']])

    def test_explicit_exception_excludes_only_confirmed_fragment(self):
        confirmed = {'scene': 'S01', 'text': SOURCE[:20], 'source': 'SCRIPT.md#P001', 'reason': 'User confirmed exact definition'}
        report = self.diagnose(samples(SOURCE), exceptions=[confirmed])
        self.assertTrue(any(hit['kind'] == 'suspected_copy' for hit in report['findings']))
        self.assertEqual([confirmed], report['confirmed_exceptions'])
        for text in (SOURCE[:12], SOURCE[:32], SOURCE):
            approved = {**confirmed, 'text': text}
            report = self.diagnose(samples(text), plan=plan(text), exceptions=[approved])
            self.assertEqual([], report['findings'])
        with self.assertRaises(VisualPlanError):
            self.diagnose(samples(SOURCE), exceptions=[{**confirmed, 'text': 'not in source'}])

    def test_definition_label_is_not_automatic_exemption(self):
        self.assertEqual('suspected_copy', self.diagnose(samples(SOURCE))['findings'][0]['kind'])

    def test_plan_difference_and_missing_mapping_are_advisory(self):
        report = self.diagnose(samples(SOURCE), plan=plan('读取材料，保留条件，提炼表达'))
        self.assertIn('plan_implementation_difference', [hit['kind'] for hit in report['findings']])
        report = self.diagnose(samples(SOURCE, info=''), plan=plan(info='I01 I02'))
        self.assertIn('semantic_mapping_requires_review', [entry['reason'] for entry in report['unverified']])
        self.assertIn('suspected_copy', [hit['kind'] for hit in report['findings']])
        report = self.diagnose(samples('Unrelated decorative label', info=''), plan=plan())
        self.assertFalse(any(hit['kind'] == 'plan_implementation_difference' for hit in report['findings']))
        self.assertIn('semantic_mapping_requires_review', [entry['reason'] for entry in report['unverified']])

    def test_unready_sample_is_not_text_evidence_and_symbols_survive(self):
        states = samples(SOURCE)
        states[0]['ready'] = False
        self.assertEqual([], self.diagnose(states)['findings'])
        self.assertEqual('不低于-1.5%且≤20kg', normalize('不低于 -1.5%，且 ≤ 20 kg。'))

    def test_static_text_is_inventory_not_visibility_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('<p hidden>hidden candidate</p><!-- comment --><script>secret()</script><svg><text>visible</text></svg>')
            (root / 'data.json').write_text('{"title":"candidate"}')
            entries = static_inventory(root, ['index.html', 'data.json'])
            self.assertEqual(['hidden candidate', 'visible', 'candidate'], [entry['text'] for entry in entries])
            self.assertEqual('/title', entries[-1]['pointer'])


if __name__ == '__main__':
    unittest.main()
