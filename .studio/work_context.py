"""An atomic Work/Variant pair per named command context."""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
from pathlib import Path
import re
import tempfile

from windows_runtime import validate_review_path

_identity = ContextVar('work_context', default='default')
_snapshot = ContextVar('work_context_snapshot', default=None)


def path(runtime):
    return Path(runtime) / 'contexts' / (_identity.get() + '.json')


def read(runtime):
    cached = _snapshot.get()
    if cached is not None and cached[0] == Path(runtime):
        return dict(cached[1])
    target = path(runtime)
    validate_review_path(target)
    if target.exists():
        if target.stat().st_nlink != 1:
            raise ValueError('Linked Current context')
        data = json.loads(target.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or set(data) != {'work', 'variant'}:
            raise ValueError('Invalid Current context')
        if any(value is not None and (not isinstance(value, str) or '/' in value or '\\' in value)
               for value in data.values()) or (data['variant'] is not None and data['work'] is None):
            raise ValueError('Invalid Current pair')
        return data
    data = {'work': None, 'variant': None}
    if _identity.get() == 'default':
        for key in data:
            legacy = Path(runtime) / ('current-' + key)
            validate_review_path(legacy)
            if legacy.is_file():
                data[key] = legacy.read_text(encoding='utf-8').strip() or None
        if data['work'] is None:
            data['variant'] = None
    return data


def write(runtime, work, variant):
    if work is None:
        variant = None
    data = {'work': work, 'variant': variant}
    target = path(runtime)
    validate_review_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.current-', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    if _snapshot.get() is not None:
        _snapshot.set((Path(runtime), data))
    # Legacy files are projections only; once a pair exists they are never read.
    if _identity.get() == 'default':
        for key, value in data.items():
            legacy = Path(runtime) / ('current-' + key)
            validate_review_path(legacy)
            if value is None:
                legacy.unlink(missing_ok=True)
            else:
                if legacy.exists() and legacy.stat().st_nlink != 1:
                    raise ValueError('Linked legacy Current projection')
                legacy.write_text(value + '\n', encoding='utf-8')


@contextmanager
def command(runtime, identity):
    if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', identity):
        raise ValueError('Context must be a short alphanumeric session id')
    token = _identity.set(identity)
    cached = _snapshot.set(None)
    try:
        _snapshot.set((Path(runtime), read(runtime)))
        yield
    finally:
        _snapshot.reset(cached)
        _identity.reset(token)
