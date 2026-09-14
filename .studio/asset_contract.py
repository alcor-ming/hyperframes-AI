"""The small module/media source-to-frozen-package contract."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import stat
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


def _inputs(directory):
    _relative(directory, "asset.json")
    metadata = COMPONENT._read_json(directory / "asset.json")
    asset_id, version, kind = (metadata.get(key) for key in ("id", "version", "kind"))
    if (type(metadata.get("schema_version")) is not int or metadata.get("schema_version") != 1
            or not isinstance(asset_id, str) or not ID.fullmatch(asset_id)
            or type(version) is not int or version < 1 or not isinstance(kind, str)
            or kind not in {"module", "media"}):
        raise COMPONENT.ComponentError("asset.json requires schema_version 1, slug id, positive version and module/media kind")
    _check_name(asset_id)
    entry = _relative(directory, metadata.get("entry"))
    suffix = Path(entry).suffix
    if ((kind == "module" and suffix not in {".js", ".mjs"})
            or (kind == "media" and suffix.lower() not in {*RASTER, ".svg"})):
        raise COMPONENT.ComponentError("Asset entry must be JS/MJS for module or PNG/JPEG/WebP/SVG for media")
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
        _check_image(directory / name)
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
