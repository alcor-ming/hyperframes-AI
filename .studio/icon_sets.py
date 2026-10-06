"""Offline Lucide source import and exact, installed icon references."""
from pathlib import Path
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET

import asset_contract as ASSET
import component_harness as COMPONENT


REF = re.compile(r"lucide:([a-z0-9]+(?:-[a-z0-9]+)*)@([0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?)$")
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?$")


def validate_manifest(data, metadata, directory):
    ASSET._fields(data, {"package", "version", "license", "icons"},
                  {"package", "version", "license", "icons"}, "icon set")
    if data["package"] != "lucide-static" or not isinstance(data["version"], str) or not SEMVER.fullmatch(data["version"]):
        raise COMPONENT.ComponentError("Icon set requires lucide-static and exact package semver")
    if data["license"] != "ISC" or not metadata.get("license"):
        raise COMPONENT.ComponentError("Icon set requires ISC license text")
    if not isinstance(data["icons"], list) or not data["icons"]:
        raise COMPONENT.ComponentError("Icon set must contain icons")
    names = set()
    for icon in data["icons"]:
        ASSET._fields(icon, {"name", "aliases", "tags", "path", "sha256"},
                      {"name", "aliases", "tags", "path", "sha256"}, "icon")
        if not isinstance(icon["name"], str) or not ASSET.ID.fullmatch(icon["name"]) or icon["name"] in names:
            raise COMPONENT.ComponentError("Icon names must be unique slugs")
        names.add(icon["name"])
        for field in ("aliases", "tags"):
            if not isinstance(icon[field], list) or any(not isinstance(v, str) or not v.strip() for v in icon[field]):
                raise COMPONENT.ComponentError("Icon aliases/tags must be nonempty strings")
        path = ASSET._relative(directory, icon["path"])
        if not path.endswith(".svg") or path not in metadata.get("dependencies", []):
            raise COMPONENT.ComponentError("Icon SVG must be a declared dependency")
        ASSET._svg(directory / path)
        if COMPONENT.file_sha256(directory / path) != icon["sha256"]:
            raise COMPONENT.ComponentError("Icon SVG hash mismatch")
    return data


