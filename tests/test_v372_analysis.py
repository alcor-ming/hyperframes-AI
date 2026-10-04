"""Synthetic acceptance coverage for content alignment and derived metrics."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from content_analysis import analyze, traffic_changes


def data():
    return {'plays': 1000, 'points': {
        'average_watch_seconds': 21, 'bounce_2s': .6, 'completion_5s': .3,
        'danmaku_count': 49, 'cover_click_rate': .1, 'completion_rate': .2,
        'average_watch_ratio': .21,
    }, 'segments': [
        {'start': i * 2, 'end': (i + 1) * 2, 'skip_rate': rate,
         'rewatch_rate': rate, 'danmaku': 3, 'peer_danmaku': 1}
        for i, rate in enumerate([.01, .02, .06, .02, .01])
    ]}


class ContentAnalysisTest(unittest.TestCase):
    def test_example_conditional_average_is_already_a_video_timestamp(self):
        original = data()
        frozen = copy.deepcopy(original)
        result = analyze(original, [{'scene': 'S2', 'anchor': 'A2', 'start': 65, 'end': 70}])
        metrics = result['metrics']
        self.assertEqual(metrics['total_watch_seconds'], 21000)
        self.assertAlmostEqual(metrics['loss_2_to_5'], .25)
        self.assertAlmostEqual(metrics['conditional_watch_seconds'], 66.833333333)
        self.assertAlmostEqual(metrics['conditional_watch_interval'][0], 65.1666666667)
        self.assertAlmostEqual(metrics['conditional_watch_interval'][1], 68.5)
        self.assertEqual(metrics['average_leave_point']['positions'], [{'scene': 'S2', 'anchor': 'A2'}])
        self.assertEqual(result['parameters']['early_exit_seconds'], 1)
        self.assertEqual(result['parameters']['middle_exit_seconds'], 3.5)
        self.assertEqual(original, frozen)
        self.assertEqual(list(metrics)[:4], ['average_watch_seconds', 'total_watch_seconds', 'bounce_2s', 'completion_5s'])

    def test_overlap_opening_and_evidence(self):
        timings = [
            {'scene': 'S1', 'anchor': 'A1', 'start': 0, 'end': 3,
             'characters': [{'char': '甲', 'start': .5, 'end': 1}, {'char': '乙', 'start': 2, 'end': 2.5}]},
            {'scene': 'S2', 'anchor': 'A2', 'start': 3, 'end': 10,
             'characters': [{'char': '丙', 'start': 4.8, 'end': 5.1}, {'char': '丁', 'start': 5, 'end': 5.4}]},
        ]
        evidence = [{'start': 3, 'end': 4, 'frame': 'frame.png', 'event': 'freeze'}]
        result = analyze(data(), timings, evidence=evidence)
        self.assertEqual(result['opening'], {'first_word_at': .5, 'text_0_2': '甲', 'text_2_5': '乙丙', 'text_0_5': '甲乙丙'})
        self.assertEqual(result['segments'][1]['overlaps'], [
            {'scene': 'S1', 'anchor': 'A1', 'seconds': 1}, {'scene': 'S2', 'anchor': 'A2', 'seconds': 1}])
        self.assertEqual(result['segments'][1]['spoken_text'], '乙')
        self.assertEqual(result['segments'][1]['evidence'], evidence)
        self.assertEqual(result['segments'][0]['evidence'], [])
        self.assertEqual(result['segments'][2]['evidence'], [])

    def test_missing_timing_keeps_metrics_and_marks_unaligned(self):
        result = analyze(data(), [])
        self.assertEqual(result['alignment'], '未对齐')
        self.assertEqual(len(result['segments']), 5)
        self.assertIsNone(result['opening']['first_word_at'])
        self.assertTrue(result['segments'][0]['danmaku_comparison']['small_sample'])
        self.assertEqual(result['segments'][0]['danmaku_comparison']['difference'], 2)
        normalized = data()
        normalized['points']['danmaku_count'] = 50
        self.assertFalse(analyze(normalized, [])['segments'][0]['danmaku_comparison']['small_sample'])

    def test_peak_positive_negative_and_monotonic(self):
        result = analyze(data(), [])
        for key in ('skip_peak', 'rewatch_peak'):
            self.assertEqual([s[key] for s in result['segments']], [False, False, True, False, False])
        normalized = data()
        for i, s in enumerate(normalized['segments']):
            s['skip_rate'] = .01 + .02 * i
        self.assertFalse(any(s['skip_peak'] for s in analyze(normalized, [])['segments']))
        # Local maximum must also clear the specified median threshold.
        for s in normalized['segments']:
            s['skip_rate'] = s['rewatch_rate'] = .02
        normalized['segments'][2].update(skip_rate=.024, rewatch_rate=.029)
        result = analyze(normalized, [])
        self.assertFalse(result['segments'][2]['skip_peak'])
        self.assertFalse(result['segments'][2]['rewatch_peak'])
        normalized['segments'][2].update(skip_rate=.025, rewatch_rate=.03)
        result = analyze(normalized, [])
        self.assertTrue(result['segments'][2]['skip_peak'])
        self.assertTrue(result['segments'][2]['rewatch_peak'])

    def test_undefined_and_missing_values(self):
        normalized = data()
        normalized['plays'] = None
        normalized['points']['completion_5s'] = 0
        result = analyze(normalized, [])
        self.assertIsNone(result['metrics']['total_watch_seconds'])
        self.assertIsNone(result['metrics']['conditional_watch_seconds'])
        self.assertIn('未提供', ' '.join(result['limitations']))
        self.assertIn('未定义', ' '.join(result['limitations']))
        for bounce, five in [(.8, .4), (-.1, .4), (.3, 1.1), (float('nan'), .4)]:
            normalized['points'].update(bounce_2s=bounce, completion_5s=five)
            metrics = analyze(normalized, [])['metrics']
            self.assertIsNone(metrics['loss_2_to_5'])
            self.assertIsNone(metrics['conditional_watch_seconds'])
        normalized['points'].update(bounce_2s=.2, completion_5s=.6, average_watch_seconds=-1)
        self.assertIsNone(analyze(normalized, [])['metrics']['conditional_watch_seconds'])
        normalized['points']['average_watch_seconds'] = 1
        self.assertIsNone(analyze(normalized, [])['metrics']['conditional_watch_seconds'])
        normalized['points'].update(bounce_2s=1, completion_5s=0)
        self.assertIsNone(analyze(normalized, [])['metrics']['loss_2_to_5'])

    def test_traffic_changes_distinguish_missing_from_zero(self):
        imports = [
            {'traffic_sources': [{'source': '搜索', 'share': .1}, {'source': '个人主页', 'share': .2}, {'source': '其他', 'share': .7}]},
            {'traffic_sources': [{'source': '搜索', 'share': .15}, {'source': '个人主页', 'share': 0}]},
            {'traffic_sources': [{'source': '搜索', 'share': None}]},
        ]
        result = traffic_changes(imports)
        sources = {s['source']: s for s in result[0]['sources']}
        self.assertAlmostEqual(sources['搜索']['delta'], .05)
        self.assertEqual(sources['个人主页']['delta'], -.2)
        self.assertIsNone(sources['其他']['delta'])
        self.assertIsNone(sources['其他']['after'])
        self.assertIsNone(result[1]['sources'][0]['delta'])
        self.assertEqual(traffic_changes(imports[:1]), [])


if __name__ == '__main__':
    unittest.main()
