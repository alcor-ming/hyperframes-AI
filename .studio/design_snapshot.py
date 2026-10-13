"""Copy card files into a Variant without replacing its authored project assets."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import designs
from storage import scoped_path
from windows_runtime import validate_review_tree


IGNORED_SNAPSHOT_DIRS = ('study',)


def snapshot_files(directory):
    """Card files that enter a Variant snapshot: skips study/, dot entries and __pycache__."""
    result = []
    for path in sorted(directory.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(directory).parts
        if parts[0] in IGNORED_SNAPSHOT_DIRS or any(part.startswith('.') or part == '__pycache__' for part in parts):
            continue
        result.append(path)
    return result


def inventory(identity):
    card = designs.require(identity)
    directory = designs.card_path(identity)
    validate_review_tree(directory)
    sources = {f'card/{p.relative_to(directory).as_posix()}': p
               for p in snapshot_files(directory)}
    references = {}
    for ref in card.get('references', []):
        owner, asset = designs._parse_reference(ref)
        origin = scoped_path(designs.card_path(owner), 'assets/' + asset)
        validate_review_tree(origin)
        files = {p.relative_to(origin).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in origin.rglob('*') if p.is_file()}
        if 'asset.json' not in files:
            raise ValueError('Missing referenced asset: ' + ref)
        references[ref] = files
        sources.update({f'references/{ref}/{name}': origin / name for name in files})
    files = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(sources.items())}
    if json.loads((directory / 'design.json').read_text(encoding='utf-8')) != card:
        raise ValueError('Card changed during snapshot')
    return {'design': card, 'files': files, 'references': references}, sources


def verify(directory, receipt):
    validate_review_tree(directory)
    files = {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in directory.rglob('*') if p.is_file()}
    if files != receipt['files']:
        raise ValueError('Frozen card files changed')


def freeze(variant, identity):
    receipt, sources = inventory(identity)
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()
    relative = 'vendor/designs/' + digest
    destination = scoped_path(variant, relative)
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.card-', dir=destination.parent) as temporary:
            staging = Path(temporary) / 'files'
            staging.mkdir()
            for name, source in sources.items():
                target = scoped_path(staging, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            verify(staging, receipt)
            staging.rename(destination)
    verify(destination, receipt)
    return {**receipt, 'path': relative}


def changes(receipt):
    current, _ = inventory(receipt['design']['id'])
    before, after = receipt['files'], current['files']
    files = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    refs = sorted(ref for ref in receipt['references'].keys() | current['references'].keys()
                  if receipt['references'].get(ref) != current['references'].get(ref))
    own = {receipt['design']['id'] + '/' + name.split('/')[2]
           for name in files if name.startswith('card/assets/') and len(name.split('/')) > 3}
    return {'files': files, 'references': refs, 'reinstall_assets': sorted(own | set(refs)),
            'message': f'卡片自本 Draft 后有变化（{len(files)} 个文件、{len(refs)} 个引用资产）' if files else None}
