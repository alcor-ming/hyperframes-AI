"""Explicit, replayable asset migration and non-destructive archive snapshots."""
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

import asset_store as store_api
from component_harness import (ComponentError, _atomic_json, _read_json, _read_frontmatter,
                               _safe_relative, file_sha256, package_write_lock,
                               parse_component_ref, validate_component_acceptance)

LAYERS = {'building-block', 'scene-template', 'content', 'reference'}
OWNER = 'hyperframes.asset-maintenance/v1'


def absolute(value):
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ComponentError('Maintenance paths must be absolute')
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ComponentError('Maintenance paths cannot contain symlinks')
    return path.resolve()


def inventory(directory):
    directory = absolute(directory)
    if not directory.is_dir():
        raise ComponentError(f'Missing directory: {directory}')
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ComponentError(f'Unsupported linked or special file: {path}')
        if path.is_file():
            if path.name == '.asset-write.lock':
                continue
            if path.stat().st_nlink != 1:
                raise ComponentError(f'Hardlinked file: {path}')
            result[path.relative_to(directory).as_posix()] = file_sha256(path)
    return result


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def selection(value):
    return store_api._validate_selection(value)


def target_store(value):
    target = absolute(value)
    store_api._guard_store(target)
    if (target / 'works').exists() or (target / '.studio').exists():
        raise ComponentError('Maintenance target cannot be a Harness or WorkStore')
    protected = {'HASHES.json', 'asset.json', 'COMPONENT.md', 'COMPONENT_LOCK.json', 'WORK.md', 'variant.yaml', 'acceptance.json'}
    if any(any((parent / name).exists() for name in protected)
           or parent.name in {'packages', 'candidates', 'acceptances', 'archive'}
           for parent in (target, *target.parents)):
        raise ComponentError('Maintenance target is inside a frozen asset, source or Work')
    if store_api._work_conflict(target, os.environ.get('HYPERFRAMES_AI_WORK_ROOT')):
        raise ComponentError('Maintenance target overlaps WorkStore')
    roots = [Path(__file__).resolve().parent.parent]
    roots += [Path(os.environ[key]) for key in ('HYPERFRAMES_AI_ROOT', 'HYPERFRAMES_AI_HOME') if os.environ.get(key)]
    if any(target == root or target in root.parents or root in target.parents for root in roots):
        raise ComponentError('Maintenance target overlaps the Harness')
    return target


