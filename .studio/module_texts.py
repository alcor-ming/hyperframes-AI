"""Frozen module text declarations and per-Scene human acceptance."""
import json
from pathlib import Path
import os
import re
import subprocess
import tempfile

from work_requests import safe


def needs_inventory(project):
    appearance = project / 'appearance-lock.json'
    if appearance.is_file() and json.loads(appearance.read_text()).get('card_fonts'):
        return True
    lock = project / 'COMPONENT_LOCK.json'
    if not lock.is_file():
        return False
    for item in json.loads(lock.read_text())['components']:
        if item.get('asset_kind') == 'module':
            return True
    return False


def collect(project, scenes, lock):
    with tempfile.TemporaryDirectory(prefix='module-texts-') as temporary:
        request = Path(temporary) / 'request.json'
        request.write_text(json.dumps({'project': str(project), 'scenes': scenes,
                                      'width': lock.get('width', 1920), 'height': lock.get('height', 1080)}))
        result = subprocess.run([os.environ.get('HYPERFRAMES_NODE', 'node'), str(Path(__file__).with_name('text_inventory.mjs')), str(request)],
                                check=True, capture_output=True, text=True, timeout=120)
        inventory = json.loads(result.stdout)
        if inventory.get('complete') is not True or not isinstance(inventory.get('items'), list):
            raise ValueError('Incomplete module text inventory')
        component_lock = project / 'COMPONENT_LOCK.json'
        assets = []
        if component_lock.is_file():
            for item in json.loads(component_lock.read_text())['components']:
                if item.get('asset_kind') == 'module':
                    metadata = json.loads(safe(project, item['vendor_path'] + '/asset.json').read_text())
                    assets.append((item['component_ref'].rsplit('@v', 1)[0], metadata))
        for item in inventory['items']:
            matches = [metadata for ref, metadata in assets if item.get('asset') in (ref, metadata['id'])]
            if len(matches) != 1:
                raise ValueError('Module text asset must identify one installed asset: ' + str(item.get('asset')))
            ownership = matches[0].get('text_ownership') or {}
            item['ownership_allowed'] = item.get('kind') == 'attached' or not item.get('embedded') or (
                ownership.get('mode') == 'embedded' and item.get('text_type') in ownership.get('kinds', []))
        return inventory


def diagnostics(items):
    findings, delegated, reading = [], [], []
    for item in items:
        location = {key: item.get(key) for key in ('scene', 'asset', 'id', 'text_type')}
        numbers = re.findall(r'[+-]?\d+(?:[.,]\d+)*(?:%|％)?', item['text'])
        if numbers:
            findings.append({**location, 'kind': 'numeric_fact_review', 'numbers': numbers, 'verdict': None})
        if item.get('embedded'):
            delegated.append({**location, 'status': 'delegated' if item.get('ownership_allowed') else 'undeclared',
                              'checks': ['position', 'occlusion', 'layout_shift']})
            if item.get('kind') == 'independent' and not item.get('ownership_allowed'):
                findings.append({**location, 'kind': 'undeclared_embedded_text'})
            if item.get('font_coverage') is False:
                findings.append({**location, 'kind': 'font_glyph_missing'})
            seconds = item['end'] - item['start']
            reading.append({**location, 'seconds': seconds, 'characters': len(item['text'].strip()),
                            'characters_per_second': len(item['text'].strip()) / seconds, 'verdict': None})
    return {'findings': findings, 'layout': delegated, 'reading': reading}


def confirmation(inventory, confirmed, *, automatic=False):
    if inventory.get('complete') is not True:
        raise ValueError('Embedded text inventory is incomplete')
    if (inventory.get('dom_fonts') or {}).get('coverage') is False:
        raise ValueError('Card font closure does not cover text/caption characters')
    embedded = [item for item in inventory['items'] if item.get('embedded')]
    scenes = sorted({item['scene'] for item in embedded})
    if any(not scene for scene in scenes):
        raise ValueError('Embedded text requires a Scene identity')
    if any(not item.get('font_coverage') for item in embedded):
        raise ValueError('Embedded text font closure does not cover actual characters')
    if any(item.get('kind') == 'independent' and not item.get('ownership_allowed') for item in embedded):
        raise ValueError('Independent embedded text lacks an asset declaration')
    if scenes and (automatic or set(confirmed) != set(scenes)):
        raise ValueError('Confirm embedded text per Scene with --confirm-embedded: ' + ', '.join(scenes))
    return [{'scene': scene, 'confirmed': True} for scene in scenes]
