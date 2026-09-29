"""Read-only layout samples and executable Visual Plans."""

from functools import partial
from html.parser import HTMLParser
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from dependency_scan import DependencyScanError, references


class VisualPlanError(ValueError):
    pass


SCENE_ID = re.compile(r"S[0-9]+[A-Z]*")
PLAN_FORMAT = '3.5.2'


def plan_cue(value):
    if value.strip().startswith('{'):
        try:
            query = json.loads(value)
            if not isinstance(query, dict) or not isinstance(query.get('token'), str) or not query['token'].strip() or set(query) - {'token', 'nth', 'within', 'edge'}:
                raise ValueError('expected cue query')
            return query
        except ValueError as error:
            raise VisualPlanError(f'invalid cue query: {value}') from error
    match = re.fullmatch(r'(.+?)#([1-9][0-9]*)', value.strip())
    return {'token': match[1], 'nth': int(match[2])} if match else {'token': value.strip()}


def plan_source(value):
    return f'SCRIPT.md#{value}' if re.fullmatch(r'P[0-9]+', value) else value


def card_content(value, identity):
    match = re.fullmatch(r'((?:\\.|[^@\[])*)\s+@([^\[\]]+?)(?:\s+\[([^\[\]]+)\])?', value)
    if not match or not match[1].strip() or not match[2].strip():
        raise VisualPlanError(f'{identity}: card text requires text @cue [SVG reference]; escape @ and [ in text')
    text = re.sub(r'\\([\\@\[\]])', r'\1', match[1].strip())
    svg = match[3]
    if svg and not re.fullmatch(r'(?:custom:.+\.svg|[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+(?:@[A-Za-z0-9_.-]+)?)', svg):
        raise VisualPlanError(f'{identity}: invalid SVG reference {svg}')
    return {'text': text, 'cue': plan_cue(match[2]), 'svg': svg}


def parse_card(header, lines):
    match = re.fullmatch(r'card ([A-Za-z][A-Za-z0-9_-]*)\s*·\s*(\S.*)', header)
    if not match:
        raise VisualPlanError('card requires card <ID> · <source anchor>')
    card = {'id': match[1], 'source': plan_source(match[2]), 'lines': []}
    latest = None
    for line in lines:
        if not line.strip():
            continue
        if line.startswith('- '):
            card['lines'].append(card_content(line[2:], card['id']))
            latest = card['lines'][-1]
            continue
        if line[:1].isspace():
            key, separator, value = line.strip().partition(':')
            if not separator or key not in {'key', 'indexKey'} or latest is None or key in latest:
                raise VisualPlanError(f"{card['id']}: invalid or duplicate per-line card field {key}")
            latest[key] = card_content(value.strip(), card['id'])
            continue
        latest = None
        key, separator, value = line.partition(':')
        value = value.strip()
        if not separator or key not in {'preset', 'area', 'title', 'note', 'exit', 'emphasis', 'input', 'inputLabel', 'outputLabel', 'figure'} or key in card or not value:
            raise VisualPlanError(f"{card['id']}: invalid or duplicate card field {key}")
        if key == 'figure':
            figure = re.fullmatch(r'(custom:.+\.svg)\s+@(.+)', value)
            if not figure:
                raise VisualPlanError(f"{card['id']}: figure requires custom:path.svg @cue")
            card[key] = {'svg': figure[1], 'cue': plan_cue(figure[2])}
        else:
            card[key] = card_content(value, card['id']) if key in {'title', 'note', 'input', 'inputLabel', 'outputLabel'} else plan_cue(value) if key in {'exit', 'emphasis'} else value
    if not re.fullmatch(r'F0[1-8]', card.get('preset', '')):
        raise VisualPlanError(f"{card['id']}: preset must be F01-F08")
    if not re.fullmatch(r'(?:full|left|right|top|bottom|[1-9][0-9]*(?:px)?\s*[x×]\s*[1-9][0-9]*(?:px)?)', card.get('area', '')):
        raise VisualPlanError(f"{card['id']}: area requires a region name or positive pixel dimensions")
    for slot in ('input', 'inputLabel', 'outputLabel', 'figure'):
        if slot in card and card['preset'] not in ({'F03', 'F05', 'F08'} if slot == 'figure' else {'F07'}):
            raise VisualPlanError(f"{card['id']}: {card['preset']} does not support {slot}")
    for item in card['lines']:
        for slot, preset in (('key', 'F06'), ('indexKey', 'F04')):
            if slot in item and card['preset'] != preset:
                raise VisualPlanError(f"{card['id']}: {card['preset']} does not support {slot}")
    for slot, item in card_rows(card):
        if item.get('svg') and (slot in {'note', 'inputLabel'} or str(slot).endswith(':indexKey')
                                or isinstance(slot, int) and card['preset'] in {'F05', 'F06', 'F07'}):
            raise VisualPlanError(f"{card['id']}: {card['preset']} does not support SVG in {slot}")
    if not any(card.get(key) for key in ('title', 'lines', 'note', 'input')):
        raise VisualPlanError(f"{card['id']}: card needs text")
    return card


