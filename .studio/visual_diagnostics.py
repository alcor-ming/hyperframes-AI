"""Read-only, advisory text diagnostics for sampled Studio states."""

from difflib import SequenceMatcher
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import subprocess

from visual_plan import VisualPlanError, markdown_structure_lines, plan_scene_rows


def normalize(text):
    # Preserve signs, decimal points, percentages and units for semantic review.
    punctuation = set('，。！？；：、“”‘’（）【】《》〈〉「」『』,!?;:"\'()[]{}')
    return ''.join(char for char in text if not char.isspace() and char not in punctuation)


def plan_information(text):
    rows, headers, headings = {}, [], []
    screen_starts = set()
    for match in markdown_structure_lines(text):
        line = match[0]
        if re.fullmatch(r'```screen\s*', line):
            screen_starts.add(match.start())
        heading = re.match(r'^#{1,6}\s+(.+)$', line)
        if heading:
            headings.append((match.start(), match.end(), heading[1]))
        if not line.lstrip().startswith('|'):
            continue
        cells = [cell.strip().strip('`') for cell in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
        if '实际表达' in cells:
            headers = cells
        elif headers and len(cells) == len(headers) and re.match(r'^I\d+\b', cells[0]):
            identity = re.match(r'^I\d+', cells[0])[0]
            rows[identity] = dict(zip(headers, cells))
    for index, heading in enumerate(headings):
        identity = re.match(r'`?(I\d+)\b', heading[2])
        if not identity:
            continue
        end = headings[index + 1][0] if index + 1 < len(headings) else len(text)
        block = text[heading[1]:end]
        screen = next((item for item in re.finditer(r'^```screen[^\S\n]*\n(.*?)^```[^\S\n]*$', block, re.M | re.S)
                       if heading[1] + item.start() in screen_starts), None)
        if screen:
            source = re.search(r'^\s*(?:-\s*)?(?:\*\*)?来源\s*[:：](?:\*\*)?\s*(.+)$', block, re.M)
            rows[identity[1]] = {'实际表达': screen[1].rstrip('\n'),
                                 '信息 ID / 来源': source[1].strip() if source else heading[2]}
    scenes = plan_scene_rows(text)
    mapping = {sid: re.findall(r'\bI\d+\b', row.get('使用信息 ID', row.get('信息 ID', '')))
               for sid, row in scenes.items()}
    return rows, mapping


def source_sections(script, research, information):
    sources = {}
    for name, text in [('SCRIPT.md', script), ('RESEARCH.md', research)]:
        text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, count=1, flags=re.S)
        text = re.sub(r'<!-- scene-index:start -->.*?<!-- scene-index:end -->', '', text, flags=re.S)
        chunks = re.split(r'<!--\s*([A-Za-z]+\d+)\s*-->', text)
        if name == 'SCRIPT.md':
            sources[name] = re.sub(r'<!--.*?-->', '', text, flags=re.S)
        for i in range(1, len(chunks), 2):
            identity = chunks[i]
            if name == 'SCRIPT.md' or any(identity in row.get('信息 ID / 来源', '') for row in information.values()):
                sources[f'{name}#{identity}'] = chunks[i + 1]
        if name == 'RESEARCH.md':
            # Only adopted, explicitly referenced research sections are candidates.
            headings = list(re.finditer(r'^#{1,6}\s+(.+)$', text, re.M))
            for index, heading in enumerate(headings):
                title = heading[1].strip()
                if any(title in row.get('信息 ID / 来源', '') for row in information.values()):
                    end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
                    sources[f'{name}#{title}'] = text[heading.end():end]
    return sources


class StaticText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.values = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, text):
        if not self.skip and text.strip():
            self.values.append({'text': text.strip(), 'line': self.getpos()[0]})


def static_inventory(project, dependencies):
    entries = []
    for name in dependencies:
        path = project / name
        if path.suffix in {'.html', '.htm', '.svg'}:
            parser = StaticText()
            parser.feed(path.read_text(encoding='utf-8-sig'))
            entries.extend({'file': name, **entry} for entry in parser.values)
        elif path.suffix == '.json':
            try:
                data = json.loads(path.read_text(encoding='utf-8-sig'))
            except (OSError, ValueError):
                continue

            def strings(value, pointer=''):
                if isinstance(value, str):
                    entries.append({'file': name, 'pointer': pointer, 'text': value})
                elif isinstance(value, dict):
                    for key, item in value.items():
                        strings(item, pointer + '/' + str(key).replace('~', '~0').replace('/', '~1'))
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        strings(item, pointer + '/' + str(index))
            strings(data)
    return entries