def migrate_plan(source, target, classifications=None):
    source, target = absolute(source), target_store(target)
    store_api._guard_source(source)
    if source == target or source in target.parents or target in source.parents:
        raise ComponentError('Migration source and target must not overlap')
    if not source.is_dir() or (source / 'works').exists():
        raise ComponentError('Migration requires an explicit asset directory')
    if any((parent / 'WORK.md').exists() or (parent / 'variant.yaml').exists()
           or (parent / 'COMPONENT_LOCK.json').exists() for parent in (source, *source.parents)):
        raise ComponentError('Migration cannot read a Work or installed project')
    choices = selection(classifications or {})
    old_selection = selection(_read_json(source / 'selection.json')) if (source / 'selection.json').exists() else {}
    merged = {ref: {**old_selection.get(ref, {}), **choices.get(ref, {})} for ref in old_selection.keys() | choices.keys()}
    # Only recognized asset roots are scanned, never unrelated runtime or Work trees.
    is_store = not any((source / name).is_file() for name in ('asset.json', 'COMPONENT.md')) and any(
        (source / name).is_dir() for name in ('packages', 'candidates', 'sources'))
    roots = [(source / name, name) for name in ('packages', 'candidates', 'sources')] if is_store else [(source, 'source')]
    rows, pending, seen, hashes = [], [], set(), {}
    for directory, origin in roots:
        if not directory.exists():
            continue
        inventory(directory)
        metadata_files = sorted({*directory.rglob('asset.json'), *directory.rglob('COMPONENT.md')})
        for metadata_path in metadata_files:
            package = metadata_path.parent
            if package in seen or origin == 'candidates' and 'review' in metadata_path.relative_to(directory).parts:
                continue
            seen.add(package)
            frozen = (package / 'HASHES.json').is_file()
            metadata = _read_json(metadata_path) if metadata_path.name == 'asset.json' else _read_frontmatter(metadata_path)
            if frozen:
                report = store_api._validate_package(package)
                ref, sha = report['component_ref'], report['package_sha256']
                if ref in hashes and hashes[ref] != sha:
                    raise ComponentError(f'Conflicting identity/version: {ref}')
                hashes[ref] = sha
            elif metadata_path.name == 'asset.json':
                ref, sha = f"{metadata['id']}@v{metadata['version']}", None
                parse_component_ref(ref)
            else:
                pending.append({'path': str(package), 'reason': 'Unfrozen legacy metadata requires explicit conversion'})
                continue
            fields = merged.setdefault(ref, {})
            layer = fields.get('asset_layer', metadata.get('asset_layer'))
            if layer is None and metadata.get('kind') in {'media', 'theme', 'background', 'motion', 'character', 'icon-set'}:
                layer = 'content'
            if layer not in LAYERS:
                pending.append({'ref': ref, 'path': str(package), 'reason': 'Explicit asset_layer required'})
            else:
                fields['asset_layer'] = layer
            relative = store_api._relative(ref).as_posix()
            state = 'source'
            acceptance = None
            copy_root = package
            if origin == 'packages':
                if not frozen:
                    raise ComponentError('Accepted package is not frozen')
                acceptance_path = absolute(source / 'acceptances' / relative / 'acceptance.json')
                if acceptance_path.stat().st_nlink != 1:
                    raise ComponentError('Acceptance cannot be hardlinked')
                acceptance = _read_json(acceptance_path)
                validate_component_acceptance(acceptance, report)
                state, destination = 'accepted', 'packages/' + relative
            elif frozen:
                state, destination = 'candidate', 'candidates/' + relative
                if origin == 'candidates':
                    if package.name != 'package' or not (package.parent / 'candidate.json').is_file():
                        raise ComponentError('Invalid candidate directory')
                    copy_root = package.parent
            else:
                destination = 'sources/' + relative
            rows.append({'ref': ref, 'sha256': sha, 'state': state, 'source': str(copy_root),
                         'destination': destination, 'files': inventory(copy_root), 'acceptance': acceptance,
                         'candidate_wrapper': copy_root != package})
    # Reference documents are retained as a complete source tree, not executable packages.
    references = []
    for directory, origin in roots:
        if origin in {'sources', 'source'} and directory.exists():
            found, warnings = store_api._discover_references(directory)
            reference_dirs = sorted({Path(row['path']).parent for row in found})
            for ref_dir in reference_dirs:
                if any(parent in reference_dirs for parent in ref_dir.parents):
                    continue
                if any(Path(row['source']).is_relative_to(ref_dir) for row in rows):
                    pending.append({'path': str(ref_dir), 'reason': 'Reference tree overlaps package/source; separate before migration'})
                    continue
                references.append({'source': str(ref_dir), 'destination': 'sources/references-' + fingerprint(str(ref_dir))[:12],
                                   'files': inventory(ref_dir)})
            pending.extend({'path': row.get('path'), 'reason': row.get('code', 'Invalid reference')} for row in warnings)
    if not rows and not references:
        pending.append({'path': str(source), 'reason': 'No supported assets found'})
    return {'schema_version': 1, 'operation': 'migrate', 'source': str(source), 'target': str(target),
            'classifications': choices, 'selection': merged, 'items': rows, 'references': references, 'pending': pending}