def card_rows(card):
    rows = [(key, card[key]) for key in ('inputLabel', 'input', 'outputLabel', 'title') if key in card]
    for number, item in enumerate(card['lines'], 1):
        rows.extend((f'{number}:{key}', item[key]) for key in ('indexKey', 'key') if key in item)
        rows.append((number, item))
    return rows + ([('note', card['note'])] if 'note' in card else [])


def validate_card_layout(card, ratio):
    """Approved allocation and count limits; real text overflow is checked in-browser."""
    if ratio not in {'16:9', '9:16'}:
        raise VisualPlanError('Card ratio must be 16:9 or 9:16')
    width, height = (1920, 1080) if ratio == '16:9' else (1080, 1920)
    area = card['area']
    x = y = 72
    w, h = width - 144, height - 144
    if area in {'left', 'right'}:
        w = (width - 192) // 2
        if area == 'right':
            x = width // 2 + 24
    elif area in {'top', 'bottom'}:
        h = (height - 192) // 2
        if area == 'bottom':
            y = height // 2 + 24
    elif area != 'full':
        match = re.fullmatch(r'([1-9][0-9]*)(?:px)?\s*[x×]\s*([1-9][0-9]*)(?:px)?', area)
        if not match:
            raise VisualPlanError(f"{card['id']}: invalid area")
        w, h = map(int, match.groups())
        if w > width - 144 or h > height - 144:
            raise VisualPlanError(f"{card['id']}: pixel area exceeds safe frame")
    limit = 6
    if h < 500:
        limit = 2
    elif w < 600 or card['preset'] in {'F05', 'F07'} or 'figure' in card:
        limit = 4
    elif card['preset'] in {'F04', 'F06'} and h < 900:
        limit = 4
    if len(card['lines']) > limit:
        raise VisualPlanError(f"{card['id']}: card overflow: {len(card['lines'])} lines exceeds capacity {limit}")
    return {'x': x, 'y': y, 'width': w, 'height': h, 'max_lines': limit}


def validate_plan_cards(plan_text, cues, *, project, closure, icon_refs=(), scene_ids=None):
    """Validate resolved card cues and SVGs against the frozen dependency closure."""
    from explainer import find_cue
    rows = plan_scene_rows(plan_text)
    project = Path(project).resolve()
    paths = {(project / item).resolve() for item in closure}
    for sid, row in rows.items():
        if scene_ids is not None and sid not in scene_ids:
            continue
        for card in row['cards'].values():
            values = [value for _, value in card_rows(card)]
            values += [card['figure']] if 'figure' in card else []
            values += [{'cue': card[key]} for key in ('exit', 'emphasis') if key in card]
            for value in values:
                try:
                    find_cue(cues, value['cue'])
                except (ValueError, TypeError, KeyError) as error:
                    raise VisualPlanError(f"{card['id']}: card cue resolution failed: {error}") from error
                svg = value.get('svg')
                if not svg:
                    continue
                if svg.startswith('custom:'):
                    path = (project / svg[7:]).resolve()
                    if not path.is_relative_to(project) or path not in paths or not path.is_file():
                        raise VisualPlanError(f"{card['id']}: SVG reference outside snapshot closure: {svg}")
                    from icon_sets import validate_svg_reference
                    from component_harness import ComponentError
                    try:
                        validate_svg_reference(svg, project)
                    except ComponentError as error:
                        raise VisualPlanError(f"{card['id']}: unsafe SVG: {error}") from error
                elif svg not in icon_refs and ('@' in svg or len([ref for ref in icon_refs if ref.rsplit('@', 1)[0] == svg]) != 1):
                    raise VisualPlanError(f"{card['id']}: SVG icon reference outside snapshot closure: {svg}")
    return rows


