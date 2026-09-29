"""Fixed geometry for the mathematical units already declared in math-plan."""

import math
import re
from pathlib import PurePosixPath

import math_chain


FIELDS = {
    'formula': {'slots'}, 'unknown': {'label'},
    'units': {'count', 'value', 'label'}, 'segment': {'count', 'value', 'label'},
    'area': {'value', 'label'}, 'number-line': {'min', 'max', 'step', 'labels'},
    'strike': {'label', 'negate'}, 'edge': {'from', 'to', 'length', 'label', 'duration'},
    'equals': {'to', 'duration'},
}
FRAMES = {'16:9': (1920, 1080), '9:16': (1080, 1920)}


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def item_text(item):
    if item['kind'] == 'equals':
        return '='
    if item['kind'] == 'formula':
        return ''.join(item['slots'])
    if item['kind'] == 'number-line':
        return ''.join(item['labels'])
    return item.get('value', '') + item.get('label', '')


def parse_plan(text, ratio=None):
    blocks = math_chain.parse_scene_blocks(text, 'math', required=False)
    if not blocks:
        return {}
    intents = math_chain.parse_plan(text)
    if ratio is not None and ratio not in FRAMES:
        raise ValueError('math_unsupported_ratio')
    for scene, block in blocks.items():
        def fail(message):
            raise ValueError(f'{scene}: {message}')

        if not isinstance(block, dict) or set(block) != {'font', 'items'}:
            fail('invalid_math_block')
        font = block['font']
        if (not isinstance(font, dict) or set(font) != {'path', 'sha256', 'characters'}
                or not all(isinstance(v, str) and v for v in font.values())
                or not re.fullmatch('[a-f0-9]{64}', font['sha256'])
                or len(font['characters']) > 4096):
            fail('invalid_math_font')
        path = PurePosixPath(font['path'])
        if (path.is_absolute() or any(p in ('', '.', '..') for p in font['path'].split('/'))
                or re.search(r'[\\:#?\x00-\x1f]', font['path'])
                or path.suffix.lower() not in {'.ttf', '.otf', '.woff', '.woff2'}):
            fail('math_font_requires_local_path')
        if not isinstance(block['items'], list) or not 1 <= len(block['items']) <= 128:
            fail('invalid_math_items')
        ids = set()
        for item in block['items']:
            if (not isinstance(item, dict) or not isinstance(item.get('kind'), str)
                    or item['kind'] not in FIELDS or set(item) != {'id', 'kind', 'box'} | FIELDS[item['kind']]):
                fail('invalid_math_item')
            identity, kind, box = item['id'], item['kind'], item['box']
            if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', identity) or identity in ids:
                fail('invalid_math_item_id')
            ids.add(identity)
            if (not isinstance(box, list) or len(box) != 4 or not all(number(v) for v in box)
                    or min(box[:2]) < 0 or min(box[2:]) <= 0):
                fail('invalid_math_box')
            if ratio and (box[0] + box[2] > FRAMES[ratio][0] or box[1] + box[3] > FRAMES[ratio][1]):
                fail('math_box_outside_frame')
            for key in ('label', 'value'):
                if key in item and (not isinstance(item[key], str) or not item[key] or len(item[key]) > 512):
                    fail('invalid_math_text')
            if kind == 'formula' and (not isinstance(item['slots'], list) or not 1 <= len(item['slots']) <= 16
                                      or not all(isinstance(v, str) and len(v) <= 128 for v in item['slots'])
                                      or not any(item['slots'])):
                fail('invalid_math_slots')
            if kind in ('units', 'segment') and (type(item['count']) is not int or not 1 <= item['count'] <= 32):
                fail('invalid_math_count')
            if kind in ('unknown', 'area') and box[2] != box[3]:
                fail('math_square_requires_equal_sides')
            if kind == 'number-line':
                if (not all(number(item[k]) for k in ('min', 'max', 'step'))
                        or item['step'] <= 0 or item['max'] <= item['min']):
                    fail('invalid_math_number_line')
                count = (item['max'] - item['min']) / item['step']
                if not math.isfinite(count) or not 1 <= count <= 32 or abs(count - round(count)) > 1e-8:
                    fail('invalid_math_number_line')
                if (not isinstance(item['labels'], list) or len(item['labels']) != round(count) + 1
                        or not all(isinstance(v, str) and v and len(v) <= 128 for v in item['labels'])):
                    fail('invalid_math_tick_labels')
            if kind == 'strike' and type(item['negate']) is not bool:
                fail('invalid_math_negation')
            if kind in ('edge', 'equals'):
                if not number(item['duration']) or not 0 < item['duration'] <= 10:
                    fail('invalid_math_motion_duration')
                for key in (('from', 'to') if kind == 'edge' else ('to',)):
                    point = item[key]
                    if (not isinstance(point, list) or len(point) != 2 or not all(number(v) and v >= 0 for v in point)):
                        fail('invalid_math_motion_point')
                    if ratio and any(point[i] + (box[2 + i] if kind == 'equals' else 0) > FRAMES[ratio][i] for i in (0, 1)):
                        fail('math_motion_outside_frame')
                if kind == 'edge':
                    if not number(item['length']) or item['length'] <= 0:
                        fail('invalid_math_edge_length')
                    if ratio and any(item[k][0] + item['length'] > FRAMES[ratio][0] for k in ('from', 'to')):
                        fail('math_motion_outside_frame')
            if not set(item_text(item)).issubset(set(font['characters'])):
                fail('math_font_characters_incomplete')
        if ids != {unit['id'] for unit in intents[scene]['units']}:
            fail('math_units_must_match_items')
    return blocks