def explainer_diagnostics(project, dependencies, lock, plan=""):
    """Static five-layer hints supplement D1; they are never visual acceptance."""
    if not lock or lock.get("mode") not in ("card", "explainer"):
        return {"findings": [], "unverified": []}
    from visual_plan import Composition
    from explainer import installed_assets
    from component_harness import ComponentError, validate_component_release
    from urllib.parse import unquote, urlsplit
    findings, unverified = [], []
    nodes = {}
    for name in dependencies:
        if Path(name).suffix.lower() in {".html", ".htm"}:
            nodes[name] = Composition((project / name).read_text(encoding="utf-8-sig")).nodes
    root = nodes.get("index.html", [])
    layers = [attrs.get("data-hf-layer") for _, attrs in root]
    expected = {"background", "stage", "overlay", "text"}
    for layer in sorted(expected - set(layers)):
        findings.append({"kind": "explainer_layer_missing", "file": "index.html", "layer": layer})
    captions = [(name, attrs) for name, entries in nodes.items() for _, attrs in entries
                if attrs.get("data-hf-layer") == "captions"]
    enabled = lock.get("selection", {}).get("captions", False)
    if len(captions) != int(enabled) or captions and captions[0][0] != "index.html":
        findings.append({"kind": "captions_lock_mismatch", "enabled": enabled, "hosts": len(captions)})
    for name, entries in nodes.items():
        if name == "index.html":
            continue
        if any("data-card-layers" in attrs for _, attrs in entries):
            try:
                validate_component_release((project / name).parent, allow_unapproved=True)
            except (ComponentError, ValueError, OSError) as exc:
                findings.append({"kind": "card_component_invalid", "file": name, "detail": str(exc)})
            continue
        if any("data-composition-id" in attrs for _, attrs in entries):
            local = {attrs.get("data-hf-layer") for _, attrs in entries}
            for layer in sorted({"stage", "overlay", "text"} - local):
                findings.append({"kind": "explainer_layer_missing", "file": name, "layer": layer})
    try:
        assets = installed_assets(project)
    except (ValueError, OSError, ComponentError) as exc:
        assets = {}
        unverified.append({"reason": "asset_closure_invalid", "detail": str(exc)})
    allowed = {ref: (project / item["vendor_path"] / item["metadata"]["entry"]).resolve()
               for ref, item in assets.items() if item["metadata"].get("kind") == "media"
               and Path(item["metadata"]["entry"]).suffix.lower() == ".mp3"}
    for name, entries in nodes.items():
        for tag, attrs in entries:
            character = attrs.get("data-character-ref")
            if character and (
                    character not in assets or assets[character]["metadata"].get("kind") != "character"):
                findings.append({"kind": "character_asset_outside_closure", "file": name, "ref": character})
            if tag != "audio" or attrs.get("data-audio-role") == "voice":
                continue
            ref, src = attrs.get("data-asset-ref"), attrs.get("src", "")
            url = urlsplit(src)
            path = (project / name).parent / unquote(url.path)
            valid = not url.scheme and not url.netloc and path.resolve() in allowed.values()
            if ref:
                valid = valid and allowed.get(ref) == path.resolve()
            if not valid:
                findings.append({"kind": "sound_asset_outside_closure", "file": name, "ref": ref, "src": src})
    for scene, row in (plan_scene_rows(plan) if plan and lock["mode"] == "explainer" else {}).items():
        for field in ("主载体", "事件与层"):
            if not row.get(field, "").strip():
                findings.append({"kind": "explainer_plan_missing", "scene": scene, "field": field})
    unverified.append({"reason": "dynamic_hosts_and_refs_require_browser_review"})
    return {"findings": findings, "unverified": unverified}


def checked_exceptions(entries, sources, scene_ids):
    if not isinstance(entries, list):
        raise VisualPlanError('Exceptions must be a JSON array of scene, text, source, reason objects')
    for entry in entries:
        if (not isinstance(entry, dict) or set(entry) != {'scene', 'text', 'source', 'reason'}
                or any(not isinstance(entry.get(key), str) or not entry[key].strip()
                                              for key in ('scene', 'text', 'source', 'reason'))
                or entry['scene'] not in scene_ids or entry['source'] not in sources
                or not normalize(entry['text'])
                or normalize(entry['text']) not in normalize(sources[entry['source']])):
            raise VisualPlanError('Exception needs an exact source-backed fragment, existing Scene and confirmation reason')
    return entries


