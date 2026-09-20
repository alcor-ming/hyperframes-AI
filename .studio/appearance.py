"""Resolve accepted visual assets once; replay only the frozen local closure."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

SLOTS = ("reveal", "emphasis", "exit", "transition")
RATIOS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:3": (1440, 1080), "3:4": (1080, 1440), "4:5": (1080, 1350)}


class AppearanceError(ValueError):
    pass


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def is_asset_appearance(settings: dict) -> bool:
    return isinstance(settings.get("theme"), dict) or isinstance(settings.get("background"), dict) or "motion" in settings


def _reference(value: object, kind: str) -> dict:
    from component_harness import parse_component_ref
    import re
    if not isinstance(value, dict) or set(value) != {"ref", "kind", "package_sha256"}:
        raise AppearanceError(f"{kind} requires an exact ref/kind/package_sha256 reference")
    if value["kind"] != kind or not isinstance(value["ref"], str) or not isinstance(value["package_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["package_sha256"]):
        raise AppearanceError(f"Invalid {kind} reference")
    parse_component_ref(value["ref"])
    return deepcopy(value)


def _parameters(metadata: dict, layers: list[tuple[str, dict]]) -> tuple[dict, dict]:
    from asset_contract import validate_parameter
    schema = metadata.get("parameters", {})
    values, sources = {}, {}
    for name, spec in schema.items():
        if "default" in spec:
            values[name], sources[name] = deepcopy(spec["default"]), "asset"
    for source, layer in layers:
        if not isinstance(layer, dict) or set(layer) - set(schema):
            raise AppearanceError("Unknown appearance parameter override")
        for name, value in layer.items():
            validate_parameter(value, schema[name])
            values[name], sources[name] = deepcopy(value), source
    return values, sources


def resolve(root: Path, account: dict, overrides: dict | None = None) -> dict:
    from asset_store import resolve_asset_closure
    from component_harness import parse_component_ref
    overrides = {} if overrides is None else overrides
    allowed = {"theme", "background", "motion", "mode", "ratio", "width", "height", "fps", "seed", "parameters"}
    if not isinstance(overrides, dict) or set(overrides) - allowed:
        raise AppearanceError("Unknown appearance selection override")
    selected = {**account, **overrides}
    selections = {kind: _reference(selected.get(kind), kind) for kind in ("theme", "background")}
    motion = account.get("motion", {})
    explicit_motion = overrides.get("motion", {})
    if not isinstance(motion, dict) or not isinstance(explicit_motion, dict) or (set(motion) | set(explicit_motion)) - set(SLOTS):
        raise AppearanceError("Unknown motion slot")
    motion = {**motion, **explicit_motion}
    selections["motion"] = {}
    refs = [selections["theme"], selections["background"]]
    for slot in SLOTS:
        value = motion.get(slot)
        if value is not None:
            if not isinstance(value, dict) or set(value) != {"asset", "entry"} or not isinstance(value["entry"], str) or not value["entry"]:
                raise AppearanceError("Motion slot requires asset and entry")
            value = {"asset": _reference(value["asset"], "motion"), "entry": value["entry"]}
            refs.append(value["asset"])
        selections["motion"][slot] = value
    mode = selected.get("mode", "text-led")
    if mode not in ("text-led", "animation-led"):
        raise AppearanceError("Unknown narrative mode")
    ratio = selected.get("ratio", "16:9")
    if not isinstance(ratio, str):
        raise AppearanceError("Ratio must be a string")
    if ratio == "source":
        width, height = selected.get("width"), selected.get("height")
        if type(width) is not int or type(height) is not int or min(width, height) <= 0:
            raise AppearanceError("source ratio requires concrete width and height before freezing")
        from math import gcd
        divisor = gcd(width, height)
        ratio = f"{width // divisor}:{height // divisor}"
    elif ratio in RATIOS:
        width, height = RATIOS[ratio]
        if "width" in selected or "height" in selected:
            width, height = selected.get("width", width), selected.get("height", height)
            a, b = map(int, ratio.split(":"))
            if type(width) is not int or type(height) is not int or min(width, height) <= 0 or width * b != height * a:
                raise AppearanceError("Dimensions do not match ratio")
    else:
        raise AppearanceError("Unknown ratio")
    fps, seed = selected.get("fps", 30), selected.get("seed", 0)
    if type(fps) is not int or not 1 <= fps <= 240 or type(seed) is not int:
        raise AppearanceError("fps must be an integer in 1..240 and seed an integer")
    closure = resolve_asset_closure(root, refs)
    parameter_layers = [("account", account.get("overrides", {})), ("explicit", overrides.get("parameters", {}))]
    values, sources = _resolve_parameters(closure, selections, ratio, parameter_layers)
    frozen = []
    for item in closure:
        identity, version = parse_component_ref(item["ref"])
        frozen.append({key: item[key] for key in ("ref", "kind", "package_sha256") } | {"version": version, "vendor_path": f"vendor/components/{identity}/v{version}"})
    lock = {"schema_version": 1, "resolver_version": 1, "contract_version": 1,
            "hash_algorithm": "sha256-canonical-json-utf8-v1", "account": {"id": account.get("id"), "revision": account.get("revision"), "sha256": digest(account)},
            "selection": selections, "assets": frozen, "mode": mode, "ratio": ratio, "width": width, "height": height, "fps": fps, "seed": seed, "time_unit": "seconds",
            "overrides": {"account": deepcopy(account.get("overrides", {})), "explicit": deepcopy(overrides.get("parameters", {}))}, "parameters": values, "sources": sources}
    lock["sha256"] = digest(lock)
    return lock


def _resolve_parameters(closure, selections, ratio, parameter_layers):
    from asset_contract import validate_declaration
    by_ref = {item["ref"]: item for item in closure}
    for _, layer in parameter_layers:
        if not isinstance(layer, dict) or set(layer) - {"theme", "background", "motion"}:
            raise AppearanceError("Unknown appearance override scope")
        if "motion" in layer and (not isinstance(layer["motion"], dict) or set(layer["motion"]) - set(SLOTS)):
            raise AppearanceError("Unknown motion override slot")
        if any(not isinstance(params, dict) for params in layer.get("motion", {}).values()):
            raise AppearanceError("Motion parameter overrides must be objects")
    values, sources = {"motion": {}}, {"motion": {}}
    for role, reference in (("theme", selections["theme"]), ("background", selections["background"]), *((slot, value["asset"]) for slot, value in selections["motion"].items() if value)):
        item = by_ref[reference["ref"]]
        metadata = item["metadata"]
        ratios = metadata.get("compatibility", {}).get("ratios")
        if ratios and ratio not in ratios:
            raise AppearanceError(f"Asset {item['ref']} does not support ratio {ratio}")
        payload = json.loads((Path(item["path"]) / metadata["entry"]).read_text(encoding="utf-8-sig"))
        if role == "background" and payload.get("renderer") not in ("solid", "transparent"):
            raise AppearanceError("Dynamic background is not supported by this resolver")
        if role in SLOTS:
            if selections["motion"][role]["entry"] not in payload.get("slots", {}):
                raise AppearanceError("Unknown motion preset entry")
            layers = [(name, layer.get("motion", {}).get(role, {})) for name, layer in parameter_layers]
            effective, origin = _parameters(metadata, layers)
            values["motion"][role], sources["motion"][role] = effective, origin
        else:
            layers = [(name, layer.get(role, {})) for name, layer in parameter_layers]
            effective, origin = _parameters(metadata, layers)
            values[role], sources[role] = effective, origin
        for path, value in effective.items():
            parts, target = path.split("."), payload
            for part in parts[:-1]:
                if not isinstance(target, dict) or part not in target:
                    raise AppearanceError(f"Parameter path is absent: {path}")
                target = target[part]
            if not isinstance(target, dict) or parts[-1] not in target:
                raise AppearanceError(f"Parameter path is absent: {path}")
            target[parts[-1]] = deepcopy(value)
        validate_declaration(payload, metadata, Path(item["path"]))
    for _, layer in parameter_layers:
        if any(selections["motion"][slot] is None and params for slot, params in layer.get("motion", {}).items()):
            raise AppearanceError("Cannot override a disabled motion slot")
    return values, sources


def _check_lock(lock: dict) -> None:
    from component_harness import parse_component_ref
    import re
    required = {"schema_version", "resolver_version", "contract_version", "hash_algorithm", "account", "selection", "assets", "mode", "ratio", "width", "height", "fps", "seed", "time_unit", "overrides", "parameters", "sources", "sha256"}
    if not isinstance(lock, dict) or set(lock) != required or any(type(lock[key]) is not int or lock[key] != 1 for key in ("schema_version", "resolver_version", "contract_version")) or digest({key: value for key, value in lock.items() if key != "sha256"}) != lock.get("sha256"):
        raise AppearanceError("Appearance lock schema or hash mismatch")
    if lock["hash_algorithm"] != "sha256-canonical-json-utf8-v1" or lock["time_unit"] != "seconds" or lock["mode"] not in ("text-led", "animation-led"):
        raise AppearanceError("Invalid frozen appearance contract")
    if not isinstance(lock["ratio"], str) or not re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", lock["ratio"]):
        raise AppearanceError("Invalid frozen ratio")
    a, b = map(int, lock["ratio"].split(":"))
    if any(type(lock[key]) is not int or lock[key] <= 0 for key in ("width", "height", "fps")) or lock["fps"] > 240 or type(lock["seed"]) is not int or lock["width"] * b != lock["height"] * a:
        raise AppearanceError("Invalid frozen dimensions, fps or seed")
    account = lock["account"]
    if not isinstance(account, dict) or set(account) != {"id", "revision", "sha256"} or not isinstance(account["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", account["sha256"]) or account["id"] is not None and not isinstance(account["id"], str) or account["revision"] is not None and (type(account["revision"]) is not int or account["revision"] < 1):
        raise AppearanceError("Invalid frozen account identity")
    if not isinstance(lock["assets"], list):
        raise AppearanceError("Invalid frozen asset closure")
    assets = {}
    for item in lock["assets"]:
        if not isinstance(item, dict) or set(item) != {"ref", "kind", "package_sha256", "version", "vendor_path"} or item["kind"] not in ("theme", "background", "motion", "module", "media"):
            raise AppearanceError("Invalid frozen asset")
        reference = _reference({key: item[key] for key in ("ref", "kind", "package_sha256")}, item["kind"])
        identity, version = parse_component_ref(reference["ref"])
        if reference["ref"] in assets or type(item["version"]) is not int or version != item["version"] or item["vendor_path"] != f"vendor/components/{identity}/v{version}":
            raise AppearanceError("Frozen asset identity or path mismatch")
        assets[reference["ref"]] = reference
    selection = lock["selection"]
    if not isinstance(selection, dict) or set(selection) != {"theme", "background", "motion"} or not isinstance(selection["motion"], dict) or set(selection["motion"]) != set(SLOTS):
        raise AppearanceError("Invalid frozen appearance selections")
    references = [(selection[kind], kind) for kind in ("theme", "background")]
    for value in selection["motion"].values():
        if value is not None:
            if not isinstance(value, dict) or set(value) != {"asset", "entry"} or not isinstance(value["entry"], str) or not value["entry"]:
                raise AppearanceError("Invalid frozen motion selection")
            references.append((value["asset"], "motion"))
    for reference, kind in references:
        checked = _reference(reference, kind)
        if assets.get(checked["ref"]) != checked:
            raise AppearanceError("Frozen selection differs from asset closure")
    if not isinstance(lock["overrides"], dict) or set(lock["overrides"]) != {"account", "explicit"} or any(not isinstance(lock[key], dict) for key in ("parameters", "sources")):
        raise AppearanceError("Invalid frozen parameter fields")


def materialize(root: Path, project: Path, lock: dict) -> dict:
    from asset_store import resolve_asset_closure
    from component_harness import install_component, _atomic_json, parse_component_ref
    from work_requests import safe
    import shutil
    _check_lock(lock)
    runtime = safe(project, "runtime/appearance.js")
    source = Path(__file__).parent / "runtime/appearance.js"
    if runtime.exists() and runtime.read_bytes() != source.read_bytes():
        raise AppearanceError("Existing appearance runtime differs; keep the frozen project unchanged")
    config_path = safe(project, "project-config.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8-sig")) if config_path.exists() else {}
    except (OSError, ValueError) as exc:
        raise AppearanceError("Appearance needs a valid project-config.json") from exc
    if not isinstance(config, dict) or not isinstance(config.get("snapshot_dependencies", []), list) or not all(isinstance(item, str) for item in config.get("snapshot_dependencies", [])):
        raise AppearanceError("snapshot_dependencies must be a list of local files")
    references = [{key: item[key] for key in ("ref", "kind", "package_sha256")} for item in lock["assets"]]
    closure = resolve_asset_closure(root, references)
    selected = {lock["selection"][kind]["ref"] for kind in ("theme", "background")}
    selected.update(value["asset"]["ref"] for value in lock["selection"]["motion"].values() if value)
    for item in closure:
        binding = {"schema_version": 3, "component_ref": item["ref"]}
        if item["ref"] in selected:
            binding["usage"] = {"role": item["kind"], "required": True}
        else:
            binding["scope"] = "dependency"
        identity, version = parse_component_ref(item["ref"])
        install_component(Path(item["path"]), project, binding,
                          binding_path=f"component-bindings/appearance.{identity}.v{version}.json",
                          expected_ref=item["ref"], acceptance=item["acceptance"])
    _atomic_json(project / "appearance-lock.json", lock)
    if not runtime.exists():
        runtime.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, runtime)
    verify(project, lock)
    declared = set(config.get("snapshot_dependencies", []))
    declared.update(("appearance-lock.json", "runtime/appearance.js", "COMPONENT_LOCK.json"))
    for item in lock["assets"]:
        identity, version = parse_component_ref(item["ref"])
        declared.add(f"component-bindings/appearance.{identity}.v{version}.json")
        declared.update(path.relative_to(project).as_posix() for path in (project / item["vendor_path"]).rglob("*") if path.is_file())
    _atomic_json(config_path, {**config, "snapshot_dependencies": sorted(declared)})
    return deepcopy(lock)


def verify(project: Path, lock: dict) -> dict:
    from component_harness import verify_installation, validate_component_release
    from work_requests import safe
    _check_lock(lock)
    disk = safe(project, "appearance-lock.json")
    if not disk.is_file() or digest(json.loads(disk.read_text(encoding="utf-8"))) != digest(lock):
        raise AppearanceError("Frozen appearance lock differs from Variant")
    report = verify_installation(project)
    installed = json.loads((project / "COMPONENT_LOCK.json").read_text(encoding="utf-8"))
    records = {item["component_ref"]: item for item in installed["components"]}
    closure = []
    for item in lock["assets"]:
        record = records.get(item["ref"], {})
        if record.get("work_package_sha256") != item["package_sha256"] or record.get("vendor_path") != item["vendor_path"] or record.get("asset_kind") != item["kind"]:
            raise AppearanceError("Frozen appearance dependency differs from installed closure")
        path = safe(project, item["vendor_path"])
        metadata = validate_component_release(path, expected_ref=item["ref"], allow_unapproved=True)["metadata"]
        closure.append({**item, "path": path, "metadata": metadata})
    values, sources = _resolve_parameters(closure, lock["selection"], lock["ratio"], list(lock["overrides"].items()))
    if digest(values) != digest(lock["parameters"]) or digest(sources) != digest(lock["sources"]):
        raise AppearanceError("Frozen effective parameters differ from accepted assets and overrides")
    return report