class Composition(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def markdown_structure_lines(text):
    """Yield structural lines and fence boundaries with offsets into the source."""
    fence = None
    for match in re.finditer(r'^.*$', text, re.M):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', match[0])
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
                yield match
            continue
        if marker:
            fence = marker[1]
            yield match
            continue
        yield match


def plan_scene_rows(plan_text):
    """Parse Scene-local design only; overview tables are never design authority."""
    metadata = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)', plan_text, re.S)
    try:
        supported = metadata and json.loads(metadata[1]).get('plan_format') == PLAN_FORMAT
    except (ValueError, AttributeError):
        supported = False
    if not supported:
        raise VisualPlanError(f'Animation Plan 格式不支持: expected plan_format {PLAN_FORMAT}')
    rows, information = {}, {}
    screen_count = card_count = 0
    for match in markdown_structure_lines(plan_text):
        if re.fullmatch(r' {0,3}(?:`{3,}|~{3,})screen\s*', match[0]):
            screen_count += 1
        if re.match(r' {0,3}(?:`{3,}|~{3,})card\b', match[0]):
            card_count += 1
        cells = {cell.strip() for cell in match[0].strip().strip('|').split('|')}
        if match[0].lstrip().startswith('|') and cells.intersection({'实际表达', '使用信息 ID', '信息 ID', '原 Scene ID'}):
            raise VisualPlanError('Animation Plan 格式不支持: legacy design tables')
    headings = [m for m in markdown_structure_lines(plan_text) if re.match(r'^## ', m[0])]
    for index, heading in enumerate(headings):
        identity = re.fullmatch(r'## (S[0-9]+[A-Z]*)(?:\s+.*)?', heading[0])
        if not identity:
            continue
        sid = identity[1]
        if sid in rows:
            raise VisualPlanError(f"Duplicate Plan Scene ID: {sid}")
        end = headings[index + 1].start() if index + 1 < len(headings) else len(plan_text)
        body = plan_text[heading.end():end]
        row = {'Scene': sid, 'body': body, 'screens': {}, 'cards': {}, 'events': [], 'exceptions': []}
        current, fence, collected = None, None, []
        for line in body.splitlines():
            marker = re.fullmatch(r' {0,3}(`{3,}|~{3,})(.*)', line)
            if fence:
                if marker and marker[1][0] == fence[0][0] and len(marker[1]) >= len(fence[0]) and not marker[2].strip():
                    kind = fence[1]
                    if kind == 'screen':
                        if not current or current in information:
                            raise VisualPlanError(f"{sid}: screen needs a unique ### I<number> heading")
                        value = {'实际表达': '\n'.join(collected), '信息 ID / 来源': plan_source(source)}
                        information[current] = value
                        row['screens'][current] = value
                    elif kind.startswith('card'):
                        card = parse_card(kind, collected)
                        identity = card['id']
                        if identity in information:
                            raise VisualPlanError(f'{sid}: duplicate information/card ID {identity}')
                        row['cards'][identity] = card
                        value = {'实际表达': '\n'.join(item['text'] for _, item in card_rows(card)), '信息 ID / 来源': card['source']}
                        information[identity] = row['screens'][identity] = value
                        for number, item in card_rows(card):
                            row['events'].append({'cue': item['cue'], 'layer': 4, 'target': f'{identity}:{number}', 'change': 'text_reveal', 'card': identity, 'row': number, 'info': identity, 'derived': True})
                        if 'figure' in card:
                            row['events'].append({'cue': card['figure']['cue'], 'layer': 2, 'target': f'{identity}:figure', 'change': 'figure_reveal', 'card': identity, 'derived': True})
                        if 'emphasis' in card:
                            row['events'].append({'cue': card['emphasis'], 'layer': 2, 'target': identity, 'change': 'emphasis', 'card': identity, 'derived': True})
                        if 'exit' in card:
                            row['events'].append({'cue': card['exit'], 'layer': 2, 'target': identity, 'change': 'exit', 'card': identity, 'derived': True})
                    elif kind == 'rhythm':
                        raise VisualPlanError('Animation Plan 格式不支持: use an event table, not rhythm JSON')
                    fence, collected = None, []
                else:
                    collected.append(line)
                continue
            if marker:
                fence = (marker[1], marker[2].strip())
                continue
            info = re.fullmatch(r'### (I[0-9]+)(?:\s+.*)?', line)
            if line.startswith('### '):
                current = info[1] if info else None
                source = line.partition('·')[2].strip() or current or ''
            origin = re.match(r'\*\*来源[:：]\*\*\s*(.*)', line)
            if origin and current:
                source = origin[1]
            if line.lstrip().startswith('|'):
                cells = [cell.strip() for cell in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
                if cells[0] == '例外':
                    if len(cells) != 5 or cells[3] not in {'pause', 'talking_head'} or not all(cells[1:]):
                        raise VisualPlanError(f'{sid}: invalid event exception row')
                    row['exceptions'].append(dict(start_cue=plan_cue(cells[1]), end_cue=plan_cue(cells[2]), kind=cells[3], reason=cells[4]))
                elif cells[0] not in {'cue', 'Cue'} and not all(re.fullmatch(r':?-+:?', cell) for cell in cells):
                    if len(cells) != 4 or cells[1] not in {'2', '3', '4'} or not cells[0] or not cells[3]:
                        raise VisualPlanError(f'{sid}: event row requires cue | layer (2/3/4) | target | change')
                    row['events'].append(dict(cue=plan_cue(cells[0]), layer=int(cells[1]), target=cells[2], change=cells[3]))
        if fence:
            raise VisualPlanError(f'{sid}: unclosed {fence[1]} fence')
        row['信息 ID'] = ', '.join(row['screens'])
        rows[sid] = row
    if not rows:
        raise VisualPlanError("Animation Plan 格式不支持: expected Scene sections (## S01) with embedded screen blocks")
    if screen_count + card_count != len(information):
        raise VisualPlanError('Animation Plan 格式不支持: screen blocks must belong to a Scene section')
    for sid, row in rows.items():
        refs = [m[1] for line in markdown_structure_lines(row['body'])
                if (m := re.fullmatch(r'\*\*延续信息[:：]\*\*\s*(.*)', line[0]))]
        for identity in re.findall(r'\b[A-Za-z][A-Za-z0-9_-]*\b', ' '.join(refs)):
            if identity not in information:
                raise VisualPlanError(f'{sid}: unknown continuation information ID {identity}')
            row['screens'][identity] = information[identity]
        row['信息 ID'] = ', '.join(row['screens'])
    from math_kit import parse_plan as parse_math_kit
    try:
        math_blocks = parse_math_kit(plan_text)
    except ValueError as error:
        raise VisualPlanError(str(error)) from error
    is_math = json.loads(metadata[1]).get('series_binding', {}).get('spec') == 'math-rap'
    if math_blocks and not is_math:
        raise VisualPlanError('math blocks require math-rap series binding')
    for sid, block in math_blocks.items():
        rows[sid]['math'] = block
    if is_math:
        from math_chain import parse_plan
        try:
            contracts = parse_plan(plan_text)
        except ValueError as error:
            raise VisualPlanError(str(error)) from error
        for sid, contract in contracts.items():
            rows[sid]['math_plan'] = contract
            kinds = {item['id']: item['kind'] for item in math_blocks.get(sid, {}).get('items', [])}
            for event in contract['cues']:
                for action in ('reveal', 'remove'):
                    for target in event[action]:
                        layers = ([4] if kinds[target] in ('formula', 'equals') else [2, 4]) if target in kinds else [2]
                        rows[sid]['events'].extend({'cue': event['cue'], 'layer': layer, 'target': target,
                                                   'change': 'math_' + action, 'derived': True} for layer in layers)
    return rows


def reference_projection(plan_text):
    return [{"id": sid, "source": "", "intent": row} for sid, row in plan_scene_rows(plan_text).items()]


def scene_projection(project, plan_text, scene_ids=None):
    """Timing comes from executable HTML; intent comes from Scene sections."""
    rows = plan_scene_rows(plan_text)
    if scene_ids is not None:
        if len(scene_ids) != 1 or scene_ids[0] not in rows:
            raise VisualPlanError("Scene reference requires exactly one existing Plan Scene ID")
        rows = {scene_ids[0]: rows[scene_ids[0]]}
    scenes = []
    for _, attrs in Composition((project / "index.html").read_text(encoding="utf-8")).nodes:
        scene_id = attrs.get("data-scene-id", attrs.get("id", ""))
        if not SCENE_ID.fullmatch(scene_id):
            continue
        try:
            start, duration = float(attrs["data-start"]), float(attrs["data-duration"])
            reading = start + float(attrs.get("data-reading-time", str(duration / 2)))
            if not all(math.isfinite(n) for n in (start, duration, reading)) or start < 0 or duration <= 0 or not start <= reading <= start + duration:
                raise ValueError()
        except (KeyError, ValueError):
            raise VisualPlanError(f"{scene_id} needs finite data-start/data-duration and local data-reading-time")
        scenes.append({"id": scene_id, "start": start, "duration": duration, "reading": reading,
                       "intent": rows.get(scene_id, {}), "source": attrs.get("data-composition-src", "index.html")})
    ids = [s["id"] for s in scenes]
    if not rows or set(ids) != set(rows) or len(ids) != len(set(ids)):
        raise VisualPlanError("Plan Scene sections and index.html timed Scene IDs must match exactly")
    return sorted(scenes, key=lambda scene: scene["start"])


def layout_projection(project, plan_text, scene_ids):
    rows = set(plan_scene_rows(plan_text))
    nodes = Composition((project / "index.html").read_text(encoding="utf-8")).nodes
    ids = {a.get("data-scene-id", a.get("id")) for _, a in nodes}
    if not scene_ids or len(set(scene_ids)) != len(scene_ids) or set(scene_ids) - rows or not set(scene_ids).intersection(ids):
        raise VisualPlanError("Layout sample needs unique Plan --scene IDs and at least one demonstrated Scene in HTML")
    canvases = [a for _, a in nodes if "data-width" in a and "data-height" in a]
    if not canvases or any(not a[k].isdigit() or not 0 < int(a[k]) <= 16384 for a in canvases for k in ("data-width", "data-height")):
        raise VisualPlanError("Layout sample needs a positive data-width/data-height canvas")
    return [{"id": sid, "source": "index.html"} for sid in scene_ids]


def validate_dependencies(project, *, layout=False, entry="index.html", check_path=None):
    """Check closure using HTML document bases, or project-root hosting for JS entries.

    Dynamic loads and nonstandard embedding still require runtime restrictions/QA.
    """
    project = project.resolve()
    visited = set()
    scanned = set()
    dynamic_loads = set()

    def visit(path, document_base=None):
        if check_path is not None:
            check_path(path)
        if layout and any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(project)):
            raise VisualPlanError(f"Layout dependency cannot be a symlink: {path}")
        path = path.resolve()
        if not path.is_relative_to(project) or not path.is_file():
            raise VisualPlanError(f"Dependency is missing or outside snapshot: {path}")
        document_base = path.parent if path.suffix in {".html", ".htm"} else document_base or project
        context = (path, document_base)
        if context in scanned:
            return
        scanned.add(context)
        visited.add(path)
        if path.suffix not in {".html", ".htm", ".css", ".js", ".mjs"}:
            return
        text = path.read_text(encoding="utf-8")
        if path.suffix in {".html", ".htm"}:
            for tag, attrs in Composition(text).nodes:
                if layout and (tag in {"audio", "video", "iframe", "object", "embed", "hyperframes-player"}
                               or "data-composition-src" in attrs or "data-card-source" in attrs):
                    raise VisualPlanError("Layout samples use semantic placeholders, not media or compositions")
                if layout and ("srcset" in attrs or "imagesrcset" in attrs):
                    raise VisualPlanError("Layout samples use a single local src, not responsive image candidates")
        try:
            refs, dynamic = references(text, path.suffix)
        except DependencyScanError as error:
            raise VisualPlanError(f"{path.name}: {error}") from error
        if dynamic:
            dynamic_loads.add(path.relative_to(project).as_posix())
        for reference in refs:
            ref = reference["value"]
            if reference["kind"] in {"import", "executable"} and urlsplit(ref).scheme.lower() in {"data", "blob"}:
                raise VisualPlanError(f"Opaque executable dependency in {path.name}: {ref}")
            if ref.startswith(("#", "data:", "blob:")):
                continue
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or ref.startswith("/"):
                raise VisualPlanError(f"Non-local dependency in {path.name}: {ref}")
            base = document_base if reference["kind"] == "fetch" else path.parent
            visit(base / unquote(parsed.path), document_base)

    visit(project / entry)
    if dynamic_loads:
        declared = False
        for filename, key in (("project-config.json", "snapshot_dependencies"), ("asset.json", "dependencies")):
            metadata_path = project / filename
            if not metadata_path.is_file():
                continue
            visit(metadata_path)
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
                entries = metadata.get(key) if isinstance(metadata, dict) else None
            except ValueError as error:
                raise VisualPlanError(f"Invalid dependency declaration: {filename}") from error
            if entries is None:
                continue
            if not isinstance(entries, list) or not all(isinstance(ref, str) and ref for ref in entries):
                raise VisualPlanError(f"{filename}: {key} must be a list of local files")
            declared = True
            for ref in entries:
                if Path(ref).is_absolute() or ".." in Path(ref).parts or "\\" in ref or ":" in ref:
                    raise VisualPlanError(f"Non-local declared dependency: {ref}")
                visit(project / ref)
        if not declared:
            raise VisualPlanError("Dynamic import/fetch requires explicit snapshot_dependencies or asset dependencies: "
                                  + ", ".join(sorted(dynamic_loads)) + "; runtime network restrictions and QA remain required")
    return sorted(p.relative_to(project).as_posix() for p in visited)


