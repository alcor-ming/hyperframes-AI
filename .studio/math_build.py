"""Transactional Plan-owned mathematical mounts from installed frozen assets."""

from html import escape
import json
import os
from pathlib import Path
import posixpath
import shutil
import subprocess
import tempfile

from card_build import digest, script_json
import component_harness as components
import explainer
import math_chain
import math_kit
from storage import scoped_path, snapshot_files
from visual_plan import VisualPlanError, scene_projection

START = '<!-- hf-math:start -->'
END = '<!-- hf-math:end -->'
MANIFEST = 'runtime/math-build.json'


def math_digest(plan):
    rows = math_kit.parse_plan(plan)
    intent = math_chain.parse_plan(plan) if rows else {}
    return digest(script_json({sid: {'math': row, 'intent': intent[sid]} for sid, row in rows.items()}).encode())


def math_scenes(project, plan):
    rows = math_kit.parse_plan(plan)
    return [{key: scene[key] for key in ('id', 'start', 'duration', 'source')}
            for scene in scene_projection(project, plan) if scene['id'] in rows]


def verify_generated(project, plan, scene_ids=None, *, closure=None):
    project = Path(project).resolve()
    rows = math_kit.parse_plan(plan)
    path = scoped_path(project, MANIFEST)
    if not path.is_file():
        if not any(scene_ids is None or sid in scene_ids for sid in rows):
            return
        raise VisualPlanError('Plan math requires math build before preview registration')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('math_sha256') != math_digest(plan):
        raise VisualPlanError('Generated math differs from Plan; run math build')
    if manifest.get('scenes') != math_scenes(project, plan):
        raise VisualPlanError('Generated math Scene timing/source changed; run math build')
    for name, expected in manifest['documents'].items():
        source = scoped_path(project, name).read_text(encoding='utf-8')
        if source.count(START) != 1 or source.count(END) != 1 or source.index(START) > source.index(END):
            raise VisualPlanError('Generated math markers changed; run math build')
        if digest(source.split(START, 1)[1].split(END, 1)[0].encode()) != expected:
            raise VisualPlanError('Generated math content changed; edit Plan instead')
    for name, expected in manifest.get('inputs', {}).items():
        path = scoped_path(project, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise VisualPlanError(f'Math build input changed: {name}; run math build')
    required = {MANIFEST, *manifest['documents'], *manifest.get('inputs', {})}
    actual = snapshot_files(project) if closure is None else closure
    if actual is None or not required.issubset(set(actual)):
        raise VisualPlanError('Generated math inputs are outside the snapshot closure; run math build')
    if rows:
        components.verify_installation(project, check_mounts=False)


def replace_block(text, content):
    block = START + '\n' + content + '\n' + END if content else ''
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1 or text.index(END) < text.index(START):
            raise VisualPlanError('Invalid generated math markers')
        before, tail = text.split(START)
        _, after = tail.split(END)
        return before + block + after
    if not content:
        return text
    position = explainer.BodyEnd(text).end
    if position is None:
        raise VisualPlanError('Math build needs a closing body element')
    return text[:position] + block + '\n' + text[position:]


def prepare(project, plan, runtime_root, ratio, *, inputs=None):
    project = Path(project).resolve()
    inputs = {} if inputs is None else inputs

    def read(relative):
        path = scoped_path(project, relative)
        if path not in inputs:
            inputs[path] = path.read_bytes() if path.exists() else None
        return inputs[path]

    rows = math_kit.parse_plan(plan, ratio=ratio)
    old = read(MANIFEST)
    previous = json.loads(old) if old is not None else {}
    if not rows and not previous:
        return {}, {'items': 0, 'scenes': [], 'files': []}
    read('index.html')
    scenes = scene_projection(project, plan)
    for scene in scenes:
        read(scene['source'])
    if set(rows) - {scene['id'] for scene in scenes}:
        raise VisualPlanError('Math Scene has no project host')
    files, grouped = {}, {}
    dependencies = {MANIFEST}
    frozen = set()
    if rows:
        intents = math_chain.parse_plan(plan)
        components.verify_installation(project, check_mounts=False)
        lock = json.loads(read('COMPONENT_LOCK.json'))
        for component in lock['components']:
            vendor = scoped_path(project, component['vendor_path'])
            frozen.update(path.relative_to(project).as_posix() for path in vendor.rglob('*') if path.is_file())
            frozen.update(binding['path'] for binding in component['bindings'])
        matches = [item for item in lock['components']
                   if item['component_ref'] == 'math-kit@v1' and item.get('asset_kind') == 'module']
        if len(matches) != 1:
            raise VisualPlanError('Install accepted math-kit@v1 before math build')
        package = scoped_path(project, matches[0]['vendor_path'])
        release = components.validate_component_release(package, allow_unapproved=True)
        bound = set()
        for binding in matches[0]['bindings']:
            bound.add(json.loads(read(binding['path'])).get('scene'))
            frozen.add(binding['path'])
        if set(rows) - bound:
            raise VisualPlanError('math-kit@v1 binding does not cover each math Scene')
        entry = (package / release['metadata']['entry']).relative_to(project).as_posix()
        css = (package / 'math-kit.css').relative_to(project).as_posix()
        cues = json.loads(read('runtime/cues.json'))
        frozen.update([entry, css, 'runtime/cues.json', 'appearance-lock.json', 'COMPONENT_LOCK.json'])
        for name in ('cues.js', 'appearance.js', 'rolls.js', 'scene-binding.js', 'math-project.js'):
            relative = 'runtime/' + name
            data = (Path(runtime_root) / '.studio/runtime' / name).read_bytes()
            old = read(relative)
            if old is not None and old != data:
                raise VisualPlanError(f'Frozen runtime differs; explicitly refresh it before math build: {relative}')
            files[relative] = data
            frozen.add(relative)
        for scene in scenes:
            if scene['id'] not in rows:
                continue
            math = rows[scene['id']]
            font = math['font']
            data = read(font['path'])
            if data is None or digest(data) != font['sha256']:
                raise VisualPlanError('Math font hash mismatch')
            frozen.add(font['path'])
            intent = intents[scene['id']]
            previous_time = -1
            for event in intent['cues']:
                at = explainer.find_cue(cues, event['cue'])
                if not scene['start'] <= at < scene['start'] + scene['duration'] or at <= previous_time:
                    raise VisualPlanError('Math cues must increase strictly inside the Scene interval')
                previous_time = at
            grouped.setdefault(scene['source'], []).append({
                'id': scene['id'], 'start': scene['start'], 'duration': scene['duration'],
                'inline': scene['source'] == 'index.html', 'math': math, 'intent': intent})
        dependencies.update(frozen)
        for name in frozen:
            if name not in files and read(name) is None:
                raise VisualPlanError(f'Missing math input: {name}')
    for source in sorted(set(grouped) | set(previous.get('documents', {}))):
        if source != 'index.html' and len(grouped.get(source, [])) > 1:
            raise VisualPlanError('Generated math Scenes need distinct composition documents')
        original = read(source).decode('utf-8')
        if source in previous.get('documents', {}):
            if original.count(START) != 1 or original.count(END) != 1 or original.index(START) > original.index(END):
                raise VisualPlanError(f'Generated math markers changed: {source}')
            owned = original.split(START, 1)[1].split(END, 1)[0]
            if digest(owned.encode()) != previous['documents'][source]:
                raise VisualPlanError(f'Generated math content changed; edit Plan instead: {source}')
        elif START in original or END in original:
            raise VisualPlanError(f'Unowned math markers cannot be overwritten: {source}')
        content = ''
        if source in grouped:
            base = posixpath.dirname(source) or '.'
            relative = lambda name: posixpath.relpath(name, base)
            payload = {'ratio': ratio, 'scenes': grouped[source], 'cues': cues,
                       'projectBase': relative('.') + '/'}
            tags = [f'<link rel="stylesheet" href="{escape(relative(css), quote=True)}">']
            tags += [f'<script src="{escape(relative(name), quote=True)}"></script>' for name in
                     ['runtime/cues.js', 'runtime/appearance.js', 'runtime/rolls.js', 'runtime/scene-binding.js', entry]]
            tags += ['<script type="application/json" data-hf-math-plan>' + script_json(payload) + '</script>',
                     f'<script src="{escape(relative("runtime/math-project.js"), quote=True)}"></script>']
            content = '\n'.join(tags)
        files[source] = replace_block(original, content).encode()
    original_config = read('project-config.json')
    config = json.loads(original_config) if original_config is not None else {}
    existing = set(config.get('snapshot_dependencies', []))
    old_owned = set(previous.get('owned_dependencies', []))
    owned = (old_owned & dependencies) | (dependencies - existing)
    config['snapshot_dependencies'] = sorted((existing - old_owned) | dependencies)
    files['project-config.json'] = (json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode()
    manifest = {'math_sha256': math_digest(plan), 'scenes': math_scenes(project, plan),
                'inputs': {name: digest(files[name] if name in files else read(name)) for name in frozen},
                'owned_dependencies': sorted(owned), 'documents': {
                    source: digest(files[source].decode().split(START, 1)[1].split(END, 1)[0].encode())
                    for source in grouped}}
    files[MANIFEST] = (json.dumps(manifest, indent=2) + '\n').encode()
    return files, {'items': sum(len(row['items']) for row in rows.values()),
                   'scenes': list(grouped), 'files': sorted(files)}


def check_geometry(project, sources, runtime_root, browser=None):
    if not sources:
        return
    command = [os.environ.get('HYPERFRAMES_NODE', 'node'), str(Path(runtime_root) / '.studio/math_kit_check.mjs'),
               str(project), json.dumps(sources)]
    if browser:
        command.append(str(browser))
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=180)
    if result.returncode:
        raise VisualPlanError('Math browser check failed: ' + (result.stderr or result.stdout)[-3000:])


def build(project, plan, runtime_root, ratio, *, browser=None, extra_files=None, expected_before=None):
    project = Path(project).resolve()
    inputs = {}
    files, report = prepare(project, plan, runtime_root, ratio, inputs=inputs)
    changes = {scoped_path(project, relative): data for relative, data in files.items()}
    changes.update(extra_files or {})
    before = {path: path.read_bytes() if path.exists() else None for path in changes}
    expected = {**before, **inputs, **(expected_before or {})}
    if report['scenes']:
        with tempfile.TemporaryDirectory(prefix='hf-math-build-') as temporary:
            staged = Path(temporary) / 'project'
            for path in project.rglob('*'):
                if path.is_symlink():
                    raise VisualPlanError('Math project must not contain symlinks')
            shutil.copytree(project, staged)
            for relative, data in files.items():
                target = scoped_path(staged, relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            check_geometry(staged, report['scenes'], runtime_root, browser)
    written = []
    try:
        if report['items']:
            components.verify_installation(project, check_mounts=False)
        for path, original in expected.items():
            if (path.read_bytes() if path.exists() else None) != original:
                raise VisualPlanError(f'Math build input changed concurrently: {path.name}')
        for path, data in changes.items():
            current = path.read_bytes() if path.exists() else None
            if current != before[path]:
                raise VisualPlanError(f'Math build input changed concurrently: {path.name}')
            if current == data:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
            try:
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
            written.append(path)
    except Exception:
        for path in reversed(written):
            if not path.exists() or path.read_bytes() != changes[path]:
                continue
            if before[path] is None:
                path.unlink()
            else:
                with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(before[path])
                try:
                    os.replace(temporary, path)
                finally:
                    temporary.unlink(missing_ok=True)
        raise
    return report