def import_lucide(package, destination, *, asset_version=1):
    """Read a local npm package; never fetch, pack, accept, or modify its files."""
    package = ASSET._root(package)
    destination = Path(destination).absolute()
    from asset_store import _guard_source
    _guard_source(destination)
    ASSET._relative(package, "package.json")
    npm = COMPONENT._read_json(package / "package.json")
    if npm.get("name") != "lucide-static" or not isinstance(npm.get("version"), str) or not SEMVER.fullmatch(npm["version"]):
        raise COMPONENT.ComponentError("Expected local lucide-static package with exact semver")
    if npm.get("license") != "ISC" or type(asset_version) is not int or asset_version < 1:
        raise COMPONENT.ComponentError("Expected ISC package and positive asset version")
    license_path = next((name for name in ("LICENSE", "LICENSE.txt", "LICENSE.md") if (package / name).is_file()), None)
    ASSET._relative(package, license_path)
    if not (package / license_path).read_text(encoding="utf-8").strip():
        raise COMPONENT.ComponentError("License text is empty")
    if destination.is_relative_to(package) or package.is_relative_to(destination):
        raise COMPONENT.ComponentError("Icon source must be separate from npm package")
    for parent in destination.parents:
        if parent.exists() or parent.is_symlink():
            ASSET._check_link(parent)
    icons = []
    for path in sorted((package / "icons").glob("*.svg")):
        ASSET._relative(package, path.relative_to(package).as_posix())
        ASSET._svg(path)
        icons.append({"name": path.stem, "aliases": [], "tags": [],
                      "path": f"icons/{path.name}", "sha256": COMPONENT.file_sha256(path)})
    # Local packages may carry per-icon search metadata; SVG-only packages remain searchable by name.
    if (package / "icon-metadata.json").exists():
        ASSET._relative(package, "icon-metadata.json")
        extra = COMPONENT._read_json(package / "icon-metadata.json")
        if not isinstance(extra, dict):
            raise COMPONENT.ComponentError("Icon metadata must be an object")
        for icon in icons:
            item = extra.get(icon["name"], {})
            if not isinstance(item, dict):
                raise COMPONENT.ComponentError("Per-icon metadata must be an object")
            icon.update({key: item.get(key, []) for key in ("aliases", "tags")})
    if (package / "tags.json").exists():
        ASSET._relative(package, "tags.json")
        tags = COMPONENT._read_json(package / "tags.json")
        if not isinstance(tags, dict):
            raise COMPONENT.ComponentError("Icon tags must be an object")
        for icon in icons:
            icon["tags"] = tags.get(icon["name"], icon["tags"])
    manifest = {"schema_version": 2, "id": "lucide-static", "version": asset_version,
                "kind": "icon-set", "entry": "icons.json", "contract_version": 1,
                "parameters": {}, "compatibility": {}, "license": "LICENSE",
                "dependencies": [icon["path"] for icon in icons]}
    declaration = {"package": npm["name"], "version": npm["version"], "license": "ISC", "icons": icons}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".icon-import-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "source"
        (staged / "icons").mkdir(parents=True)
        for icon in icons:
            shutil.copyfile(package / icon["path"], staged / icon["path"])
        shutil.copyfile(package / license_path, staged / "LICENSE")
        COMPONENT._atomic_json(staged / "asset.json", manifest)
        COMPONENT._atomic_json(staged / "icons.json", declaration)
        ASSET._inputs(staged)
        if destination.exists() or destination.is_symlink():
            ASSET._root(destination)
            ASSET._inputs(destination)
            for path in destination.rglob("*"):
                ASSET._check_link(path)
            if not COMPONENT._same_tree(staged, destination):
                raise COMPONENT.ComponentError("Icon identity/version already has different content")
        else:
            staged.rename(destination)
    return {"source": str(destination), "asset_ref": f"lucide-static@v{asset_version}",
            "package": npm["name"], "version": npm["version"], "icons": len(icons), "accepted": False}


def search_icons(packages, query=""):
    results = {}
    for package in sorted(map(Path, packages)):
        report = ASSET.validate_asset(package)
        if report["metadata"]["kind"] != "icon-set":
            continue
        data = COMPONENT._read_json(package / report["metadata"]["entry"])
        for icon in data["icons"]:
            ref = f"lucide:{icon['name']}@{data['version']}"
            row = {**icon, "ref": ref, "asset_ref": report["component_ref"],
                   "package_sha256": report["package_sha256"], "package_path": str(package)}
            if ref in results and (results[ref]["sha256"], results[ref]["package_sha256"]) != (row["sha256"], row["package_sha256"]):
                raise COMPONENT.ComponentError(f"Conflicting exact icon reference: {ref}")
            results[ref] = row
    return [row for ref, row in sorted(results.items()) if query.casefold() in
            " ".join([row["name"], *row["aliases"], *row["tags"]]).casefold()]


def project_packages(project):
    project = Path(project)
    if not (project / "COMPONENT_LOCK.json").is_file():
        return []
    COMPONENT.verify_installation(project, check_mounts=False)
    lock = COMPONENT._read_json(project / "COMPONENT_LOCK.json")
    return [project / item["vendor_path"] for item in lock["components"] if item.get("asset_kind") == "icon-set"]


def _resolve(packages, reference):
    if not isinstance(reference, str) or not REF.fullmatch(reference):
        raise COMPONENT.ComponentError("Icon requires exact lucide:name@package-semver reference")
    rows = search_icons(packages)
    if not rows:
        raise COMPONENT.ComponentError("Icon set not installed; import, pack, accept and install the icon set first")
    match = next((row for row in rows if row["ref"] == reference), None)
    if match is None:
        raise COMPONENT.ComponentError(f"Icon reference outside installed closure: {reference}")
    return match


