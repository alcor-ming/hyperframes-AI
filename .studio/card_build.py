"""Plan-owned card mounts, built only from installed frozen assets."""

from html import escape
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import component_harness as components
import explainer
import icon_sets
from storage import scoped_path
from visual_plan import (VisualPlanError, card_rows, markdown_structure_lines,
                         plan_scene_rows, scene_projection, validate_card_layout,
                         validate_plan_cards)


START = '<!-- hf-cards:start -->'
END = '<!-- hf-cards:end -->'
MANIFEST = 'runtime/card-build.json'
ET.register_namespace('', 'http://www.w3.org/2000/svg')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


def cards_digest(plan):
    return digest(script_json({sid: row['cards'] for sid, row in plan_scene_rows(plan).items()}).encode())


def card_scenes(project, plan):
    rows = plan_scene_rows(plan)
    return [{key: scene[key] for key in ('id', 'start', 'duration', 'source')}
            for scene in scene_projection(project, plan) if rows[scene['id']]['cards']]


def verify_generated(project, plan, scene_ids=None):
    rows = plan_scene_rows(plan)
    path = scoped_path(project, MANIFEST)
    if not path.is_file():
        if not any(row['cards'] for sid, row in rows.items() if scene_ids is None or sid in scene_ids):
            return
        raise VisualPlanError('Plan cards require cards build before preview registration')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('cards_sha256') != cards_digest(plan):
        raise VisualPlanError('Generated cards differ from Plan; run cards build')
    if manifest.get('scenes') != card_scenes(project, plan):
        raise VisualPlanError('Generated card Scene timing/source changed; run cards build')
    for name, expected in manifest['documents'].items():
        source = scoped_path(project, name).read_text(encoding='utf-8')
        if source.count(START) != 1 or source.count(END) != 1:
            raise VisualPlanError('Generated card markers changed; run cards build')
        if digest(source.split(START, 1)[1].split(END, 1)[0].encode()) != expected:
            raise VisualPlanError('Generated card content changed; edit Plan instead')
    for name, expected in manifest.get('inputs', {}).items():
        if digest(scoped_path(project, name).read_bytes()) != expected:
            raise VisualPlanError(f'Card build input changed: {name}; run cards build')


def replace_block(text, content):
    block = START + '\n' + content + '\n' + END if content else ''
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1 or text.index(END) < text.index(START):
            raise VisualPlanError('Invalid generated card markers')
        before, tail = text.split(START)
        _, after = tail.split(END)
        return before + block + after
    if not content:
        return text
    position = explainer.BodyEnd(text).end
    if position is None:
        raise VisualPlanError('Card build needs a closing body element')
    return text[:position] + block + '\n' + text[position:]


def replace_card(plan, identity, body):
    """Replace one complete card body, never rewrite adjacent Markdown."""
    if not isinstance(body, str) or len(body.encode('utf-8')) > 65536:
        raise VisualPlanError('Card body must be text smaller than 64 KiB')
    boundaries = list(markdown_structure_lines(plan))
    for index, line in enumerate(boundaries):
        match = re.fullmatch(r' {0,3}(`{3,}|~{3,})card ([A-Za-z][A-Za-z0-9_-]*)\s*·\s*(\S.*)', line[0])
        if not match or match[2] != identity:
            continue
        closing = boundaries[index + 1]
        if re.search(r'^ {0,3}(?:`{3,}|~{3,})', body, re.M):
            raise VisualPlanError('Card body cannot contain Markdown fences')
        candidate = plan[:line.end()] + '\n' + body.rstrip() + '\n' + plan[closing.start():]
        plan_scene_rows(candidate)
        return candidate
    raise VisualPlanError(f'Unknown Plan card: {identity}')


def card_bodies(plan):
    result = []
    lines = list(markdown_structure_lines(plan))
    for index, line in enumerate(lines):
        match = re.fullmatch(r' {0,3}(`{3,}|~{3,})card ([A-Za-z][A-Za-z0-9_-]*)\s*·\s*(\S.*)', line[0])
        if match:
            result.append({'id': match[2], 'source': match[3],
                           'body': plan[line.end():lines[index + 1].start()].strip('\n')})
    return result


def installed_kit(project):
    components.verify_installation(project, check_mounts=False)
    lock = components._read_json(project / 'COMPONENT_LOCK.json')
    matches = [item for item in lock['components']
               if item['component_ref'] == 'card-kit@v1' and item.get('asset_kind') == 'module']
    if len(matches) != 1:
        raise VisualPlanError('Install accepted card-kit@v1 before cards build')
    package = scoped_path(project, matches[0]['vendor_path'])
    release = components.validate_component_release(package, allow_unapproved=True)
    return package, release


