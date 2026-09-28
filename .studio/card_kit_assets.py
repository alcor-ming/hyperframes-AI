"""Export the Harness-owned card runtime as an editable module AssetSource."""

from pathlib import Path
import json
import shutil

import asset_contract as CONTRACT
from component_harness import ComponentError


CARD_KIT_REF = "card-kit@v1"


def export_card_kit(runtime_root: Path, target: Path) -> dict:
    """Write only the explicit source target; packing and acceptance stay separate."""
    root = CONTRACT._root(Path(runtime_root) / ".studio")
    target = Path(target).expanduser().absolute()
    from asset_store import _guard_source
    _guard_source(target)
    for parent in (target, *target.parents):
        if parent.exists() or parent.is_symlink():
            CONTRACT._check_link(parent)
        if any((parent / name).exists() for name in ('COMPONENT_LOCK.json', 'HASHES.json', 'acceptance.json')):
            raise ComponentError('Card source must be outside installed projects and frozen packages')
    resolved = target.resolve()
    for protected in (root.resolve(), (Path(runtime_root) / 'runtime').resolve()):
        if resolved.is_relative_to(protected) or protected.is_relative_to(resolved):
            raise ComponentError('Card source must be separate from the installed Harness runtime')
    sources = {"card-kit.js": "runtime/card-kit.js",
               "card-kit.css": "runtime/card-kit.css",
               "USAGE.md": "spec/card-kit.md"}
    files = {}
    for name, relative in sources.items():
        CONTRACT._check_dependency(root, root / relative)
        files[name] = (root / relative).read_bytes()
    metadata = {"schema_version": 2, "id": "card-kit", "version": 1, "kind": "module",
                "entry": "card-kit.js", "contract_version": 1, "parameters": {},
                "compatibility": {"ratios": ["16:9", "9:16"]},
                "dependencies": ["card-kit.css"], "usage": "USAGE.md",
                "files": sorted(files),
                "description": "F01-F08 cue-driven cards with frozen Theme and split layers"}
    files["asset.json"] = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if target.exists():
        CONTRACT._root(target)
        existing = set()
        for path in target.rglob("*"):
            CONTRACT._check_link(path)
            if path.is_file():
                existing.add(path.relative_to(target).as_posix())
        if existing != set(files) or any((target / name).read_bytes() != data for name, data in files.items()):
            raise ComponentError(f"Asset identity/version already has different content: {CARD_KIT_REF}")
    else:
        target.mkdir(parents=True)
        try:
            for name, data in files.items():
                (target / name).write_bytes(data)
            CONTRACT._inputs(target)
        except Exception:
            shutil.rmtree(target)
            raise
    return {"component_ref": CARD_KIT_REF, "kind": "module", "source": str(target), "status": "source"}
