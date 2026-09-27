"""Import bundled SFX into editable AssetSource entries, never accept them."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess

from asset_contract import ID, _relative, _root
from component_harness import ComponentError, _atomic_json


CATEGORIES = set("click pop whoosh impact chime glitch error sparkle typing riser notification ping key".split())


def hit_offset(path):
    try:
        result = subprocess.run([os.environ.get("HYPERFRAMES_FFMPEG_PATH", "ffmpeg"),
            "-nostdin", "-v", "info", "-protocol_whitelist", "file,pipe", "-i", str(path),
            "-af", "silencedetect=noise=-40dB:d=0.001", "-f", "null", "-"],
            capture_output=True, text=True, timeout=120)
        if result.returncode:
            return 0, False
        events = re.findall(r"silence_(start|end):\s*([0-9.]+)", result.stderr)
        if events and events[0][0] == "start" and float(events[0][1]) <= 0.001:
            end = next((float(value) for event, value in events if event == "end"), None)
            return (end, True) if end is not None else (0, False)
        return 0, True
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return 0, False


def import_sfx(package_root: Path, source: Path) -> dict:
    bundled = _root(Path(package_root) / "dist/skills/media-use/audio/assets/sfx")
    _relative(bundled, "manifest.json")
    _relative(bundled, "CREDITS.md")
    try:
        manifest = json.loads((bundled / "manifest.json").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise ComponentError("Invalid SFX manifest") from exc
    if not isinstance(manifest, dict) or not manifest:
        raise ComponentError("SFX manifest must map ids to records")
    source = Path(source).absolute()
    if source.is_relative_to(bundled) or bundled.is_relative_to(source):
        raise ComponentError("SFX destination must be separate from bundled assets")
    if source.exists():
        _root(source)
    else:
        from asset_contract import _check_link
        for parent in source.parents:
            if parent.exists():
                _check_link(parent)
    entries = []
    for identity, item in manifest.items():
        if not ID.fullmatch(identity) or not isinstance(item, dict):
            raise ComponentError("Invalid SFX manifest entry")
        category = identity.split("-", 1)[0]
        if category not in CATEGORIES or not isinstance(item.get("description"), str) or not item["description"].strip():
            raise ComponentError("SFX requires category and description")
        filename = _relative(bundled, item.get("file"))
        if Path(filename).suffix.lower() != ".mp3":
            raise ComponentError("SFX entry must be MP3")
        target = source / identity
        if target.exists() or target.is_symlink():
            raise ComponentError(f"SFX destination already exists: {identity}")
        entries.append((identity, item, filename, target, category))
    created = []
    try:
        for identity, item, filename, target, category in entries:
            target.mkdir(parents=True, exist_ok=False)
            created.append(target)
            media = target / Path(filename).name
            shutil.copyfile(bundled / filename, media)
            shutil.copyfile(bundled / "CREDITS.md", target / "CREDITS.md")
            offset, estimated = hit_offset(media)
            _atomic_json(target / "asset.json", {"schema_version": 2, "id": identity,
                "version": 1, "kind": "media", "entry": media.name,
                "contract_version": 1, "parameters": {}, "compatibility": {},
                "purpose": item["description"], "description": item["description"],
                "tags": [category], "license": "CREDITS.md", "hit_offset": offset,
                "hit_offset_estimated": estimated})
    except Exception:
        for target in created:
            shutil.rmtree(target)
        raise
    return {"source": str(source), "imported": [identity for identity, *_ in entries], "accepted": False}
