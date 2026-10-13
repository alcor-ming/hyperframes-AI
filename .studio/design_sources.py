"""Pinned, non-executable upstream source caches outside card closures."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
from urllib.parse import urlsplit

import designs


def identity(url, commit):
    if not isinstance(url, str):
        raise designs.DesignError('Source URL must be a string')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or not parsed.path.strip('/')):
        raise designs.DesignError('Source requires an HTTPS repository URL without credentials')
    if not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit):
        raise designs.DesignError('Source requires a full lowercase commit SHA')
    return hashlib.sha256(url.encode()).hexdigest()[:24] + '@' + commit


def cache_path(url, commit, *, root=None, config=None, create=False):
    name = identity(url, commit)
    user = designs.user_root(root, config, create=create)
    if user is None:
        raise designs.DesignError('Configure design_root before loading external sources')
    sources = user / '.sources'
    if sources.is_symlink() or (sources / name).is_symlink():
        raise designs.DesignError('Source cache must not be linked')
    if create:
        sources.mkdir(exist_ok=True)
    return sources / name


def manifest(url, commit, *, root=None, config=None):
    directory = cache_path(url, commit, root=root, config=config)
    try:
        result = json.loads((directory / 'source.json').read_text(encoding='utf-8'))
        files = designs._tree_files(directory / 'files')
        if result['url'] != url or result['commit'] != commit or files != {
                path: item['sha256'] for path, item in result['files'].items()}:
            raise ValueError('source content mismatch')
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise designs.DesignError(f'Invalid or missing source cache: {error}') from error
    return result


def _archive(url, commit, directory, output):
    # Fetch objects only: no checkout, hooks, submodules, filters, or upstream scripts.
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
    args = ['git', '-c', 'credential.helper=', '-c', 'protocol.allow=never',
            '-c', 'protocol.https.allow=always', '-c', 'http.followRedirects=false']
    def run(*command):
        return subprocess.run([*args, *command], cwd=directory, env=env, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180).stdout
    try:
        run('init', '--bare', '.')
        run('fetch', '--depth=1', '--no-tags', url, commit)
        if run('rev-parse', 'FETCH_HEAD').decode().strip() != commit:
            raise designs.DesignError('Fetched commit differs from requested source')
        run('archive', '--format=tar', '--output=' + str(output), commit)
    except (subprocess.SubprocessError, OSError) as error:
        raise designs.DesignError('Unable to fetch the pinned HTTPS source repository') from error


def source_add(url, commit, *, root=None, config=None):
    destination = cache_path(url, commit, root=root, config=config, create=True)
    if destination.exists():
        return {**manifest(url, commit, root=root, config=config), 'path': str(destination)}
    with tempfile.TemporaryDirectory(prefix='.source-', dir=destination.parent) as temporary:
        temporary = Path(temporary)
        git = temporary / 'git'
        git.mkdir()
        archive = temporary / 'source.tar'
        _archive(url, commit, git, archive)
        staging = temporary / 'cache'
        files = staging / 'files'
        files.mkdir(parents=True)
        with tarfile.open(archive) as packed:
            seen = set()
            for item in packed:
                name = item.name.rstrip('/')
                target = designs._safe_child(files, name)
                if name in seen or (not item.isdir() and not item.isfile()):
                    raise designs.DesignError('Source archive contains duplicate or linked entries')
                seen.add(name)
                if item.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with packed.extractfile(item) as source, target.open('xb') as output:
                        shutil.copyfileobj(source, output)
        hashes = designs._tree_files(files)
        licenses = [p for p in hashes if Path(p).name.lower().startswith(('license', 'copying', 'notice', 'ofl'))]
        # License locations are evidence, not an automatic legal classification.
        records = {p: {'sha256': sha, 'license': 'unreviewed',
                       'license_files': [license for license in licenses
                                         if Path(p).is_relative_to(Path(license).parent)]}
                   for p, sha in hashes.items()}
        result = {'schema_version': 1, 'url': url, 'commit': commit, 'files': records}
        (staging / 'source.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        staging.rename(destination)
    for path in destination.rglob('*'):
        path.chmod(0o555 if path.is_dir() else 0o444)
    destination.chmod(0o555)
    return {**result, 'path': str(destination)}


def validate_record(source):
    if not isinstance(source, dict) or source.get('kind') != 'external':
        raise designs.DesignError('Invalid external borrowed source')
    identity(source.get('url', ''), source.get('commit'))
    files = source.get('files')
    if not isinstance(files, dict) or not files:
        raise designs.DesignError('External borrowed source requires per-file provenance')
    for path, item in files.items():
        designs._safe_child(Path('/source'), path)
        if (not isinstance(item, dict) or not re.fullmatch('[0-9a-f]{64}', str(item.get('sha256', '')))
                or not isinstance(item.get('license'), str) or not item['license'].strip()
                or item['license'] == 'unreviewed' or not isinstance(item.get('attribution'), str)
                or not item['attribution'].strip()):
            raise designs.DesignError('External files require SHA256, reviewed license and attribution')


def compare(source, commit=None, *, root=None, config=None):
    validate_record(source)
    current = manifest(source['url'], commit or source['commit'], root=root, config=config)
    changes = {}
    for path, old in source['files'].items():
        new = current['files'].get(path)
        if new is None or new['sha256'] != old['sha256']:
            changes[path] = {'recorded': old['sha256'], 'source': new['sha256'] if new else None}
    return {'source': {'url': source['url'], 'commit': current['commit']},
            'source_changed': bool(changes), 'files': changes}
