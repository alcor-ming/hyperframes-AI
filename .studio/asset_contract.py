"""The small module/media source-to-frozen-package contract."""

from __future__ import annotations

from pathlib import Path
import json
import math
import os
import re
import shutil
import stat
import subprocess
import warnings
import xml.etree.ElementTree as ET

import component_harness as COMPONENT
from visual_plan import VisualPlanError, validate_dependencies


ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PRIVATE_NAMES = {"__pycache__", "node_modules", "venv", "cache", "caches", "private", "secrets",
                 "credentials", "tmp", "temp", "works", "requests", "review", "drafts"}
PRIVATE_FILES = {"work.md", "script.md", "research.md", "package.md", "animation_plan.md", "variant.yaml"}
DEVICE = re.compile(r"^(?:con|prn|aux|nul|com[1-9\u00b9\u00b2\u00b3]|lpt[1-9\u00b9\u00b2\u00b3])(?:\.|$)", re.I)
RASTER = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}
SVG_TAGS = set("svg g defs path rect circle ellipse line polyline polygon text tspan title desc "
               "linearGradient radialGradient stop clipPath mask use symbol".split())
SVG_ATTRS = set("id class version x y x1 y1 x2 y2 dx dy width height viewBox preserveAspectRatio "
                "d points cx cy r rx ry fx fy fr pathLength fill fill-opacity fill-rule stroke "
                "stroke-width stroke-opacity stroke-linecap stroke-linejoin stroke-miterlimit "
                "stroke-dasharray stroke-dashoffset opacity transform gradientUnits gradientTransform "
                "spreadMethod offset stop-color stop-opacity clip-path clip-rule clipPathUnits mask "
                "maskUnits maskContentUnits href font-family font-size font-weight font-style text-anchor "
                "dominant-baseline alignment-baseline textLength lengthAdjust vector-effect "
                "shape-rendering color display visibility overflow".split())

KINDS = {"module", "media", "theme", "background", "motion"}
DECLARATIVE = {"theme", "background", "motion"}


def asset_requires_runtime(metadata):
    return metadata.get("kind", metadata.get("asset_type")) not in DECLARATIVE | {"media"}


def _fields(value, allowed, required=(), label="asset"):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        raise COMPONENT.ComponentError(f"Invalid {label} fields; allowed: {sorted(allowed)}")


