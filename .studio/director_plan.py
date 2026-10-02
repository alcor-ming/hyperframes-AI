"""Director Brief and A/B storyboard, layered on the existing Scene parser."""
import re

import lines


FORMAT = '3.7.0'


def parse(text, metadata, scenes):
    line = lines.frozen({'line': metadata.get('line')})
    if line is None:
        raise ValueError('New Plan requires a frozen line')
    brief_section = re.search(r'^## 导演 Brief\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    brief = dict(re.findall(r'^\*\*(.+?)[：:]\*\*\s*([^\n]*)', brief_section[1] if brief_section else '', re.M))
    findings = [{'kind': 'missing_brief_field', 'field': key} for key in line['brief']['required'] if not brief.get(key, '').strip()]
    references = [value for value in re.split(r'[,，、\s]+', brief.get('参考机制', '').strip()) if value]
    known = {item['id']: item for item in lines.catalogue('mechanisms')['mechanisms']}
    if line['mode'] == 'explainer' and not 1 <= len(references) <= 3:
        findings.append({'kind': 'reference_count', 'expected': '1–3'})
    for identity in references:
        if identity not in known:
            findings.append({'kind': 'unknown_mechanism', 'id': identity})
        elif line['id'] not in known[identity]['lines']:
            findings.append({'kind': 'mechanism_line_mismatch', 'id': identity})
    section = re.search(r'^## 分镜表\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    segments, seen, previous_scene = {}, set(), None
    for row in (section[1] if section else '').splitlines():
        if not row.lstrip().startswith('|'):
            continue
        cells = [cell.strip() for cell in re.split(r'(?<!\\)\|', row.strip().strip('|'))]
        if cells[0] == '段' or all(re.fullmatch(r':?-+:?', cell) for cell in cells):
            continue
        match = re.fullmatch(r'(S[0-9]+[A-Z]*)·([AB])([1-9][0-9]*)', cells[0])
        if not match or len(cells) != 7:
            findings.append({'kind': 'invalid_storyboard_row', 'row': row})
            continue
        sid, role, number = match.groups()
        if sid != previous_scene and sid in segments:
            findings.append({'kind': 'interleaved_scene', 'scene': sid})
        previous_scene = sid
        values = segments.setdefault(sid, [])
        expected_role = 'A' if len(values) % 2 == 0 else 'B'
        expected_number = len(values) // 2 + 1
        if role != expected_role or int(number) != expected_number or cells[0] in seen:
            findings.append({'kind': 'invalid_segment_sequence', 'id': cells[0]})
        seen.add(cells[0])
        if not all(cells[1:4]):
            findings.append({'kind': 'missing_storyboard_content', 'id': cells[0]})
        if cells[5] not in ('', 'cut'):
            findings.append({'kind': 'invalid_handoff', 'id': cells[0]})
        values.append({'id': cells[0], 'role': role, 'cue': cells[1], 'visible': cells[2], 'task': cells[3],
                       'subject': cells[4] or line['subjects'][role]['primary'],
                       'secondary': line['subjects'][role]['secondary'], 'handoff': cells[5],
                       'carry': [value for value in re.split(r'[,，、\s]+', cells[6]) if value]})
    if set(segments) != set(scenes):
        findings.append({'kind': 'storyboard_scene_mismatch', 'storyboard': list(segments), 'scenes': list(scenes)})
    return {'brief': brief, 'segments': segments, 'findings': findings}
