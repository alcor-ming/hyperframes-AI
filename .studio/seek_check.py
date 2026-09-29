"""Static author-callback risks, not a proof of seek correctness or acceptance."""
import json
import os
from pathlib import Path
import subprocess

from dependency_scan import HTMLDependencies
from work_requests import safe


def findings(project, dependencies):
    units, result = [], []
    for name in dependencies:
        path = Path(name)
        if any(part in {"vendor", "runtime", "library", "libraries", "lib", "node_modules"} for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix not in {".js", ".mjs", ".cjs", ".html", ".htm"}:
            continue
        try:
            text = safe(project, name).read_text(encoding="utf-8-sig")
            scripts = HTMLDependencies(text).units if suffix in {".html", ".htm"} else [
                {"kind": "js", "mode": "module" if suffix == ".mjs" else "auto", "text": text}]
            units.extend({**unit, "file": name, "unit": index} for index, unit in enumerate(scripts) if unit["kind"] == "js")
        except (ValueError, OSError) as error:
            result.append({"kind": "seek_scan_unverified", "file": name, "detail": str(error)})
    if not units:
        return result
    try:
        scanned = subprocess.run([os.environ.get("HYPERFRAMES_NODE", "node"), str(Path(__file__).with_suffix(".cjs"))],
                                 input=json.dumps(units), capture_output=True, text=True, encoding="utf-8", timeout=60)
        if scanned.returncode:
            raise ValueError(scanned.stderr.strip())
        parsed = json.loads(scanned.stdout)
        if not isinstance(parsed, list) or not all(isinstance(item, dict) and "kind" in item for item in parsed):
            raise ValueError("Invalid seek scanner result")
        result.extend(parsed)
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        result.append({"kind": "seek_scan_unverified", "file": None, "detail": str(error)})
    return result