def copy_match(text, sources):
    best = None
    for source, original in sources.items():
        reference = normalize(original)
        if not reference:
            continue
        # ponytail: quadratic matching; chunk by source Anchor if large sources become slow.
        blocks = SequenceMatcher(None, reference, text, autojunk=False).get_matching_blocks()
        score = sum(block.size for block in blocks) / len(text)
        if best is None or score > best['coverage']:
            best = {'source': source, 'coverage': score, 'continuous': max(block.size for block in blocks) / len(text)}
    return best


def resolve_information(text, choices, information):
    """Assign text to one Plan block by exact string evidence only; ambiguity stays unresolved."""
    value = normalize(text)
    blocks = {info: information[info]['实际表达'] for info in choices if info in information}
    if not value or not blocks:
        return ''
    exact = [info for info, planned in blocks.items()
             if value == normalize(planned) or any(value == normalize(line) for line in planned.splitlines())]
    if exact:
        return exact[0] if len(exact) == 1 else ''
    contained = [info for info, planned in blocks.items() if value in normalize(planned)]
    return contained[0] if len(contained) == 1 else ''


def text_diagnostics(samples, script, research, plan, *, minimum=20, similarity=0.8, exceptions=None, scenes=None,
                     scene_ids=None, mode=None):
    information, mapping = plan_information(plan)
    outside = {sid: ids for sid, ids in mapping.items() if scene_ids is not None and sid not in scene_ids}
    if scene_ids is not None:
        mapping = {sid: ids for sid, ids in mapping.items() if sid in scene_ids}
        selected = {info for ids in mapping.values() for info in ids}
        information = {info: row for info, row in information.items() if info in selected}
    sources = source_sections(script, research, information)
    exceptions = checked_exceptions(exceptions or [], sources, mapping)
    groups, findings, unverified, excluded, source_groups = {}, [], [], [], {}
    covered, failed = set(), set()
    for sample in sorted(samples, key=lambda item: item['time']):
        active = {scene['id'] for scene in scenes or []
                  if scene['start'] <= sample['time'] < scene['start'] + scene['duration']}
        if not sample.get('ready'):
            failed.update(active)
            failed.update(item.get('scene') for item in sample.get('texts', []))
            continue
        covered.update(active)
        for item in sample.get('texts', []):
            if mode in ('card', 'explainer') and item.get('layer') != 'text':
                continue
            scene, info = item.get('scene', ''), item.get('info', '')
            if scene in outside:
                continue
            if scene not in mapping:
                unverified.append({'reason': 'unmapped_scene', 'time': sample['time'], 'text': item['text']})
                continue
            covered.add(scene)
            text = item['text'].strip()
            if not text:
                continue
            choices = mapping[scene]
            if not info:
                info = resolve_information(text, choices, information)
            if info not in choices or info not in information:
                info = ''
            # Unresolved text keeps its element identity instead of merging into one Scene string.
            key = (scene, info, '' if info else item.get('selector', '') or text)
            group = groups.setdefault(key, {'parts': [], 'locations': [], 'times': []})
            # Deduplicate persistent and progressively revealed text across seek samples.
            if not any(normalize(text) in normalize(part) for part in group['parts']):
                group['parts'] = [part for part in group['parts'] if normalize(part) not in normalize(text)]
                group['parts'].append(text)
            location = item.get('selector', '')
            if location not in group['locations']:
                group['locations'].append(location)
            group['times'].append(sample['time'])
    for (scene, info, _), group in groups.items():
        parts = group['parts']
        if info:
            # Several DOM nodes may form one block; compare them in Plan order, not reveal order.
            expected = normalize(information[info]['实际表达'])
            parts = sorted(parts, key=lambda part: (expected.find(normalize(part)) % (len(expected) + 1)))
        text = ''.join(parts)
        normalized = normalize(text)
        location = {'scene': scene, 'info': info or None, 'text': text,
                    'selectors': group['locations'], 'start': min(group['times']), 'end': max(group['times'])}
        if not info:
            unverified.append({**location, 'reason': 'semantic_mapping_requires_review'})
        else:
            planned = information[info]['实际表达']
            expected = normalize(planned)
            if expected != normalized:
                remaining = iter(expected)
                # ponytail: half-length is a relative shortening hint; semantic equivalence needs review.
                truncated = bool(normalized) and len(normalized) < len(expected) and (
                    all(char in remaining for char in normalized) or len(normalized) <= len(expected) / 2)
                findings.append({**location, 'kind': 'plan_information_truncated' if truncated else 'plan_implementation_difference', 'planned': planned,
                                 'source': information[info].get('信息 ID / 来源', '')})
        for entry in exceptions:
            if entry['scene'] == scene and normalize(entry['text']) in normalized:
                normalized = normalized.replace(normalize(entry['text']), '')
                excluded.append(entry)
        if info and normalized:
            reference = information[info].get('信息 ID / 来源', '')
            anchors = re.findall(r'\b[A-Z]+\d+\b', reference)
            for anchor in anchors:
                if anchor == info:
                    continue
                key = next((key for key in sources if key.endswith('#' + anchor)), None)
                if key:
                    source_groups.setdefault(key, []).append((location, normalized))
        if len(normalized) < minimum:
            continue
        best = copy_match(normalized, sources)
        if best and best['coverage'] >= similarity:
            findings.append({**location, 'kind': 'suspected_copy', **best,
                             'semantic_review': 'Check negation, numbers, units, attribution and necessary quotation; no automatic verdict'})
    for source, members in source_groups.items():
        if len(members) < 2:
            continue
        ordered = sorted(members, key=lambda item: item[0]['start'])
        combined = ''.join(dict.fromkeys(text for _, text in ordered))
        if len(combined) < minimum or any(combined == text for _, text in ordered):
            continue
        best = copy_match(combined, {source: sources[source]})
        if best and best['coverage'] >= similarity:
            findings.append({'kind': 'suspected_split_copy', 'scenes': list(dict.fromkeys(item['scene'] for item, _ in ordered)),
                             'text': combined, 'members': [item for item, _ in ordered], **best,
                             'semantic_review': 'Source-anchor aggregation is a hint, not proof of one semantic unit'})
    unresolved = {scene for scene, info, _ in groups if not info}
    for scene, identities in mapping.items():
        for info in identities:
            if (scene, info, '') in groups:
                continue
            row = information.get(info)
            entry = {'scene': scene, 'info': info, 'source': row.get('信息 ID / 来源', '') if row else ''}
            if not row:
                unverified.append({**entry, 'reason': 'plan_information_undefined'})
            elif scene in unresolved:
                unverified.append({**entry, 'reason': 'plan_information_mapping_unresolved'})
            elif scene in covered and scene not in failed:
                findings.append({**entry, 'kind': 'plan_information_missing', 'planned': row['实际表达']})
            else:
                unverified.append({**entry, 'reason': 'plan_information_not_observed'})
    for info, row in information.items():
        if not any(info in identities for identities in mapping.values()):
            unverified.append({'info': info, 'reason': 'plan_information_not_observed', 'source': row.get('信息 ID / 来源', '')})
    unverified.append({'reason': 'external_or_unresolved_adopted_sources_require_review'})
    return {'findings': findings, 'unverified': unverified, 'confirmed_exceptions': excluded,
            'out_of_scope': [{'scene': sid, 'information_ids': ids, 'reason': 'outside_reference_scope'}
                             for sid, ids in outside.items()],
            'sources': list(sources), 'observed_groups': len(groups)}


def parameters(args):
    values = {'step': args.step, 'width': args.width, 'timeout_ms': args.timeout_ms}
    if (any(not math.isfinite(value) or value <= 0 for value in values.values())
            or not 160 <= args.width <= 4096 or not 100 <= args.timeout_ms <= 30000
            or args.minimum < 1 or not math.isfinite(args.similarity) or not 0 < args.similarity <= 1):
        raise VisualPlanError('Invalid diagnostic parameters: positive finite values, similarity <=1, width 160..4096, timeout 100..30000')
    return values


def probe(request, node='node'):
    try:
        result = subprocess.run([node, str(Path(__file__).with_name('visual_probe.mjs'))],
                                input=json.dumps(request), capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=1800)
        if result.returncode:
            raise VisualPlanError(f'Studio sampling failed: {result.stderr[:1000]}')
        data = json.loads(result.stdout)
        if not isinstance(data, dict) or not isinstance(data.get('samples'), list):
            raise VisualPlanError('Studio sampling returned invalid evidence')
        return data
    except (OSError, subprocess.TimeoutExpired, ValueError, VisualPlanError) as error:
        return {'samples': [], 'timeline': [],
                'unverified': [{'reason': 'studio_sampling_unavailable', 'detail': str(error)}]}