def validate_svg_reference(reference, project, packages=None):
    project = Path(project)
    if reference.startswith("custom:"):
        name = ASSET._relative(project, reference.removeprefix("custom:"))
        if not name.endswith(".svg"):
            raise COMPONENT.ComponentError("Custom SVG reference requires .svg")
        ASSET._svg(project / name)
        return {"path": name, "custom": True}
    return _resolve(project_packages(project) if packages is None else packages, reference)


def use_icon(packages, reference, project, destination, *, color_token="--appearance-colors-text", stroke_token="--appearance-lines-icon-width"):
    project = ASSET._root(project)
    installed = project_packages(project)
    if {Path(p).resolve() for p in packages} - {p.resolve() for p in installed}:
        raise COMPONENT.ComponentError("Icon reference outside installed project closure")
    row = _resolve(installed, reference)
    for token in (color_token, stroke_token):
        if not re.fullmatch(r"--[a-zA-Z][a-zA-Z0-9-]*", token):
            raise COMPONENT.ComponentError("Icon theme token must be a CSS custom property")
    from work_requests import safe
    destination = COMPONENT._safe_relative(str(destination), "icon destination")
    if not destination.endswith(".svg") or destination.startswith("vendor/"):
        raise COMPONENT.ComponentError("Icon destination must be a non-vendor SVG")
    target = safe(project, destination)
    if target.exists():
        raise COMPONENT.ComponentError("Icon destination already exists")
    root = ET.fromstring((Path(row["package_path"]) / row["path"]).read_text(encoding="utf-8"))
    root.set("data-icon", reference)
    root.set("data-icon-sha256", row["sha256"])
    root.set("stroke", "currentColor")
    root.set("style", f"color:var({color_token});stroke-width:var({stroke_token},2)")
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        handle.write(ET.tostring(root, encoding="unicode"))
    return {**row, "path": destination, "source_marker": reference}


def _geometry(root):
    ignored = {"data-icon", "data-icon-sha256", "style", "class", "id", "width", "height", "stroke", "stroke-width", "color", "aria-hidden", "role"}
    def shape(node, is_root=False):
        return (node.tag.removeprefix("{http://www.w3.org/2000/svg}"),
                sorted((key, value) for key, value in node.attrib.items()
                       if key != "data-hf-id" and (not is_root or key not in ignored)),
                (node.text or "").strip(), [shape(child) for child in node])
    return shape(root, True)


def audit_icons(records, packages):
    issues = []
    try:
        sources = {row["ref"]: row for row in search_icons(packages)}
    except COMPONENT.ComponentError:
        sources = {}
    for record in records:
        try:
            root = ET.fromstring(record.get("svg", ""))
        except ET.ParseError:
            continue
        reference = root.get("data-icon")
        code = None
        if reference:
            try:
                row = sources.get(reference)
                if row is None:
                    raise COMPONENT.ComponentError("Icon source is outside the verified closure")
                original = ET.parse(Path(row["package_path"]) / row["path"]).getroot()
                if root.get("data-icon-sha256") != row["sha256"] or _geometry(root) != _geometry(original):
                    code = "icon_source_mismatch"
            except COMPONENT.ComponentError:
                code = "icon_source_mismatch"
        elif not (record.get("schematic") or root.get("data-hf-schematic") is not None):
            # ponytail: size-only suspicion, not a pass/fail classifier; visual review decides meaning.
            if 0 < record.get("width", 0) <= 128 and 0 < record.get("height", 0) <= 128:
                code = "unmarked_small_svg"
        if code:
            issues.append({"code": code, "target": record.get("target"), "reference": reference,
                           "status": "review", "message": "Icon source or recognizability needs visual review"})
    return issues
