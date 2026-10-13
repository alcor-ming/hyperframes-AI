"""Copy successful delivery files into an append-only, hash-verified export shelf."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import tempfile

from component_harness import package_write_lock
from storage import scoped_path
from windows_runtime import validate_review_path


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def component(value):
    if (not isinstance(value, str) or value in {'', '.', '..'}
            or re.search(r'[\x00-\x1f/\\:<>"|?*]', value) or value.endswith((' ', '.'))
            or re.fullmatch(r'(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?', value)):
        raise ValueError('Invalid export directory component')
    return value


def publish(export_root, work, variant, files, *, series=None, revision=1, review=False):
    if review:
        raise ValueError('Review/test-work cannot publish exports')
    if type(revision) is not int or revision < 1 or not isinstance(files, dict) or not files:
        raise ValueError('Export requires a positive revision and delivery files')
    if set(files) - {'video', 'cover'}:
        raise ValueError('Unknown export media role')
    root = Path(export_root).absolute()
    for path in (root, Path(work), Path(variant)):
        validate_review_path(path)
    work, variant = Path(work).resolve(), Path(variant).resolve()
    if not variant.is_relative_to(work):
        raise ValueError('Variant must belong to Work')
    sources, hashes = {}, {}
    for role, source in files.items():
        source = Path(source).absolute()
        if not source.is_relative_to(variant):
            raise ValueError('Export source must belong to Variant')
        source = scoped_path(variant, source.relative_to(variant).as_posix())
        if not source.is_file() or source.stat().st_nlink != 1:
            raise ValueError('Export source must be an unlinked regular file')
        if source.suffix.lower() not in ({'.mp4'} if role == 'video' else {'.png', '.jpg', '.jpeg', '.webp'}):
            raise ValueError('Unexpected export media extension')
        sources[role], hashes[role] = source, sha256(source)
    leaf = scoped_path(root, '/'.join(map(component, (series or '未分系列', work.name, variant.name))))
    if leaf.is_relative_to(variant) or variant.is_relative_to(leaf):
        raise ValueError('Export shelf must be separate from Variant source')
    leaf.mkdir(parents=True, exist_ok=True)
    with package_write_lock(scoped_path(leaf, '.export.lock')):
        index = scoped_path(leaf, '.exports.json')
        if index.exists() and index.stat().st_nlink != 1:
            raise ValueError('Linked export index')
        entries = json.loads(index.read_text()) if index.exists() else []
        if not isinstance(entries, list):
            raise ValueError('Invalid export index')
        entry = next((item for item in entries if item['hashes'] == hashes), None)
        if entry is None:
            sequence = max((item['sequence'] for item in entries), default=0) + 1
            prefix = f'{variant.name}-r{revision:03d}-e{sequence:03d}'
            entry = {'sequence': sequence, 'revision': revision, 'hashes': hashes,
                     'files': {role: prefix + '-' + role + source.suffix.lower() for role, source in sources.items()}}
            entries.append(entry)
            # An interrupted index write must not reserve a shared temporary name forever.
            stream = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=leaf,
                                                  prefix='.exports-', suffix='.pending.json', delete=False)
            temporary = Path(stream.name)
            try:
                with stream:
                    json.dump(entries, stream, ensure_ascii=False, indent=2)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, index)
            finally:
                temporary.unlink(missing_ok=True)
        for role, source in sources.items():
            target = scoped_path(leaf, entry['files'][role])
            temporary = scoped_path(leaf, entry['files'][role] + '.partial')
            if target.exists():
                if (temporary.exists() and target.stat().st_nlink == 2
                        and os.path.samefile(temporary, target) and sha256(target) == hashes[role]):
                    temporary.unlink()
                if target.stat().st_nlink != 1 or sha256(target) != hashes[role]:
                    raise ValueError('Existing export differs; refusing to overwrite')
                continue
            if temporary.exists():
                if temporary.stat().st_nlink != 1 or sha256(temporary) != hashes[role]:
                    raise ValueError('Incomplete export copy requires inspection')
            else:
                try:
                    with source.open('rb') as incoming, temporary.open('xb') as outgoing:
                        shutil.copyfileobj(incoming, outgoing)
                        outgoing.flush()
                        os.fsync(outgoing.fileno())
                except Exception:
                    temporary.unlink(missing_ok=True)
                    raise
            if sha256(temporary) != hashes[role]:
                temporary.unlink()
                raise ValueError('Source changed while copying export')
            # Lock excludes another publisher; exclusive creation also protects existing user files.
            try:
                os.link(temporary, target)
            except FileExistsError:
                raise ValueError('Export destination appeared; refusing to overwrite') from None
            temporary.unlink()
        return {'directory': str(leaf), **entry}