def svg_content(project, cards, inputs):
    packages = icon_sets.project_packages(project)
    icons = icon_sets.search_icons(packages)
    content, files = {}, set()
    for card in cards:
        values = [value for _, value in card_rows(card)]
        if card.get('figure'):
            values.append(card['figure'])
        for value in values:
            reference = value.get('svg')
            if not reference or reference in content:
                continue
            if reference.startswith('custom:'):
                record = icon_sets.validate_svg_reference(reference, project)
                path = scoped_path(project, record['path'])
                data = path.read_bytes()
                inputs[path] = data
                root = ET.fromstring(data)
                root.set('data-hf-schematic', '')
            else:
                found = [row for row in icons if row['ref'] == reference or
                         '@' not in reference and row['ref'].rsplit('@', 1)[0] == reference]
                if len(found) != 1:
                    raise VisualPlanError(f'Card icon outside unique installed closure: {reference}')
                row = found[0]
                path = Path(row['package_path']) / row['path']
                data = path.read_bytes()
                inputs[path] = data
                root = ET.fromstring(data)
                root.set('data-icon', row['ref'])
                root.set('data-icon-sha256', row['sha256'])
                root.set('stroke', 'currentColor')
                root.set('color', 'var(--appearance-colors-text)')
                root.set('stroke-width', 'var(--appearance-lines-icon-width,2)')
            files.add(path.relative_to(project).as_posix())
            content[reference] = ET.tostring(root, encoding='unicode')
    return content, files, [row['ref'] for row in icons]