def source_changes(before, after):
    def files(root):
        result = {}
        for path in root.rglob("*"):
            if path.is_file():
                with path.open("rb") as stream:
                    result[path.relative_to(root).as_posix()] = hashlib.file_digest(stream, "sha256").hexdigest()
        return result
    a, b = files(before), files(after)
    return [name for name in sorted(a.keys() | b.keys()) if a.get(name) != b.get(name)]


def serve(preview, hf_dist=None, port=0, review=None, *, layout=False):
    scripts = {} if layout else {name: Path(hf_dist).resolve() / name for name in ("hyperframes-player.global.js", "hyperframe.runtime.iife.js")}
    if not all(p.is_file() for p in scripts.values()):
        raise VisualPlanError("--hyperframes-dist must contain the installed player and runtime bundles")
    if layout:
        data = json.loads((preview / "visual-plan.json").read_text(encoding="utf-8"))
        scope = escape(" / ".join(s["id"] for s in data["scenes"]))
        page = (f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>布局样段 {scope}</title><style>body{{margin:0;font:16px system-ui;letter-spacing:0}}'
                'header{padding:12px;overflow-wrap:anywhere}iframe{display:block;width:100%;height:calc(100dvh - 90px);border:0}</style>'
                f'<header>布局样段 | {scope} | 动效与媒体尚未实现<br>'
                f'{escape(preview.name)} | {"Review | " if review else ""}生产播放与渲染尚未验证</header>'
                '<iframe title="静态布局样段" sandbox="allow-scripts allow-same-origin" src="source-snapshot/index.html"></iframe></html>').encode()
    else:
        page = Path(__file__).with_name("visual_plan.html").read_bytes()

    class Handler(SimpleHTTPRequestHandler):
        def send_head(self):
            target = Path(self.translate_path(self.path)).resolve()
            if not target.is_relative_to(preview.resolve()):
                self.send_error(403)
                return None
            header = self.headers.get("Range")
            if not header or not target.is_file():
                return super().send_head()
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", header)
            size = target.stat().st_size
            if not match or not any(match.groups()) or size == 0:
                self.send_error(416)
                return None
            first, last = match.groups()
            start = int(first) if first else max(0, size - int(last))
            end = min(int(last), size - 1) if first and last else size - 1
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return None
            stream = target.open("rb")
            stream.seek(start)
            self.remaining = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(str(target)))
            self.send_header("Content-Length", str(self.remaining))
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            return stream

        def copyfile(self, source, outputfile):
            try:
                if not hasattr(self, "remaining"):
                    return super().copyfile(source, outputfile)
                while self.remaining:
                    chunk = source.read(min(self.remaining, 1024 * 1024))
                    if not chunk:
                        break
                    outputfile.write(chunk)
                    self.remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass  # A new media seek can cancel the previous byte range.

        def do_GET(self):
            name = urlsplit(self.path).path
            if name == "/":
                content, kind = page, "text/html; charset=utf-8"
            elif name == "/session.json":
                content = json.dumps({"review": os.environ.get("HYPERFRAMES_AI_REVIEW") == "1",
                                      "version": os.environ.get("HYPERFRAMES_AI_VERSION", "development"),
                                      "candidate": review}).encode()
                kind = "application/json"
            elif name.removeprefix("/hf/") in scripts and name.startswith("/hf/"):
                content, kind = scripts[name.removeprefix("/hf/")].read_bytes(), "text/javascript"
            else:
                target = Path(self.translate_path(self.path)).resolve()
                if not target.is_relative_to(preview.resolve()):
                    self.send_error(403)
                    return
                return super().do_GET()
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("Accept-Ranges", "bytes")
            policy = "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; connect-src 'self' blob:"
            if layout:
                policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; media-src 'none'; connect-src 'none'; object-src 'none'"
            self.send_header("Content-Security-Policy", policy)
            super().end_headers()

    with ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(preview))) as server:
        print(f"http://127.0.0.1:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
