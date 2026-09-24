"""Local, independently accepted Component packages; Work keeps its own copies."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import tempfile

from component_harness import (
    ComponentError, _atomic_json, _read_json, _read_frontmatter,
    _safe_relative, _same_tree, file_sha256, parse_component_ref,
    validate_component_release, validate_component_acceptance,
)


def _config_path(root: Path) -> Path:
    value = os.environ.get("HYPERFRAMES_AI_ASSET_CONFIG") or os.environ.get("HYPERFRAMES_AI_CONFIG")
    return Path(value) if value else root / ".studio/.runtime/assets.json"


def _tool_paths(root: Path) -> list[Path]:
    if os.environ.get("HYPERFRAMES_AI_RESOLVED_CONFIG"):
        return [root / name for name in (".studio", "runtime", ".agents")]
    return [root]


def asset_store_root(root: Path) -> Path:
    config = _config_path(root)
    value = os.environ.get("HYPERFRAMES_AI_ASSET_ROOT")
    if not value and config.is_file():
        value = json.loads(config.read_text(encoding="utf-8-sig")).get("asset_root")
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ComponentError("AssetStore is not configured; run component root <absolute-path>")
    store = Path(value).resolve()
    _guard_store(store)
    return store


def _guard_store(store: Path) -> None:
    if os.environ.get("HYPERFRAMES_AI_REVIEW") != "1":
        return
    review = os.environ.get("HYPERFRAMES_AI_ASSET_REVIEW_ROOT")
    if not review or store.resolve() != (Path(review) / "store").resolve():
        raise ComponentError("Review asset writes require the pinned isolated AssetStore")
    for value in json.loads(os.environ.get("HYPERFRAMES_AI_REVIEW_PROTECTED_ROOTS", "[]")):
        if store.resolve().is_relative_to(Path(value).resolve()):
            raise ComponentError("Review AssetStore cannot target production")


def _target(store: Path, relative: str) -> Path:
    from work_requests import RequestError, safe
    _guard_store(store)
    try:
        target = safe(store, relative)
    except RequestError as error:
        raise ComponentError(str(error)) from error
    if target.is_file() and target.stat().st_nlink > 1:
        raise ComponentError(f"AssetStore target cannot be a hardlink: {target}")
    return target


def _guard_source(source: Path) -> None:
    if os.environ.get("HYPERFRAMES_AI_REVIEW") != "1":
        return
    review = os.environ.get("HYPERFRAMES_AI_ASSET_REVIEW_ROOT")
    work = os.environ.get("HYPERFRAMES_AI_WORK_ROOT")
    roots = ([Path(review) / "sources"] if review else []) + ([Path(work) / "works/active"] if work else [])
    if not any(source.resolve().is_relative_to(path.resolve()) for path in roots):
        raise ComponentError("Review source must be an isolated source copy or Review Work-local directory")


def configure_asset_store(root: Path, directory: Path) -> dict:
    from windows_runtime import paths_overlap
    directory = Path(directory).expanduser()
    if not directory.is_absolute():
        raise ComponentError("AssetStore requires an absolute path")
    directory = directory.resolve()
    if os.environ.get("HYPERFRAMES_AI_REVIEW") == "1":
        raise ComponentError("Review cannot change its isolated asset root configuration")
    config_path = Path(os.environ.get("HYPERFRAMES_AI_DEFAULT_CONFIG") or _config_path(root))
    config = json.loads(config_path.read_text(encoding="utf-8-sig")) if config_path.is_file() else {}
    work_root = os.environ.get("HYPERFRAMES_AI_WORK_ROOT") or config.get("work_root")
    protected = _tool_paths(root)
    if os.environ.get("HYPERFRAMES_AI_HOME"):
        protected.append(Path(os.environ["HYPERFRAMES_AI_HOME"]))
    if ((directory / "works").exists() or _work_conflict(directory, work_root)
            or any(paths_overlap(directory, path) for path in protected)):
        raise ComponentError("AssetStore must be outside the Harness and WorkStore")
    directory.mkdir(parents=True, exist_ok=True)
    config["asset_root"] = str(directory)
    _atomic_json(config_path, config)
    return {"asset_root": str(directory), "config": str(config_path),
            "scope": "next-command"}


def _work_conflict(directory: Path, work_root: str | None) -> bool:
    from windows_runtime import paths_overlap
    if not work_root:
        return False
    work = Path(work_root).resolve()
    # The root deployment reserves one sibling library, never works/ or runtime data.
    return paths_overlap(directory, work) and not directory.resolve().is_relative_to(work / "asset-library")


def _sources(store: Path) -> list[str]:
    path = store / "sources.json"
    sources = _read_json(path).get("sources") if path.exists() else []
    if not isinstance(sources, list) or not all(isinstance(item, str) and Path(item).is_absolute() for item in sources):
        raise ComponentError("AssetStore sources must be an array of absolute directories")
    return sources


def _configured_sources(root: Path, store: Path) -> list[str]:
    config = _config_path(root)
    snapshot = os.environ.get("HYPERFRAMES_AI_RESOLVED_CONFIG")
    data = json.loads(snapshot) if snapshot else (_read_json(config) if config.is_file() else {})
    if "asset_source_roots" in data:
        sources = data["asset_source_roots"]
        if not isinstance(sources, list) or not all(isinstance(p, str) and Path(p).is_absolute() for p in sources):
            raise ComponentError("Configured asset_source_roots must be absolute directories")
        return sources
    return _sources(store)


def register_source(store: Path, directory: Path) -> dict:
    from windows_runtime import paths_overlap
    directory = Path(directory).expanduser().resolve()
    _guard_source(directory)
    protected = [store]
    if os.environ.get("HYPERFRAMES_AI_ROOT"):
        protected += _tool_paths(Path(os.environ["HYPERFRAMES_AI_ROOT"]))
    if os.environ.get("HYPERFRAMES_AI_HOME"):
        protected.append(Path(os.environ["HYPERFRAMES_AI_HOME"]))
    if (not directory.is_dir() or _work_conflict(directory, os.environ.get("HYPERFRAMES_AI_WORK_ROOT"))
            or any(paths_overlap(directory, path) for path in protected)):
        raise ComponentError("Asset source must be an existing directory outside AssetStore")
    path = _target(store, "sources.json")
    data = {"sources": _sources(store)}
    if str(directory) not in data["sources"]:
        data["sources"].append(str(directory))
        data["sources"].sort()
        _atomic_json(path, data)
    return data


def authoring_project(root: Path, project: Path) -> Path:
    project = project.expanduser().resolve()
    store = asset_store_root(root)
    sources = _configured_sources(root, store)
    if not project.is_dir() or not any(project.is_relative_to(Path(p).resolve()) for p in sources):
        raise ComponentError("Standalone sample must be inside a registered AssetSource")
    _guard_source(project)
    config = _read_json(_config_path(root))
    work_root = os.environ.get("HYPERFRAMES_AI_WORK_ROOT") or config.get("work_root")
    if any(project.is_relative_to(p.resolve()) for p in _tool_paths(root)) or project.is_relative_to(store.resolve()) or _work_conflict(project, work_root):
        raise ComponentError("Standalone samples cannot target Harness, AssetStore or a Work")
    return project


def _relative(ref: str) -> Path:
    identity, version = parse_component_ref(ref)
    return Path(identity) / f"v{version}"


def _validate_package(directory: Path, expected_ref: str | None = None) -> dict:
    if not (directory / "COMPONENT.md").is_file() and not (directory / "asset.json").is_file():
        raise ComponentError("Unsupported asset contract; a Component Release is required")
    report = validate_component_release(directory, expected_ref=expected_ref, allow_unapproved=True)
    kinds = {"component", "effect", "module", "media"}
    if (directory / "asset.json").is_file():
        kinds |= {"theme", "background", "motion"}
    if report["metadata"].get("asset_type", "component") not in kinds:
        raise ComponentError("Unsupported asset type for the Component contract")
    return report


def _validate_dependencies(directory: Path, report: dict) -> None:
    if (directory / "asset.json").is_file():
        return  # validate_asset already checks the frozen recursive closure.
    from visual_plan import VisualPlanError, validate_dependencies
    try:
        validate_dependencies(directory, entry="component.html")
    except VisualPlanError as error:
        raise ComponentError(f"Asset dependency check failed: {error}") from error
    dependencies = report["metadata"].get("dependencies", [])
    if not isinstance(dependencies, list):
        raise ComponentError("Asset dependencies must be an array of local path/sha256 records")
    for item in dependencies:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ComponentError("Asset dependency requires path and sha256")
        target = directory / _safe_relative(item["path"], "dependency path")
        if not target.is_file() or file_sha256(target) != item.get("sha256"):
            raise ComponentError(f"Asset dependency digest mismatch: {item['path']}")


def import_component(store: Path, source: Path) -> dict:
    source = Path(source).expanduser().resolve()
    _guard_source(source)
    return _import_package(store, source)


def pack_source(store: Path, source: Path) -> dict:
    from asset_contract import freeze_source
    source = Path(source).expanduser().resolve()
    _guard_source(source)
    _guard_store(store)
    store.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".asset-pack-", dir=store) as temporary:
        frozen = Path(temporary) / "package"
        freeze_source(source, frozen)
        return _import_package(store, frozen, original_source=source)


def _import_package(store: Path, source: Path, *, original_source: Path | None = None) -> dict:
    report = _validate_package(source)
    _accepted_closure(store, report["metadata"].get("asset_dependencies", []), visiting={report["component_ref"]})
    relative = _relative(report["component_ref"])
    destination = _target(store, (Path("candidates") / relative).as_posix())
    accepted = _target(store, (Path("packages") / relative).as_posix())
    for existing in (destination / "package", accepted):
        if existing.exists() and not _same_tree(source, existing):
            raise ComponentError(f"Asset identity/version already has different content: {report['component_ref']}")
    if destination.exists():
        return _read_json(destination / "candidate.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".asset-import-", dir=destination.parent) as temporary:
        staging = Path(temporary) / "candidate"
        shutil.copytree(source, staging / "package")
        if not _same_tree(source, staging / "package"):
            raise ComponentError("Asset changed during import")
        _validate_package(staging / "package", report["component_ref"])
        # Studio may edit review/, never package/ or the eventual accepted copy.
        shutil.copytree(staging / "package", staging / "review")
        data = {"component_ref": report["component_ref"], "package_sha256": report["package_sha256"],
                "source": str(original_source or source), "status": "candidate", "path": str(destination),
                "review": str(destination / "review")}
        _atomic_json(staging / "candidate.json", data)
        staging.rename(destination)
    return data


def accept_component(store: Path, ref: str, sha256: str, note: str, *, runtime_root: Path) -> dict:
    relative = _relative(ref)
    candidate = _target(store, (Path("candidates") / relative).as_posix())
    report = _validate_package(candidate / "package", ref)
    if sha256 != report["package_sha256"]:
        raise ComponentError("Acceptance must name the exact candidate package_sha256")
    if not note.strip():
        raise ComponentError("Acceptance requires a note recording the reviewed fixture and result")
    if not _same_tree(candidate / "package", candidate / "review"):
        raise ComponentError("Review copy changed; package changes as a new version before acceptance")
    _validate_dependencies(candidate / "package", report)
    _accepted_closure(store, report["metadata"].get("asset_dependencies", []), runtime_root=runtime_root,
                      visiting={ref})
    from asset_contract import asset_requires_runtime
    executable = asset_requires_runtime(report["metadata"])
    lock = _read_json(runtime_root / "windows-runtime.lock.json") if executable else {"target": "declarative", "versions": {}}
    declared_runtime = report["metadata"].get("runtime", {})
    declared_versions = declared_runtime.get("versions", {}) if isinstance(declared_runtime, dict) else None
    if not isinstance(declared_versions, dict):
        raise ComponentError("Asset runtime versions must be an object")
    required_versions = {"hyperframes", *declared_versions} if executable else set()
    entry = report["metadata"].get("entry", "component.html")
    source = (candidate / "package" / entry).read_text(encoding="utf-8") if executable else ""
    # ponytail: literal legacy use detection; indirect aliases need runtime.versions metadata.
    for name, marker in (("gsap", "gsap."), ("three", "THREE.")):
        if executable and (marker in source or any(name in item["path"].lower() for item in report["files"])):
            required_versions.add(name)
    if required_versions - set(lock["versions"]):
        raise ComponentError("Asset declares unsupported runtime dependencies")
    acceptance = {"schema_version": 1, "status": "accepted", "component_ref": ref,
                  "package_sha256": sha256, "accepted_at": datetime.now(timezone.utc).isoformat(),
                  "note": note.strip(), "source": _read_json(candidate / "candidate.json")["source"],
                  "runtime": {"target": lock["target"], "versions": {
                      name: lock["versions"][name] for name in sorted(required_versions)}}}
    if os.environ.get("HYPERFRAMES_AI_REVIEW") == "1":
        acceptance["review"] = {"work_root": os.environ["HYPERFRAMES_AI_WORK_ROOT"], "asset_root": str(store)}
    validate_component_acceptance(acceptance, report, runtime_root=runtime_root)
    destination = _target(store, (Path("packages") / relative).as_posix())
    record = _target(store, (Path("acceptances") / relative / "acceptance.json").as_posix())
    if destination.exists():
        if not _same_tree(candidate / "package", destination):
            raise ComponentError(f"Refusing to overwrite accepted asset: {ref}")
        if record.is_file():
            existing = _read_json(record)
            validate_component_acceptance(existing, report, runtime_root=runtime_root)
            return existing
        _atomic_json(record, acceptance)
        return acceptance
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".asset-accept-", dir=destination.parent) as temporary:
        staging = Path(temporary) / "package"
        shutil.copytree(candidate / "package", staging)
        if not _same_tree(candidate / "package", staging):
            raise ComponentError("Candidate changed during acceptance")
        _validate_package(staging, ref)
        staging.rename(destination)
    _atomic_json(record, acceptance)
    return acceptance


def discover_components(root: Path, query: str = "", *, kind=None, ratio=None, tag=None,
                        recommendation=None, rebuild=False, research_root=None) -> dict:
    def declared_ratios(metadata):
        compatibility = metadata.get("compatibility", {})
        return compatibility.get("ratios", []) if isinstance(compatibility, dict) else []

    roots = [(root / ".studio/components", "legacy")]
    try:
        store = asset_store_root(root)
    except ComponentError:
        store = None
    if store:
        roots += [(store / "packages", "accepted"), (store / "candidates", "candidate")]
        sources = _configured_sources(root, store)
        roots += [(Path(path), "source") for path in sources]
    assets, errors = [], []
    cache_path = _target(store, ".discovery-cache.json") if store else None
    try:
        cache = _read_json(cache_path) if cache_path and cache_path.is_file() and not rebuild else {}
    except (ComponentError, ValueError, OSError):
        cache = {}
    fresh, refreshed = {}, []

    def read(path):
        stat = path.stat()
        key = str(path.resolve())
        signature = [stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size]
        item = cache.get(key)
        if not isinstance(item, dict) or item.get("signature") != signature:
            item = {"signature": signature, "value": _read_frontmatter(path) if path.name == "COMPONENT.md" else _read_json(path)}
            refreshed.append(key)
        fresh[key] = item
        return item["value"]

    selection = {}
    if store and (store / "selection.json").exists():
        try:
            selection = read(store / "selection.json")
            if not isinstance(selection, dict) or any(not isinstance(value, dict) for value in selection.values()):
                raise ComponentError("Selection metadata must map exact asset refs to objects")
            for ref, value in selection.items():
                parse_component_ref(ref)
                for field in ("aliases", "tags", "examples", "limitations"):
                    if field in value and (not isinstance(value[field], list) or not all(isinstance(item, str) for item in value[field])):
                        raise ComponentError(f"Selection {field} must be an array of strings")
                if "recommendation" in value and value["recommendation"] not in ("recommended", "historical", "pending"):
                    raise ComponentError("Selection recommendation must be recommended, historical or pending")
        except (ComponentError, OSError, ValueError) as error:
            selection = {}
            errors.append({"path": str(store / "selection.json"), "error": str(error), "unsynchronized": True})
    seen = set()
    observed_hashes = {}
    for directory, origin in roots:
        if not directory.is_dir():
            if origin == "source":
                errors.append({"path": str(directory), "error": "Source is unavailable"})
            continue
        for metadata_path in sorted([*directory.rglob("COMPONENT.md"), *directory.rglob("asset.json")]):
            if origin == "candidate" and "review" in metadata_path.relative_to(directory).parts:
                continue
            package = metadata_path.parent
            if package.resolve() in seen:
                continue
            seen.add(package.resolve())
            try:
                if origin == "source" and metadata_path.name == "asset.json" and not (package / "HASHES.json").exists():
                    metadata = read(metadata_path)
                    ref = f"{metadata['id']}@v{metadata['version']}"
                    parse_component_ref(ref)
                    assets.append({"component_ref": ref, "package_sha256": None, "path": str(package.resolve()),
                                   "origin": origin, "available": False, "status": "editable-source",
                                   "asset_type": metadata["kind"], "ratio": metadata.get("ratio"),
                                   "ratios": declared_ratios(metadata),
                                   "communication_goal": metadata.get("description", ""),
                                   "verification": "metadata-only; source is not accepted"})
                    continue
                metadata = read(metadata_path)
                if metadata_path.name == "asset.json":
                    metadata = {**metadata, "asset_type": metadata["kind"]}
                hashes = read(package / "HASHES.json")
                ref = hashes.get("component_ref", hashes.get("asset_ref"))
                if not isinstance(ref, str):
                    raise ComponentError("Asset manifest requires a string reference")
                parse_component_ref(ref)
                observed_hashes.setdefault(ref, set()).add(hashes["package_sha256"])
                if metadata_path.name == "asset.json" and ref != f"{metadata['id']}@v{metadata['version']}":
                    raise ComponentError("Asset metadata identity disagrees with manifest")
                if not isinstance(hashes.get("files"), list) or not hashes["files"]:
                    raise ComponentError("Asset manifest requires files")
                for entry in hashes["files"]:
                    dependency = package / _safe_relative(entry["path"], "manifest file")
                    if not dependency.resolve().is_relative_to(package.resolve()) or not dependency.is_file():
                        raise ComponentError(f"Manifest file missing or outside package: {entry['path']}")
                report = {"component_ref": ref, "metadata": metadata, "ratio": metadata.get("ratio"),
                          "package_sha256": hashes["package_sha256"]}
                metadata, ref = report["metadata"], report["component_ref"]
                available = origin == "legacy" and metadata.get("status") == "library-approved"
                acceptance = None
                if origin == "accepted":
                    acceptance = read(store / "acceptances" / _relative(ref) / "acceptance.json")
                    validate_component_acceptance(acceptance, report, runtime_root=root)
                    available = True
                assets.append({"component_ref": ref, "package_sha256": report["package_sha256"],
                               "path": str(package.resolve()), "origin": origin, "available": available,
                               "status": "accepted" if acceptance else metadata.get("status", "candidate"),
                               "asset_type": metadata.get("asset_type", "component"), "ratio": report["ratio"],
                               "ratios": declared_ratios(metadata),
                               "communication_goal": metadata.get("communication_goal", metadata.get("description", "")),
                               "information_shapes": metadata.get("information_shapes", []),
                               "anti_use_cases": metadata.get("anti_use_cases", []), "acceptance": acceptance,
                               "verification": "metadata-only; verified on use"})
                if str(metadata.get("entry", "")).lower().endswith(".mp3"):
                    assets[-1]["media_type"] = "audio"
            except (ComponentError, OSError, ValueError, KeyError, TypeError) as error:
                errors.append({"path": str(package), "error": str(error)})
    hashes: dict[str, set[str]] = observed_hashes
    for asset in assets:
        if asset["package_sha256"]:
            hashes.setdefault(asset["component_ref"], set()).add(asset["package_sha256"])
    for asset in assets:
        if len(hashes.get(asset["component_ref"], set())) > 1:
            asset.update(available=False, conflict="Same identity/version has different package hashes")
        extra = selection.get(asset["component_ref"], {})
        asset.update({key: extra[key] for key in ("aliases", "tags", "purpose", "examples", "limitations", "replacement") if key in extra})
        state = extra.get("recommendation", "pending")
        asset["recommendation"] = state if state in {"recommended", "historical", "pending"} else "pending"
        asset["ratio"] = asset.get("ratio") or "unknown"
        asset["ratios"] = asset.get("ratios") or ([asset["ratio"]] if asset["ratio"] != "unknown" else [])
        if not isinstance(asset["ratios"], list) or not all(isinstance(value, str) for value in asset["ratios"]):
            asset["ratios"] = []
        if asset["ratio"] == "unknown" and len(asset["ratios"]) == 1:
            asset["ratio"] = asset["ratios"][0]
        asset["check_scope"] = asset.get("verification", "metadata-only")
        asset["group"] = asset["origin"]
        asset["match_reasons"] = [key for key in ("component_ref", "communication_goal", "purpose", "aliases", "tags", "information_shapes")
                                  if query and query.casefold() in json.dumps(asset.get(key, ""), ensure_ascii=False).casefold()]
        asset["use"] = ("appearance binding with exact ref/hash" if asset["asset_type"] in {"theme", "background", "motion"}
                        else "component install with exact ref/hash") if asset["available"] else "reference only; not accepted for use"
    if query:
        assets = [asset for asset in assets if asset["match_reasons"]]
    assets = [asset for asset in assets if (not kind or asset["asset_type"] == kind or asset.get("media_type") == kind)
              and (not ratio or ratio in asset["ratios"] or ratio == "unknown" and not asset["ratios"])
              and (not tag or tag in asset.get("tags", []))
              and (not recommendation or asset["recommendation"] == recommendation)]
    assets.sort(key=lambda asset: (not asset["available"], {"recommended": 0, "pending": 1, "historical": 2}[asset["recommendation"]], asset["component_ref"]))
    if cache_path and fresh != cache:
        try:
            _atomic_json(cache_path, fresh)
        except (ComponentError, OSError) as error:
            errors.append({"path": str(cache_path), "error": str(error), "unsynchronized": True})
    result = {"assets": assets, "errors": errors, "refreshed": refreshed}
    if research_root is not None:
        from research_catalog import query as research_query
        result["research"] = research_query(research_root, query)["documents"]
    return result


def resolve_component(root: Path, value: str) -> tuple[Path, dict | None]:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    is_path = path.is_dir()
    ref = _validate_package(path)["component_ref"] if is_path else value
    parse_component_ref(ref)
    inventory = discover_components(root)
    matches = [item for item in inventory["assets"] if item["component_ref"] == ref]
    if any(item.get("conflict") for item in matches):
        raise ComponentError(f"Conflicting identity/version across asset sources: {ref}")
    available = [item for item in matches if item["available"] and (not is_path or Path(item["path"]) == path.resolve())]
    if not available:
        detail = next((item["error"] for item in inventory["errors"] if item["path"] == str(path)), "")
        raise ComponentError(f"Asset is not accepted or compatible: {ref}" + (f": {detail}" if detail else ""))
    available.sort(key=lambda item: item["origin"] != "accepted")
    selected, acceptance = Path(available[0]["path"]), available[0]["acceptance"]
    report = _validate_package(selected, ref)
    if acceptance is not None:
        validate_component_acceptance(acceptance, report, runtime_root=root)
    return selected, acceptance


def _accepted_closure(store, references, *, runtime_root=None, visiting=None):
    from asset_contract import validate_reference
    if not isinstance(references, list):
        raise ComponentError("Asset references must be a list")
    visiting, resolved = set(visiting or ()), {}

    def visit(reference):
        validate_reference(reference)
        ref = reference["ref"]
        if ref in visiting:
            raise ComponentError(f"Cyclic asset dependency: {ref}")
        if ref in resolved:
            if any(reference[key] != resolved[ref][key] for key in ("kind", "package_sha256")):
                raise ComponentError(f"Conflicting exact asset references: {ref}")
            return
        relative = _relative(ref)
        package = _target(store, (Path("packages") / relative).as_posix())
        record = _target(store, (Path("acceptances") / relative / "acceptance.json").as_posix())
        if not package.is_dir() or not record.is_file():
            raise ComponentError(f"Asset dependency is not accepted: {ref}")
        report = _validate_package(package, ref)
        if (report["metadata"].get("kind") != reference["kind"] or report["package_sha256"] != reference["package_sha256"]):
            raise ComponentError(f"Asset reference kind/hash mismatch: {ref}")
        acceptance = _read_json(record)
        validate_component_acceptance(acceptance, report, runtime_root=runtime_root)
        candidate = _target(store, (Path("candidates") / relative / "package").as_posix())
        if candidate.exists() and _validate_package(candidate, ref)["package_sha256"] != reference["package_sha256"]:
            raise ComponentError(f"Conflicting identity/version across asset sources: {ref}")
        visiting.add(ref)
        for dependency in report["metadata"].get("asset_dependencies", []):
            visit(dependency)
        visiting.remove(ref)
        resolved[ref] = {**reference, "path": str(package), "metadata": report["metadata"], "acceptance": acceptance}

    for reference in references:
        visit(reference)
    return list(resolved.values())


def resolve_asset_closure(root: Path, references: list[dict]) -> list[dict]:
    """Resolve dependency-first accepted packages, never candidates or floating versions."""
    closure = _accepted_closure(asset_store_root(root), references, runtime_root=root)
    resolved_refs = {item["ref"] for item in closure}
    for item in discover_components(root)["assets"]:
        if item["component_ref"] in resolved_refs and item.get("conflict"):
            raise ComponentError(f"Conflicting identity/version across asset sources: {item['component_ref']}")
    return closure


def resolve_asset(root: Path, reference: dict) -> tuple[Path, dict, dict]:
    closure = resolve_asset_closure(root, [reference])
    item = next(item for item in closure if item["ref"] == reference["ref"])
    path = Path(item["path"])
    return path, _validate_package(path, item["ref"]), item["acceptance"]
