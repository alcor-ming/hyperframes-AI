"""Language-aware dependency extraction using the tool's pinned syntax parsers."""
from functools import lru_cache
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess


class DependencyScanError(ValueError):
    pass


class HTMLDependencies(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.refs, self.units = [], []
        self.active = None
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'base' and 'href' in attrs:
            raise DependencyScanError('HTML base href changes the dependency root and is not supported')
        self.refs.extend({'value': attrs[key], 'kind': 'executable' if tag in ('script', 'iframe')
                          or key == 'data-composition-src' else 'html'}
                         for key in ('src', 'data-composition-src', 'poster') if attrs.get(key))
        if tag == 'link' and attrs.get('href'):
            executable = bool({'stylesheet', 'modulepreload'} & set(attrs.get('rel', '').lower().split())) or attrs.get('as', '').lower() == 'script'
            self.refs.append({'value': attrs['href'], 'kind': 'executable' if executable else 'html'})
        if attrs.get('style'):
            self.units.append({'kind': 'css', 'text': '* {' + attrs['style'] + '}'})
        for key, value in pairs:
            if key.startswith('on') and value:
                self.units.append({'kind': 'js', 'mode': 'handler', 'text': value})
        if tag == 'style':
            self.active = {'kind': 'css', 'text': ''}
        elif tag == 'script':
            kind = attrs.get('type', '').strip().lower()
            if kind == 'importmap':
                raise DependencyScanError('HTML importmap changes dependency resolution and is not supported')
            if not attrs.get('src') and kind in ('', 'module', 'text/javascript', 'application/javascript',
                                                'text/ecmascript', 'application/ecmascript'):
                self.active = {'kind': 'js', 'mode': 'module' if kind == 'module' else 'script', 'text': ''}
        if self.active is not None:
            self.units.append(self.active)

    def handle_data(self, data):
        if self.active is not None:
            self.active['text'] += data

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.active = None


@lru_cache(maxsize=128)
def _parse(payload, node, module_root):
    environment = os.environ.copy()
    if module_root:
        environment['HYPERFRAMES_DEPENDENCY_MODULE_ROOT'] = module_root
    try:
        result = subprocess.run([node, str(Path(__file__).with_suffix('.cjs'))], input=payload,
                                capture_output=True, text=True, encoding='utf-8', timeout=60,
                                cwd=Path(__file__).parent, env=environment)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise DependencyScanError(f'Dependency parser unavailable: {error}') from error
    if result.returncode:
        raise DependencyScanError(f'Dependency syntax parsing failed: {result.stderr.strip()}')
    try:
        return json.loads(result.stdout)
    except ValueError as error:
        raise DependencyScanError('Dependency parser returned invalid output') from error


def references(text, suffix):
    refs = []
    if suffix in ('.html', '.htm'):
        html = HTMLDependencies(text)
        refs, units = html.refs, html.units
    else:
        units = [{'kind': 'css' if suffix == '.css' else 'js',
                  'mode': 'module' if suffix == '.mjs' else 'auto', 'text': text}]
    if not units:
        return refs, []
    result = _parse(json.dumps(units), os.environ.get('HYPERFRAMES_NODE', 'node'),
                    os.environ.get('HYPERFRAMES_DEPENDENCY_MODULE_ROOT', ''))
    return refs + result['refs'], result['dynamic']
