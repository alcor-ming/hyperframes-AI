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


class VisualPlanError(ValueError):
    pass


class Composition(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def scene_projection(project, plan_text):
    """Timing comes from executable HTML; intent comes from the existing Plan table."""
    rows = {}
    headers = []
    for line in plan_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "Scene":
            headers = cells
        elif headers and re.fullmatch(r"S\d+", cells[0]):
            rows.setdefault(cells[0], {}).update(dict(zip(headers, cells)))
    scenes = []
    for _, attrs in Composition((project / "index.html").read_text(encoding="utf-8")).nodes:
        scene_id = attrs.get("data-scene-id", attrs.get("id", ""))
        if not re.fullmatch(r"S\d+", scene_id):
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
        raise VisualPlanError("Plan Scene table and index.html timed Scene IDs must match exactly")
    return sorted(scenes, key=lambda scene: scene["start"])


def layout_projection(project, plan_text, scene_ids):
    rows = set(re.findall(r"^\|\s*(S\d+)\s*\|", plan_text, re.MULTILINE))
    nodes = Composition((project / "index.html").read_text(encoding="utf-8")).nodes
    ids = {a.get("data-scene-id", a.get("id")) for _, a in nodes}
    if not scene_ids or len(set(scene_ids)) != len(scene_ids) or set(scene_ids) - rows or set(scene_ids) - ids:
        raise VisualPlanError("Layout sample needs unique --scene IDs present in both Plan and HTML")
    canvases = [a for _, a in nodes if "data-width" in a and "data-height" in a]
    if not canvases or any(not a[k].isdigit() or not 0 < int(a[k]) <= 16384 for a in canvases for k in ("data-width", "data-height")):
        raise VisualPlanError("Layout sample needs a positive data-width/data-height canvas")
    return [{"id": sid, "source": "index.html"} for sid in scene_ids]


def validate_dependencies(project, *, layout=False):
    """Check literal local references; browser QA must also check dynamic asset loads."""
    project = project.resolve()
    visited = set()

    def visit(path):
        if layout and any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(project)):
            raise VisualPlanError(f"Layout dependency cannot be a symlink: {path}")
        path = path.resolve()
        if not path.is_relative_to(project) or not path.is_file():
            raise VisualPlanError(f"Dependency is missing or outside snapshot: {path}")
        if path in visited:
            return
        visited.add(path)
        if path.suffix not in {".html", ".css", ".js", ".mjs"}:
            return
        text = path.read_text(encoding="utf-8")
        refs = []
        if path.suffix == ".html":
            for tag, attrs in Composition(text).nodes:
                if layout and (tag in {"audio", "video", "iframe", "object", "embed", "hyperframes-player"} or "data-composition-src" in attrs):
                    raise VisualPlanError("Layout samples use semantic placeholders, not media or compositions")
                if layout and ("srcset" in attrs or "imagesrcset" in attrs):
                    raise VisualPlanError("Layout samples use a single local src, not responsive image candidates")
                refs.extend(attrs[key] for key in ("src", "data-composition-src", "poster") if attrs.get(key))
                if tag == "link" and attrs.get("href"):
                    refs.append(attrs["href"])
        refs += re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", text)
        if layout:
            refs += re.findall(r"@import\s+['\"]([^'\"]+)['\"]", text)
        refs += re.findall(r"(?:\bfrom\s*|\bimport\s*\(?\s*|\bfetch\s*\(\s*)['\"]([^'\"]+)['\"]", text)
        for ref in refs:
            if ref.startswith(("#", "data:", "blob:")):
                continue
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or ref.startswith("/"):
                raise VisualPlanError(f"Non-local dependency in {path.name}: {ref}")
            visit(path.parent / unquote(parsed.path))

    visit(project / "index.html")
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