def validate_reference(value):
    _fields(value, {"ref", "kind", "package_sha256"}, {"ref", "kind", "package_sha256"}, "asset reference")
    if (not isinstance(value["ref"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*@v[1-9][0-9]*", value["ref"])
            or not isinstance(value["kind"], str) or value["kind"] not in KINDS
            or not isinstance(value["package_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["package_sha256"])):
        raise COMPONENT.ComponentError("Asset reference requires exact ref, kind and package_sha256")


def validate_parameter(value, spec):
    _fields(spec, {"type", "default", "minimum", "maximum", "enum"}, {"type", "default"}, "parameter schema")
    kinds = {"string": str, "number": (int, float), "integer": int, "boolean": bool}
    kind = spec["type"]
    if not isinstance(kind, str) or kind not in kinds:
        raise COMPONENT.ComponentError("Unsupported parameter type")
    if not isinstance(value, kinds[kind]) or (kind in {"number", "integer"} and (isinstance(value, bool) or not math.isfinite(value))):
        raise COMPONENT.ComponentError("Parameter value has incorrect type")
    for bound in ("minimum", "maximum"):
        if bound in spec and (kind not in {"number", "integer"} or type(spec[bound]) not in {int, float} or not math.isfinite(spec[bound])):
            raise COMPONENT.ComponentError("Invalid parameter numeric bounds")
    if (("minimum" in spec and value < spec["minimum"]) or ("maximum" in spec and value > spec["maximum"])):
        raise COMPONENT.ComponentError("Parameter value is outside allowed range")
    if "enum" in spec and (not isinstance(spec["enum"], list) or not spec["enum"] or value not in spec["enum"]):
        raise COMPONENT.ComponentError("Parameter value is outside allowed enum")
    if isinstance(value, str) and re.search(r"[<>;{}]|url\s*\(|expression\s*\(|javascript:", value, re.I):
        raise COMPONENT.ComponentError("Executable expressions are not permitted in declarations")


def _declaration(directory, metadata):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise COMPONENT.ComponentError(f"Duplicate declaration key: {key}")
            result[key] = value
        return result

    try:
        payload = json.loads((directory / metadata["entry"]).read_text(encoding="utf-8"), object_pairs_hook=unique,
                             parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (ValueError, OSError, UnicodeError) as exc:
        raise COMPONENT.ComponentError("Invalid asset declaration JSON") from exc
    return validate_declaration(payload, metadata, directory, check_defaults=True)


def validate_declaration(payload, metadata, directory, *, check_defaults=False):
    """Validate both package defaults and resolved, explicitly overridden declarations."""
    kind = metadata["kind"]
    if kind == "theme":
        _fields(payload, {"tokens", "fonts"}, {"tokens"}, "Theme")
        _fields(payload["tokens"], {"typography", "colors", "surface", "border", "radius", "shadow", "lines"}, label="Theme tokens")
        fonts = payload.get("fonts", [])
        if not isinstance(fonts, list):
            raise COMPONENT.ComponentError("Theme fonts must be an array")
        for font in fonts:
            _fields(font, {"family", "path", "license", "style", "weight"}, {"family", "path", "license"}, "Theme font")
            if not isinstance(font["family"], str) or not font["family"].strip():
                raise COMPONENT.ComponentError("Font requires a family")
            if font.get("style", "normal") not in ("normal", "italic", "oblique"):
                raise COMPONENT.ComponentError("Font style must be normal, italic or oblique")
            weight = font.get("weight", "normal")
            if not (type(weight) is int and 1 <= weight <= 1000):
                if not isinstance(weight, str) or not re.fullmatch(r"normal|bold|[1-9][0-9]{0,3}(?: [1-9][0-9]{0,3})?", weight):
                    raise COMPONENT.ComponentError("Invalid font weight or variable weight range")
                if weight not in ("normal", "bold"):
                    weights = list(map(int, weight.split()))
                    if max(weights) > 1000 or weights != sorted(weights):
                        raise COMPONENT.ComponentError("Invalid font weight or variable weight range")
            for key in ("path", "license"):
                if _relative(directory, font[key]) not in metadata.get("dependencies", []):
                    raise COMPONENT.ComponentError("Font files and license must be declared dependencies")
    elif kind == "background":
        _fields(payload, {"renderer", "parameters", "readability"}, {"renderer", "parameters"}, "Background")
        if payload["renderer"] not in ("solid", "transparent"):
            raise COMPONENT.ComponentError("Dynamic Background renderers are not supported yet")
        _fields(payload["parameters"], {"color"} if payload["renderer"] == "solid" else set(),
                {"color"} if payload["renderer"] == "solid" else set(), "Background parameters")
        if payload["renderer"] == "solid" and not re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", str(payload["parameters"]["color"])):
            raise COMPONENT.ComponentError("Solid Background needs a hex color")
        if "readability" in payload:
            _fields(payload["readability"], {"foreground", "regions"}, label="Background readability")
            if payload["readability"].get("foreground", "any") not in ("light", "dark", "any"):
                raise COMPONENT.ComponentError("Invalid foreground readability condition")
    else:
        _fields(payload, {"slots", "reduced_motion"}, {"slots", "reduced_motion"}, "Motion")
        for group in (payload["slots"], payload["reduced_motion"]):
            _fields(group, {"reveal", "emphasis", "exit", "transition"}, label="Motion slots")
            for settings in group.values():
                _fields(settings, {"duration", "easing", "x", "y", "scale", "stagger"}, {"duration", "easing"}, "Motion slot")
                for key, value in settings.items():
                    if key == "easing":
                        if not isinstance(value, str) or not re.fullmatch(r"(?:none|linear|power[1-4]\.(?:in|out|inOut)|(?:sine|expo|circ|back|bounce)\.(?:in|out|inOut))", value):
                            raise COMPONENT.ComponentError("Unsupported Motion easing")
                    elif type(value) not in {int, float} or not math.isfinite(value) or (key in {"duration", "stagger", "scale"} and value < 0):
                        raise COMPONENT.ComponentError("Invalid Motion numeric value")
    def inspect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"mode", "modes", "layout", "cue", "script", "background", "motion"}:
                    raise COMPONENT.ComponentError(f"Declaration contains forbidden field: {key}")
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
        elif isinstance(value, str):
            if re.search(r"[<>;{}]|url\s*\(|expression\s*\(|javascript:", value, re.I):
                raise COMPONENT.ComponentError("Executable expressions are not permitted in declarations")
        elif value is not None and type(value) not in {bool, int, float}:
            raise COMPONENT.ComponentError("Invalid declaration value")
    inspect(payload)
    for path, spec in metadata["parameters"].items():
        prefixes = {"theme": ("tokens.",), "background": ("parameters.",),
                    "motion": ("slots.", "reduced_motion.")}
        if not path.startswith(prefixes[kind]):
            raise COMPONENT.ComponentError(f"Asset identity or dependency field cannot be overridden: {path}")
        current = payload
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                raise COMPONENT.ComponentError(f"Parameter path is not in the declaration: {path}")
            current = current[part]
        validate_parameter(current, spec)
        if check_defaults and current != spec["default"]:
            raise COMPONENT.ComponentError(f"Parameter default differs from declaration: {path}")
    return payload


def _schema2(directory, metadata):
    _fields(metadata, {"schema_version", "id", "version", "kind", "entry", "contract_version", "parameters",
                      "compatibility", "dependencies", "asset_dependencies", "runtime", "usage", "example", "license",
                      "files", "description", "source_url", "rights"},
            {"contract_version", "parameters", "compatibility"}, "schema 2 manifest")
    if type(metadata["contract_version"]) is not int or metadata["contract_version"] != 1:
        raise COMPONENT.ComponentError("Unsupported asset contract_version")
    compatibility = metadata["compatibility"]
    _fields(compatibility, {"ratios"}, label="asset compatibility")
    ratios = compatibility.get("ratios", [])
    if not isinstance(ratios, list) or any(ratio not in ("9:16", "16:9", "4:3", "1:1") for ratio in ratios):
        raise COMPONENT.ComponentError("Invalid asset compatible ratios")
    parameters = metadata["parameters"]
    if not isinstance(parameters, dict):
        raise COMPONENT.ComponentError("Asset parameters must be a path/schema object")
    for path, spec in parameters.items():
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*", path):
            raise COMPONENT.ComponentError("Invalid parameter path")
        validate_parameter(spec.get("default") if isinstance(spec, dict) else None, spec)
    dependencies = metadata.get("asset_dependencies", [])
    if not isinstance(dependencies, list):
        raise COMPONENT.ComponentError("Asset dependencies must be an array of exact references")
    seen = set()
    for dependency in dependencies:
        validate_reference(dependency)
        if dependency["ref"] in seen or dependency["ref"] == f"{metadata['id']}@v{metadata['version']}":
            raise COMPONENT.ComponentError("Duplicate or cyclic asset dependency")
        seen.add(dependency["ref"])
        if metadata["kind"] in DECLARATIVE and dependency["kind"] != "media":
            raise COMPONENT.ComponentError("Declarative assets can only depend on Media, not other appearance or executable assets")
    if metadata["kind"] in DECLARATIVE:
        if metadata.get("runtime"):
            raise COMPONENT.ComponentError("Declarative assets cannot require runtime libraries")
        _declaration(directory, metadata)


def _check_name(name):
    if (not name or name in {".", ".."} or name.startswith(".") or name[-1:] in {".", " "}
            or any(ord(char) < 32 or char in '<>:"\\|?*' for char in name)
            or DEVICE.match(name) or name.casefold() in PRIVATE_NAMES | PRIVATE_FILES):
        raise COMPONENT.ComponentError(f"Unsafe or private asset path: {name!r}")


def _check_link(path):
    info = path.lstat()
    if (stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400
            or (stat.S_ISREG(info.st_mode) and info.st_nlink != 1)):
        raise COMPONENT.ComponentError(f"Asset paths cannot use links: {path}")


def _root(directory):
    directory = Path(directory).absolute()
    try:
        for path in (directory, *directory.parents):
            _check_link(path)
        if not directory.is_dir():
            raise COMPONENT.ComponentError(f"Asset directory is missing: {directory}")
    except OSError as exc:
        raise COMPONENT.ComponentError(f"Cannot read asset directory: {directory}") from exc
    return directory


def _check_dependency(directory, path):
    """Inspect each lexical step before the shared resolver follows a dependency."""
    try:
        parts = path.relative_to(directory).parts
        current = directory
        for name in parts:
            if name == "..":
                current = current.parent
                if not current.is_relative_to(directory):
                    raise COMPONENT.ComponentError(f"Asset dependency escapes source: {path}")
                continue
            _check_name(name)
            current = current / name
            _check_link(current)
        if not current.is_file():
            raise COMPONENT.ComponentError(f"Asset dependency must be a regular file: {path}")
    except (OSError, ValueError) as exc:
        raise COMPONENT.ComponentError(f"Asset dependency is missing or outside source: {path}") from exc


def _relative(directory, value):
    if not isinstance(value, str) or not value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise COMPONENT.ComponentError(f"Invalid asset file path: {value!r}")
    for part in value.split("/"):
        _check_name(part)
    _check_dependency(directory, directory / value)
    return value


def _svg(path):
    try:
        text = path.read_text(encoding="utf-8")
        if ("<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper()
                or re.search(r"<\?(?!xml\s)", text)):
            raise COMPONENT.ComponentError(f"SVG declarations are not allowed: {path.name}")
        root = ET.fromstring(text, parser=ET.XMLParser(target=ET.TreeBuilder(insert_pis=True)))
    except (OSError, UnicodeError, ET.ParseError) as exc:
        raise COMPONENT.ComponentError(f"Invalid SVG: {path.name}") from exc
    ids, references = set(), set()
    if root.tag not in {"svg", "{http://www.w3.org/2000/svg}svg"}:
        raise COMPONENT.ComponentError(f"SVG needs an svg root: {path.name}")
    for node in root.iter():
        tag = node.tag.removeprefix("{http://www.w3.org/2000/svg}") if isinstance(node.tag, str) else ""
        if tag not in SVG_TAGS:
            raise COMPONENT.ComponentError(f"SVG element is not allowed: {tag!r}")
        for key, value in node.attrib.items():
            key = "href" if key == "{http://www.w3.org/1999/xlink}href" else key
            if key == "{http://www.w3.org/XML/1998/namespace}space" and value in {"default", "preserve"}:
                continue
            if key not in SVG_ATTRS or "\\" in value:
                raise COMPONENT.ComponentError(f"SVG attribute is not allowed: {key}")
            if key == "id":
                if not value or re.search(r"[\s#]", value) or value in ids:
                    raise COMPONENT.ComponentError("SVG IDs must be nonempty and unique")
                ids.add(value)
            if key == "href":
                if not value.startswith("#") or len(value) == 1:
                    raise COMPONENT.ComponentError("SVG href must be a local fragment")
                references.add(value[1:])
            if re.search(r"url\s*\(", value, re.I):
                match = re.fullmatch(r"url\(\s*(['\"]?)#([^\s)'\"]+)\1\s*\)", value, re.I)
                if not match:
                    raise COMPONENT.ComponentError("SVG URLs must be local fragments")
                references.add(match.group(2))
    if references - ids:
        raise COMPONENT.ComponentError(f"SVG fragment is missing: {sorted(references - ids)}")


def _check_image(path):
    suffix = path.suffix.lower()
    if suffix == ".svg":
        _svg(path)
    elif suffix in RASTER:
        from PIL import Image

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(path) as image:
                    if image.format != RASTER[suffix] or min(image.size) <= 0:
                        raise ValueError("Image format does not match its extension")
                    image.verify()
                with Image.open(path) as image:
                    image.load()
        except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise COMPONENT.ComponentError(f"Invalid image: {path.name}: {exc}") from exc


def _check_audio(path):
    """Probe and decode local MP3 bytes without granting media network access."""
    probe = os.environ.get("HYPERFRAMES_FFPROBE_PATH", "ffprobe")
    decoder = os.environ.get("HYPERFRAMES_FFMPEG_PATH", "ffmpeg")
    try:
        result = subprocess.run([probe, "-v", "error", "-protocol_whitelist", "file,pipe",
            "-show_entries", "stream=codec_type,codec_name,sample_rate,channels:format=format_name,duration",
            "-of", "json", str(path)], capture_output=True, text=True, timeout=30)
        if result.returncode or result.stderr.strip():
            raise ValueError(result.stderr.strip() or "probe failed")
        report = json.loads(result.stdout)
        streams = [item for item in report["streams"] if item.get("codec_type") == "audio"]
        if report["format"]["format_name"] != "mp3" or len(streams) != 1 or streams[0]["codec_name"] != "mp3":
            raise ValueError("MP3 extension requires one real MP3 audio stream")
        stream = streams[0]
        duration = float(report["format"]["duration"])
        rate, channels = int(stream["sample_rate"]), int(stream["channels"])
        if not math.isfinite(duration) or duration <= 0 or rate <= 0 or channels <= 0:
            raise ValueError("invalid duration, sample rate or channels")
        result = subprocess.run([decoder, "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
            "-protocol_whitelist", "file,pipe", "-i", str(path), "-map", "0:a:0", "-f", "null", "-"],
            capture_output=True, text=True, timeout=120)
        if result.returncode or result.stderr.strip():
            raise ValueError(result.stderr.strip() or "decode failed")
        return {"format": "mp3", "codec": "mp3", "duration": duration, "sample_rate": rate, "channels": channels}
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        raise COMPONENT.ComponentError(f"Invalid MP3 audio {path.name}; local ffprobe/ffmpeg required: {exc}") from exc


def _inputs(directory):
    _relative(directory, "asset.json")
    metadata = COMPONENT._read_json(directory / "asset.json")
    asset_id, version, kind = (metadata.get(key) for key in ("id", "version", "kind"))
    if (type(metadata.get("schema_version")) is not int or metadata.get("schema_version") not in {1, 2}
            or not isinstance(asset_id, str) or not ID.fullmatch(asset_id)
            or type(version) is not int or version < 1 or not isinstance(kind, str)
            or kind not in (KINDS if metadata.get("schema_version") == 2 else {"module", "media"})):
        raise COMPONENT.ComponentError("asset.json requires a supported schema_version, slug id, positive version and kind")
    _check_name(asset_id)
    entry = _relative(directory, metadata.get("entry"))
    suffix = Path(entry).suffix
    if ((kind == "module" and suffix not in {".js", ".mjs"})
            or (kind == "media" and suffix.lower() not in {*RASTER, ".svg", ".mp3"})
            or (kind in DECLARATIVE and suffix != ".json")):
        raise COMPONENT.ComponentError("Asset entry must be JS/MJS for module or PNG/JPEG/WebP/SVG/MP3 for media")
    if metadata["schema_version"] == 2:
        _schema2(directory, metadata)
    runtime = metadata.get("runtime", {})
    if not isinstance(runtime, dict) or not isinstance(runtime.get("versions", {}), dict):
        raise COMPONENT.ComponentError("Asset runtime and runtime.versions must be objects")
    seeds = {"asset.json", entry}
    dependencies = metadata.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise COMPONENT.ComponentError("Asset dependencies must be a list of local files")
    seeds.update(_relative(directory, item) for item in dependencies)
    for key in ("usage", "example", "license"):
        if key in metadata:
            seeds.add(_relative(directory, metadata[key]))
    whitelist = metadata.get("files")
    if whitelist is not None:
        if not isinstance(whitelist, list) or not whitelist:
            raise COMPONENT.ComponentError("Asset files must be a nonempty file whitelist")
        whitelist = {"asset.json", *(_relative(directory, item) for item in whitelist)}
        if not seeds <= whitelist:
            raise COMPONENT.ComponentError("Asset file whitelist omits a declared entry or dependency")
        seeds = whitelist
    files = set()
    try:
        for seed in sorted(seeds):
            files.update(validate_dependencies(directory, entry=seed,
                         check_path=lambda path: _check_dependency(directory, path)))
    except (VisualPlanError, OSError, UnicodeError) as exc:
        raise COMPONENT.ComponentError(f"Invalid asset dependencies: {exc}") from exc
    if any(name.casefold() == "hashes.json" for name in files):
        raise COMPONENT.ComponentError("HASHES.json is generated only in the frozen package")
    if whitelist is not None and not files <= whitelist:
        raise COMPONENT.ComponentError(f"Asset dependency is outside file whitelist: {sorted(files - whitelist)}")
    names = {}
    for name in sorted(files | seeds):
        _relative(directory, name)
        for prefix in (Path(name), *Path(name).parents):
            folded = prefix.as_posix().casefold()
            if folded in names and names[folded] != prefix.as_posix():
                raise COMPONENT.ComponentError(f"Asset paths have a case-insensitive collision: {name}")
            names[folded] = prefix.as_posix()
    for name in sorted(files):
        if kind in DECLARATIVE and Path(name).suffix.lower() in {".js", ".mjs", ".cjs", ".html", ".htm", ".css", ".wasm"}:
            raise COMPONENT.ComponentError("Declarative assets cannot contain executable dependencies")
        _check_image(directory / name)
        if Path(name).suffix.lower() == ".mp3":
            audio = _check_audio(directory / name)
            if kind == "media" and name == entry:
                metadata = {**metadata, "media_type": "audio", "audio": audio}
    return metadata, sorted(files)


def validate_asset(directory, expected_ref=None):
    """Validate one closed, hash-covered module/media package."""
    directory = _root(directory)
    metadata, files = _inputs(directory)
    _relative(directory, "HASHES.json")
    for path in directory.rglob("*"):
        _check_link(path)
        for name in path.relative_to(directory).parts:
            _check_name(name)
        if not path.is_file() and not path.is_dir():
            raise COMPONENT.ComponentError(f"Frozen asset contains a non-regular path: {path}")
    actual = COMPONENT.package_entries(directory)
    if [item["path"] for item in actual] != files:
        raise COMPONENT.ComponentError("Frozen asset contains files outside its declared dependency closure")
    hashes = COMPONENT._validate_hashes(directory)
    asset_ref = f"{metadata['id']}@v{metadata['version']}"
    if hashes.get("component_ref") != asset_ref or (expected_ref is not None and asset_ref != expected_ref):
        raise COMPONENT.ComponentError(f"Asset identity does not match expected package: {asset_ref}")
    return {"component_ref": asset_ref, "component_id": metadata["id"], "version": metadata["version"],
            "ratio": None, "metadata": {**metadata, "asset_type": metadata["kind"]},
            "package_sha256": hashes["package_sha256"], "files": hashes["files"]}


def freeze_source(source, destination):
    """Copy only selected inputs; never write hashes or state into editable source."""
    source = _root(source)
    destination = Path(destination).absolute()
    if (destination.exists() or destination.is_symlink() or destination.is_relative_to(source)
            or source.is_relative_to(destination)):
        raise COMPONENT.ComponentError("Frozen destination must be new and separate from the source")
    for parent in destination.parents:
        if parent.exists() or parent.is_symlink():
            _check_link(parent)
    metadata, files = _inputs(source)
    before = [{"path": name, "sha256": COMPONENT.file_sha256(source / name)} for name in files]
    destination.mkdir(parents=True)
    try:
        for name in files:
            _relative(source, name)
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)
        _, after_files = _inputs(source)
        after = [{"path": name, "sha256": COMPONENT.file_sha256(source / name)} for name in after_files]
        if before != after or COMPONENT.package_entries(destination) != before:
            raise COMPONENT.ComponentError("Asset source changed during freezing; retry from stable inputs")
        COMPONENT._atomic_json(destination / "HASHES.json", {
            "schema_version": 1, "algorithm": COMPONENT.PACKAGE_ALGORITHM,
            "component_ref": f"{metadata['id']}@v{metadata['version']}", "files": before,
            "package_sha256": COMPONENT.package_sha256(destination),
        })
        return validate_asset(destination)
    except Exception:
        shutil.rmtree(destination)
        raise