def copy_checked(source, destination, expected, replacements=None):
    if inventory(source) != expected:
        raise ComponentError(f'Migration input changed: {source}')
    destination = absolute(destination)
    output = dict(expected)
    for name, data in (replacements or {}).items():
        output[name] = hashlib.sha256(data).hexdigest()
    if destination.exists():
        if inventory(destination) != output:
            raise ComponentError(f'Refusing different destination content: {destination}')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.asset-transfer-', dir=destination.parent) as temporary:
        staged = Path(temporary) / 'content'
        shutil.copytree(source, staged)
        for name, data in (replacements or {}).items():
            (staged / _safe_relative(name, 'replacement')).write_bytes(data)
        if inventory(staged) != output or inventory(source) != expected:
            raise ComponentError('Asset changed during copy')
        staged.rename(destination)


def migrate_apply(plan):
    if not isinstance(plan, dict) or plan.get('operation') != 'migrate' or plan.get('schema_version') != 1:
        raise ComponentError('Unsupported migration plan')
    source, target = absolute(plan['source']), target_store(plan['target'])
    with ExitStack() as locks:
        source_lock = (source / '.asset-write.lock' if not any((source / name).is_file() for name in ('asset.json', 'COMPONENT.md'))
                       and any((source / name).is_dir() for name in ('packages', 'candidates', 'sources'))
                       else source.parent / ('.asset-maintenance-' + fingerprint(str(source))[:12] + '.lock'))
        for lock in sorted({absolute(source_lock), store_api._target(target, '.asset-write.lock')}):
            locks.enter_context(package_write_lock(lock))
        fresh = migrate_plan(source, target, plan['classifications'])
        if fresh != plan:
            raise ComponentError('Migration plan changed; regenerate before applying')
        if plan['pending']:
            raise ComponentError('Migration has pending classifications or unsupported assets')
        selected_path = store_api._target(target, 'selection.json')
        selected = selection(_read_json(selected_path)) if selected_path.exists() else {}
        for ref, values in plan['selection'].items():
            if ref in selected and any(key in selected[ref] and selected[ref][key] != value for key, value in values.items()):
                raise ComponentError(f'Conflicting target selection: {ref}')
        # Preflight all identities before publishing any migrated object.
        for row in plan['items']:
            for name in ('packages', 'candidates'):
                existing = target / name / store_api._relative(row['ref'])
                if name == 'candidates':
                    existing /= 'package'
                if existing.exists() and row['sha256'] and store_api._validate_package(existing)['package_sha256'] != row['sha256']:
                    raise ComponentError(f'Conflicting target identity/version: {row["ref"]}')
            if row['acceptance'] is not None:
                record = store_api._target(target, 'acceptances/' + store_api._relative(row['ref']).as_posix() + '/acceptance.json')
                if record.exists() and _read_json(record) != row['acceptance']:
                    raise ComponentError('Refusing to overwrite acceptance history')
        for row in plan['items']:
            destination = store_api._target(target, row['destination'])
            if row['state'] == 'candidate' and not row['candidate_wrapper']:
                store_api._import_package(target, Path(row['source']))
            else:
                replacements = {}
                if row['candidate_wrapper']:
                    candidate = _read_json(Path(row['source']) / 'candidate.json')
                    if candidate.get('component_ref') != row['ref'] or candidate.get('package_sha256') != row['sha256']:
                        raise ComponentError('Invalid candidate provenance')
                    candidate.update(path=str(destination), review=str(destination / 'review'))
                    replacements['candidate.json'] = (json.dumps(candidate, indent=2, ensure_ascii=False) + '\n').encode()
                copy_checked(Path(row['source']), destination, row['files'], replacements)
            if row['acceptance'] is not None:
                record = store_api._target(target, ('acceptances/' + store_api._relative(row['ref']).as_posix() + '/acceptance.json'))
                if record.exists() and _read_json(record) != row['acceptance']:
                    raise ComponentError('Refusing to overwrite acceptance history')
                if not record.exists():
                    _atomic_json(record, row['acceptance'])
        for row in plan['references']:
            copy_checked(Path(row['source']), store_api._target(target, row['destination']), row['files'])
        if migrate_plan(source, target, plan['classifications']) != plan:
            raise ComponentError('Source changed during migration; legacy discovery remains enabled')
        for ref, values in plan['selection'].items():
            selected[ref] = {**selected.get(ref, {}), **values}
        _atomic_json(selected_path, selected)
        marker_path = store_api._target(target, 'catalog-migration.json')
        marker = _read_json(marker_path) if marker_path.exists() else {'schema_version': 1, 'retired_roots': []}
        marker['retired_roots'] = sorted(set(marker['retired_roots']) | {str(source)})
        _atomic_json(marker_path, marker)
    return {'operation': 'migrate', 'items': len(plan['items']), 'target': str(target),
            'retired_root': str(source), 'source_preserved': True}