def prepare(project, plan, runtime_root, ratio, *, inputs=None):
    """Return proposed bytes; no project writes until every input validates."""
    project = Path(project).resolve()
    inputs = {} if inputs is None else inputs

    def read(relative):
        path = scoped_path(project, relative)
        if path not in inputs:
            inputs[path] = path.read_bytes() if path.exists() else None
        return inputs[path]

    for relative in ('index.html', 'COMPONENT_LOCK.json', 'appearance-lock.json'):
        read(relative)
    rows = plan_scene_rows(plan)
    cards = [card for row in rows.values() for card in row['cards'].values()]
    old_manifest = read(MANIFEST)
    previous = json.loads(old_manifest) if old_manifest is not None else {}
    if not cards and not previous:
        return {}, {'cards': 0, 'scenes': [], 'files': []}
    scenes = scene_projection(project, plan)
    cues = json.loads(read('runtime/cues.json')) if cards else {}
    svg, svg_files, icon_refs = svg_content(project, cards, inputs)
    validate_plan_cards(plan, cues, project=project, closure=svg_files, icon_refs=icon_refs)
    files, grouped = {}, {}
    dependencies = set(svg_files) | {MANIFEST}
    if cards:
        package, release = installed_kit(project)
        entry = (package / release['metadata']['entry']).relative_to(project).as_posix()
        css = (package / 'card-kit.css').relative_to(project).as_posix()
        dependencies.update([entry, css, 'runtime/cues.json', 'appearance-lock.json'])
        for name in ('cues.js', 'appearance.js', 'rolls.js', 'scene-binding.js', 'card-project.js'):
            relative = 'runtime/' + name
            source = Path(runtime_root) / '.studio/runtime' / name
            target = scoped_path(project, relative)
            data = source.read_bytes()
            old = read(relative)
            if old is not None and old != data:
                raise VisualPlanError(f'Frozen runtime differs; explicitly refresh it before card build: {relative}')
            files[relative] = data
            dependencies.add(relative)
    for scene in scenes:
        selected = list(rows[scene['id']]['cards'].values())
        if not selected:
            continue
        for card in selected:
            validate_card_layout(card, ratio)
            for _, item in card_rows(card):
                at = explainer.find_cue(cues, item['cue'])
                if not scene['start'] <= at < scene['start'] + scene['duration']:
                    raise VisualPlanError(f"{card['id']}: cue outside Scene interval")
        source = scene['source']
        scoped_path(project, source)
        grouped.setdefault(source, []).append({
            'id': scene['id'], 'start': scene['start'], 'duration': scene['duration'],
            'inline': source == 'index.html', 'cards': selected})
    for source in sorted(set(grouped) | set(previous.get('documents', {}))):
        if source != 'index.html' and len(grouped.get(source, [])) > 1:
            raise VisualPlanError('Generated card Scenes need distinct composition documents')
        path = scoped_path(project, source)
        original = read(source).decode('utf-8')
        if source in previous.get('documents', {}):
            # Protect only generated text, allowing independent edits elsewhere in the Scene.
            if START not in original or END not in original:
                raise VisualPlanError(f'Generated card block removed outside the builder: {source}')
            owned = original.split(START, 1)[1].split(END, 1)[0]
            if digest(owned.encode()) != previous['documents'][source]:
                raise VisualPlanError(f'Generated card content changed; edit Plan instead: {source}')
        elif START in original or END in original:
            raise VisualPlanError(f'Unowned card markers cannot be overwritten: {source}')
        content = ''
        if source in grouped:
            base = posixpath.dirname(source) or '.'
            relative = lambda name: posixpath.relpath(name, base)
            payload = {'ratio': ratio, 'scenes': grouped[source], 'cues': cues,
                       'svg': svg, 'projectBase': relative('.') + '/'}
            tags = [f'<link rel="stylesheet" href="{escape(relative(css), quote=True)}">']
            tags += [f'<script src="{escape(relative(name), quote=True)}"></script>' for name in
                     ['runtime/cues.js', 'runtime/appearance.js', 'runtime/rolls.js', 'runtime/scene-binding.js', entry]]
            tags += ['<script type="application/json" data-hf-card-plan>' + script_json(payload) + '</script>',
                     f'<script src="{escape(relative("runtime/card-project.js"), quote=True)}"></script>']
            content = '\n'.join(tags)
        files[source] = replace_block(original, content).encode('utf-8')
    original_config = read('project-config.json')
    config = json.loads(original_config) if original_config is not None else {}
    existing = set(config.get('snapshot_dependencies', []))
    old_owned = set(previous.get('owned_dependencies', []))
    owned = (old_owned & dependencies) | (dependencies - existing)
    config['snapshot_dependencies'] = sorted((existing - old_owned) | dependencies)
    files['project-config.json'] = (json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode()
    frozen_inputs = {path.relative_to(project).as_posix(): digest(data)
                     for path, data in inputs.items() if data is not None
                     and (path.relative_to(project).as_posix() in svg_files
                          or path.name in {'cues.json', 'appearance-lock.json'})}
    manifest = {'plan_sha256': digest(plan.encode()), 'cards_sha256': cards_digest(plan), 'inputs': frozen_inputs,
                'scenes': card_scenes(project, plan),
                'owned_dependencies': sorted(owned), 'documents': {
        source: digest(files[source].decode().split(START, 1)[1].split(END, 1)[0].encode()) for source in grouped}}
    files[MANIFEST] = (json.dumps(manifest, indent=2) + '\n').encode()
    return files, {'cards': len(cards), 'scenes': list(grouped), 'files': sorted(files)}


def check_geometry(project, sources, runtime_root, browser=None):
    if not sources:
        return
    command = [os.environ.get('HYPERFRAMES_NODE', 'node'), str(Path(runtime_root) / '.studio/card_kit_check.mjs'),
               str(project), json.dumps(sources)]
    if browser:
        command.append(str(browser))
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=180)
    if result.returncode:
        raise VisualPlanError('Card browser capacity check failed: ' + (result.stderr or result.stdout)[-3000:])


def build(project, plan, runtime_root, ratio, *, browser=None, extra_files=None, expected_before=None):
    """Stage and measure before committing; restore only our own writes on failure."""
    project = Path(project).resolve()
    inputs = {}
    files, report = prepare(project, plan, runtime_root, ratio, inputs=inputs)
    changes = {scoped_path(project, relative): data for relative, data in files.items()}
    changes.update(extra_files or {})
    before = {path: path.read_bytes() if path.exists() else None for path in changes}
    expected = {**before, **inputs, **(expected_before or {})}
    if report['scenes']:
        with tempfile.TemporaryDirectory(prefix='hf-card-build-') as temporary:
            staged = Path(temporary) / 'project'
            # Reject links before copying, including undeclared files in an editable project.
            for path in project.rglob('*'):
                if path.is_symlink():
                    raise VisualPlanError('Card project must not contain symlinks')
            shutil.copytree(project, staged)
            for relative, data in files.items():
                target = scoped_path(staged, relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            check_geometry(staged, report['scenes'], runtime_root, browser)
    written = []
    try:
        if report['cards']:
            components.verify_installation(project, check_mounts=False)
        for path, original in expected.items():
            if (path.read_bytes() if path.exists() else None) != original:
                raise VisualPlanError(f'Card build input changed concurrently: {path.name}')
        for path, data in changes.items():
            current = path.read_bytes() if path.exists() else None
            if current != before[path]:
                raise VisualPlanError(f'Card build input changed concurrently: {path.name}')
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
                path.write_bytes(before[path])
        raise
    return report
