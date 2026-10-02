"""Versioned product lines and their small reference mechanism catalogue."""
from copy import deepcopy
import json
from pathlib import Path


def catalogue(name):
    # JSON is the repository's dependency-free YAML subset.
    return json.loads(Path(__file__).with_name(name + '.yaml').read_text(encoding='utf-8'))


def select(state):
    mode = state.get('mode') or 'card'
    suffix = state.get('submodule') or state.get('appearance_lock', {}).get('submodule') if mode == 'showcase' else state.get('series_binding', {}).get('spec')
    identity = mode + ('/' + suffix if suffix else '')
    if identity not in catalogue('lines')['lines']:
        raise ValueError('Unknown product line: ' + identity)
    return deepcopy(catalogue('lines')['lines'][identity])


def frozen(state):
    line = state.get('line')
    if line is None:
        return None
    known = catalogue('lines')['lines']
    if not isinstance(line, dict) or line.get('id') not in known or type(line.get('version')) is not int:
        raise ValueError('Invalid frozen product line')
    if set(line) != {'id', 'version'} or line['version'] != known[line['id']]['version']:
        raise ValueError('Unsupported frozen product line version')
    return deepcopy(known[line['id']])


def bind(state):
    line = select(state)
    return {key: line[key] for key in ('id', 'version')}


def validate_catalogues():
    lines = catalogue('lines')['lines']
    required = {'id', 'version', 'mode', 'author_model', 'plan_template', 'brief', 'subjects', 'stages', 'thresholds', 'critic_checks', 'defaults', 'assets', 'exemptions'}
    for identity, line in lines.items():
        if set(line) != required or line['id'] != identity or line['version'] != 1:
            raise ValueError('Invalid product line: ' + identity)
        for paths in line['stages'].values():
            if any(not (Path(__file__).resolve().parents[1] / path).is_file() for path in paths):
                raise ValueError('Missing line rule file: ' + identity)
    ids = set()
    for item in catalogue('mechanisms')['mechanisms']:
        if set(item) != {'id', 'mechanism', 'lines', 'transfer', 'source'} or item['id'] in ids or not item['lines'] or not set(item['lines']) <= lines.keys():
            raise ValueError('Invalid reference mechanism')
        if any(not isinstance(item[key], str) or not item[key].strip() for key in ('id', 'mechanism', 'transfer', 'source')) or not item['source'].startswith('https://'):
            raise ValueError('Invalid reference mechanism fields')
        ids.add(item['id'])
    return lines