def archive_plan(target, items):
    target = target_store(target)
    rows = []
    for name in sorted(set(items)):
        relative = _safe_relative(name, 'archive item')
        path = store_api._target(target, relative)
        parts = Path(relative).parts
        if len(parts) in {3, 4} and parts[0] == 'candidates':
            candidate = _read_json(path / 'candidate.json')
            ref = candidate['component_ref']
            if Path(relative) != Path('candidates') / store_api._relative(ref):
                raise ComponentError('Candidate identity/path mismatch')
            package = store_api._validate_package(path / 'package', ref)
            if package['package_sha256'] != candidate['package_sha256']:
                raise ComponentError('Candidate hash mismatch')
            if inventory(path / 'package') != inventory(path / 'review'):
                raise ComponentError('Edited candidate review cannot be archived')
        elif len(parts) == 2 and parts[0] == 'workspaces':
            marker = _read_json(path / '.asset-workspace.json')
            if marker != {'owner': OWNER, 'active': False}:
                raise ComponentError('Workspace has no inactive maintenance ownership')
        else:
            raise ComponentError('Archive only accepts owned candidates or workspaces')
        files = inventory(path)
        if any(Path(key).name in {'COMPONENT_LOCK.json', 'variant.yaml', 'WORK.md', 'acceptance.json'} for key in files):
            raise ComponentError('Archive cannot include Work, installed or accepted data')
        rows.append({'path': str(relative), 'files': files})
    if not rows:
        raise ComponentError('Archive requires explicit items')
    return {'schema_version': 1, 'operation': 'archive', 'target': str(target), 'items': rows}


def archive_apply(plan):
    if not isinstance(plan, dict) or plan.get('operation') != 'archive' or plan.get('schema_version') != 1:
        raise ComponentError('Unsupported archive plan')
    target = target_store(plan['target'])
    with package_write_lock(store_api._target(target, '.asset-write.lock')):
        fresh = archive_plan(target, [row['path'] for row in plan['items']])
        if fresh != plan:
            raise ComponentError('Archive input changed; regenerate plan')
        archive = store_api._target(target, 'archive/' + fingerprint(plan))
        for row in plan['items']:
            copy_checked(store_api._target(target, row['path']), archive / row['path'], row['files'])
        if archive_plan(target, [row['path'] for row in plan['items']]) != plan:
            raise ComponentError('Archive input changed during copy')
        _atomic_json(archive / 'manifest.json', plan)
    # ponytail: preserve originals; physical reclamation needs a separate live-use contract.
    return {'operation': 'archive', 'archive': str(archive), 'items': len(plan['items']),
            'source_preserved': True, 'reclaimed_bytes': 0}


def save_plan(path, plan):
    path = absolute(path)
    protected = [Path(plan['target'])]
    if plan['operation'] == 'migrate':
        protected.append(Path(plan['source']))
    if any(path.is_relative_to(root) for root in protected):
        raise ComponentError('Plan output must be outside source and target')
    if path.exists():
        if _read_json(path) != plan:
            raise ComponentError('Plan output already exists with different content')
    else:
        _atomic_json(path, plan)
    return {'plan': str(path), 'items': len(plan['items']), 'pending': plan.get('pending', [])}
