"""Pure calculations for normalized, single-publication content analytics."""
from math import isfinite
from statistics import median


PARAMETERS = {
    'version': 'v3.7.2',
    'early_exit_seconds': 1.0,
    'middle_exit_seconds': 3.5,
    'average_rounding_seconds': 0.5,
    'peak_neighbor_segments': 2,
    'peak_requires_local_maximum': True,
    'peak_edges': 'not_classified',
    'rewatch_peak_ratio': 1.5,
    'rewatch_peak_difference': 0.01,
    'skip_peak_difference': 0.005,
    'danmaku_small_sample': 50,
}


def _number(value, *, probability=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not isfinite(value) or value < 0 or (probability and value > 1):
        return None
    return value


def _overlap(a, b, start, end):
    return max(0, min(b, end) - max(a, start))


def _peak(segments, index, field):
    if index == 0 or index == len(segments) - 1:
        return False
    value = _number(segments[index].get(field), probability=True)
    left = _number(segments[index - 1].get(field), probability=True)
    right = _number(segments[index + 1].get(field), probability=True)
    if value is None or left is None or right is None or value <= max(left, right):
        return False
    neighbors = [
        _number(segments[i].get(field), probability=True)
        for i in range(max(0, index - 2), min(len(segments), index + 3))
        if i != index
    ]
    if any(v is None for v in neighbors):
        return False
    baseline = median(neighbors)
    if field == 'rewatch_rate':
        return (value + 1e-12 >= baseline * PARAMETERS['rewatch_peak_ratio']
                and value - baseline + 1e-12 >= PARAMETERS['rewatch_peak_difference'])
    return value - baseline + 1e-12 >= PARAMETERS['skip_peak_difference']


def analyze(normalized, timings, *, evidence=None):
    """Return ordered metrics and interval alignment; all times are video seconds.

    Timings contain scene, anchor, start, end and optional character timings.
    Text windows use character onsets and half-open intervals to avoid counting
    a character twice across the adjacent opening windows.
    """
    limitations = ['没有逐秒留存曲线；平均离开点是估算均值，不代表中位数。',
                   '单条发布无基线；平均播放占比只在同一片长组内比较。']
    points = normalized.get('points', {})
    chars = sorted((c for t in timings for c in t.get('characters', [])),
                   key=lambda c: c['start'])

    def text(start, end):
        return ''.join(c['char'] for c in chars if start <= c['start'] < end)

    if not timings:
        limitations.append('未对齐：没有 Anchor / Scene 时间表。')
    if not chars:
        limitations.append('未提供字级时间，无法确定首个口播词和窗口内口播。')
    opening = {
        'first_word_at': chars[0]['start'] if chars else None,
        'text_0_2': text(0, 2) if chars else None,
        'text_2_5': text(2, 5) if chars else None,
        'text_0_5': text(0, 5) if chars else None,
    }
    segments = []
    raw_segments = normalized.get('segments', [])
    count = _number(points.get('danmaku_count'))
    small_sample = count is not None and count < PARAMETERS['danmaku_small_sample']
    if small_sample:
        limitations.append('弹幕样本少：全片少于 50 条。')
    elif count is None:
        limitations.append('弹幕总量未提供，无法判断样本量。')
    for i, segment in enumerate(raw_segments):
        start, end = segment['start'], segment['end']
        overlaps = []
        for timing in timings:
            seconds = _overlap(start, end, timing['start'], timing['end'])
            if seconds:
                overlaps.append({'scene': timing.get('scene'), 'anchor': timing.get('anchor'),
                                 'seconds': seconds})
        current, peer = (_number(segment.get(k)) for k in ('danmaku', 'peer_danmaku'))
        segments.append({
            **segment, 'overlaps': overlaps,
            'spoken_text': text(start, end) if chars else None,
            'rewatch_peak': _peak(raw_segments, i, 'rewatch_rate'),
            'skip_peak': _peak(raw_segments, i, 'skip_rate'),
            'danmaku_comparison': {'current': current, 'peer': peer,
                                  'difference': current - peer if current is not None and peer is not None else None,
                                  'small_sample': small_sample if count is not None else None},
            'evidence': [dict(e) for e in evidence or []
                         if _overlap(start, end, e['start'], e['end'])],
        })

    avg = _number(points.get('average_watch_seconds'))
    plays = _number(normalized.get('plays'))
    bounce = _number(points.get('bounce_2s'), probability=True)
    five = _number(points.get('completion_5s'), probability=True)
    loss = conditional = interval = leave = None
    valid = bounce is not None and five is not None and bounce + five <= 1 + 1e-12
    if not valid:
        limitations.append('2 秒 / 5 秒比率缺失、越界或概率组合无效，派生值未定义。')
    else:
        middle = max(0, 1 - bounce - five)
        if bounce < 1:
            loss = middle / (1 - bounce)
        else:
            limitations.append('2 秒后观众为零，2–5 秒相对流失未定义。')
        if five == 0:
            limitations.append('5 秒完播为 0，条件平均观看时长与平均离开点未定义。')
        elif avg is not None:
            spent = bounce * PARAMETERS['early_exit_seconds'] + middle * PARAMETERS['middle_exit_seconds']
            estimate = (avg - spent) / five
            if estimate < 5 - 1e-12:
                limitations.append('平均时长与 5 秒留存及假设不相容，条件平均观看时长未定义。')
            else:
                conditional = estimate
                half = PARAMETERS['average_rounding_seconds']
                interval = [max(5, (avg - half - spent) / five), (avg + half - spent) / five]
                leave = {'at': estimate, 'positions': [
                    {'scene': t.get('scene'), 'anchor': t.get('anchor')}
                    for t in timings if t['start'] <= estimate < t['end']
                ]}
                if not leave['positions']:
                    limitations.append('平均离开点未落入已提供的时间区间。')
        else:
            limitations.append('平均播放时长缺失或无效，条件平均观看时长未定义。')
    if plays is None:
        limitations.append('播放量未提供或无效，总观看时长未提供。')
    if avg is None:
        limitations.append('平均播放时长未提供或无效，总观看时长未提供。')
    metrics = {
        'average_watch_seconds': avg,
        'total_watch_seconds': avg * plays if avg is not None and plays is not None else None,
        'bounce_2s': bounce, 'completion_5s': five, 'loss_2_to_5': loss,
        'conditional_watch_seconds': conditional, 'conditional_watch_interval': interval,
        'average_leave_point': leave,
        'cover_click_rate': _number(points.get('cover_click_rate'), probability=True),
        'completion_rate': _number(points.get('completion_rate'), probability=True),
        'average_watch_ratio': _number(points.get('average_watch_ratio')),
    }
    return {'alignment': '已对齐' if timings else '未对齐', 'segments': segments,
            'opening': opening, 'metrics': metrics, 'parameters': dict(PARAMETERS),
            'limitations': limitations}


def traffic_changes(imports):
    """Compare consecutive imports in caller-supplied chronological order."""
    changes = []
    for i in range(1, len(imports)):
        before = {s['source']: _number(s.get('share'), probability=True)
                  for s in imports[i - 1].get('traffic_sources', [])}
        after = {s['source']: _number(s.get('share'), probability=True)
                 for s in imports[i].get('traffic_sources', [])}
        changes.append({'from_index': i - 1, 'to_index': i, 'sources': [
            {'source': source, 'before': before.get(source), 'after': after.get(source),
             'delta': after[source] - before[source]
             if before.get(source) is not None and after.get(source) is not None else None}
            for source in dict.fromkeys([*before, *after])
        ]})
    return changes
