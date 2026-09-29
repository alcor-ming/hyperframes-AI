"""Explicit musical timing and Scene-local mathematical intent."""

import json
import math
import re


def validate_beat_grid(grid):
    if (not isinstance(grid, dict) or set(grid) != {
            'schema_version', 'audio_sha256', 'beats_per_bar', 'first_downbeat', 'times'}
            or type(grid['schema_version']) is not int or grid['schema_version'] != 1
            or not isinstance(grid['audio_sha256'], str)
            or not re.fullmatch(r'[0-9a-fA-F]{64}', grid['audio_sha256'])
            or type(grid['beats_per_bar']) is not int or not 1 <= grid['beats_per_bar'] <= 9007199254740991
            or not isinstance(grid['times'], list) or not grid['times']
            or type(grid['first_downbeat']) is not int
            or not 0 <= grid['first_downbeat'] < len(grid['times'])):
        raise ValueError('invalid_beat_grid')
    previous = -1
    for time in grid['times']:
        if type(time) not in (int, float) or not math.isfinite(time) or time < 0 or time <= previous:
            raise ValueError('invalid_beat_grid')
        previous = time
    return grid


def make_beat_grid(times, audio_sha256, beats_per_bar, first_downbeat):
    return validate_beat_grid(dict(schema_version=1, audio_sha256=audio_sha256,
                                   beats_per_bar=beats_per_bar, first_downbeat=first_downbeat, times=times))


def find_beat(grid, bar, beat):
    validate_beat_grid(grid)
    if (type(bar) is not int or not 1 <= bar <= 9007199254740991
            or type(beat) is not int or not 1 <= beat <= grid['beats_per_bar']):
        raise ValueError('invalid_beat_query')
    index = grid['first_downbeat'] + (bar - 1) * grid['beats_per_bar'] + beat - 1
    if index >= len(grid['times']):
        raise ValueError('beat_not_found')
    return grid['times'][index]


def _contract(value, scene):
    def fail():
        raise ValueError(f'{scene}: invalid_math_plan')

    if not isinstance(value, dict) or set(value) != {'units', 'symbols', 'invariants', 'zero_basics', 'cues'}:
        fail()
    if (not all(isinstance(value[key], list) for key in ('units', 'invariants', 'zero_basics', 'cues'))
            or not isinstance(value['symbols'], dict)
            or not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                       for k, v in value['symbols'].items())
            or not all(isinstance(v, str) and v.strip() for v in value['invariants'])):
        fail()
    ids = set()
    for unit in value['units']:
        if (not isinstance(unit, dict) or set(unit) != {'id', 'symbol', 'graphic'}
                or not all(isinstance(v, str) for v in unit.values()) or not unit['id'].strip()
                or unit['id'] in ids or unit['symbol'] not in value['symbols']):
            fail()
        ids.add(unit['id'])
    for check in value['zero_basics']:
        if (not isinstance(check, dict) or set(check) != {'relation', 'action'}
                or not all(isinstance(v, str) for v in check.values())):
            fail()
    for event in value['cues']:
        if (not isinstance(event, dict) or set(event) != {'cue', 'keep', 'reveal', 'remove'}
                or not isinstance(event['cue'], (str, dict))):
            fail()
        used = set()
        for key in ('keep', 'reveal', 'remove'):
            refs = event[key]
            if (not isinstance(refs, list) or not all(isinstance(v, str) and v in ids for v in refs)
                    or len(set(refs)) != len(refs) or used.intersection(refs)):
                fail()
            used.update(refs)
    return value


def parse_plan(text):
    from visual_plan import markdown_structure_lines
    headings = [m for m in markdown_structure_lines(text) if re.match(r'^## ', m[0])]
    result = {}
    for index, heading in enumerate(headings):
        match = re.fullmatch(r'## (S[0-9]+[A-Z]*)(?:\s+.*)?', heading[0])
        if not match:
            continue
        scene = match[1]
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        blocks, fence, lines = [], None, []
        for line in text[heading.end():end].splitlines():
            marker = re.fullmatch(r' {0,3}(`{3,}|~{3,})(.*)', line)
            if fence:
                if marker and marker[1][0] == fence[0][0] and len(marker[1]) >= len(fence[0]) and not marker[2].strip():
                    if fence[1] == 'math-plan':
                        blocks.append(json.loads('\n'.join(lines)))
                    fence = None
                else:
                    lines.append(line)
            elif marker:
                fence, lines = (marker[1], marker[2].strip()), []
        if scene in result or len(blocks) != 1 or fence and fence[1] == 'math-plan':
            raise ValueError(f'{scene}: expected_one_math_plan')
        result[scene] = _contract(blocks[0], scene)
    if not result:
        raise ValueError('missing_math_plan')
    return result


def plan_findings(text, cues, duration):
    from explainer import find_cue, number
    number(duration, 'duration')
    findings, identities, events = [], {}, []

    def report(code, scene, message):
        findings.append(dict(code=code, scene=scene, message=message))

    for scene, plan in parse_plan(text).items():
        for unit in plan['units']:
            if not unit['graphic'].strip():
                report('math_missing_graphic', scene, unit['id'])
            elif unit['graphic'] != plan['symbols'][unit['symbol']]:
                report('math_symbol_inconsistent', scene, unit['id'])
        for symbol, identity in plan['symbols'].items():
            if symbol in identities and identities[symbol] != identity:
                report('math_symbol_inconsistent', scene, symbol)
            identities[symbol] = identity
        if not plan['invariants']:
            report('math_missing_invariants', scene, 'No invariants declared')
        if not plan['zero_basics'] or any(not v['relation'].strip() or not v['action'].strip() for v in plan['zero_basics']):
            report('math_missing_zero_basics', scene, 'Each relation needs a visible action')
        for event in plan['cues']:
            try:
                at = find_cue(cues, event['cue'])
                if at > duration:
                    raise ValueError('cue_outside_duration')
                if event['reveal'] or event['remove']:
                    events.append(at)
            except ValueError as exc:
                report('math_unresolved_cue', scene, str(exc))
    if duration - max(events, default=0) > 2:
        report('math_trailing_gap', None, 'More than 2 seconds after the last mathematical event')
    return findings
