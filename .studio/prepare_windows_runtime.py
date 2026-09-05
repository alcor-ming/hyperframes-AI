"""Explicit build-time download/seed step; never called by a creation command."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen
import zipfile

REPO = Path(__file__).resolve().parent.parent
VERSIONS = {"hyperframes": "0.8.27", "gsap": "3.14.2", "three": "0.160.0"}
ARCHIVES = [
    {"kind": "zip", "file": "node-v22.22.2-win-x64.zip", "target": "runtime/node",
     "strip_prefix": "node-v22.22.2-win-x64", "url": "https://nodejs.org/dist/v22.22.2/node-v22.22.2-win-x64.zip"},
    {"kind": "zip", "file": "chrome-headless-shell-152.0.7977.30-win64.zip", "target": "runtime/chromium",
     "strip_prefix": "chrome-headless-shell-win64", "url": "https://storage.googleapis.com/chrome-for-testing-public/152.0.7977.30/win64/chrome-headless-shell-win64.zip"},
    {"kind": "zip", "file": "ffmpeg-7.1.1-essentials_build.zip", "target": "runtime/ffmpeg",
     "strip_prefix": "ffmpeg-7.1.1-essentials_build", "url": "https://github.com/GyanD/codexffmpeg/releases/download/7.1.1/ffmpeg-7.1.1-essentials_build.zip"},
]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def seed_lock(source: Path, metadata: list[Path], output: Path) -> None:
    lock = read(source)
    if lock.get("lockfileVersion") != 3 or lock["packages"]["node_modules/hyperframes"]["version"] != VERSIONS["hyperframes"]:
        raise ValueError("Seed must be a complete lockfileVersion 3 for HyperFrames 0.8.27")
    for path in metadata:
        package = read(path)
        name = package["name"]
        if name not in ("gsap", "three") or package["version"] != VERSIONS[name] or package.get("dependencies"):
            raise ValueError("Expected dependency-free GSAP 3.14.2 or Three 0.160.0 metadata")
        lock["packages"][f"node_modules/{name}"] = {
            "version": package["version"], "resolved": package["dist"]["tarball"],
            "integrity": package["dist"]["integrity"], "license": package["license"],
        }
    lock["name"] = "hyperframes-windows-runtime"
    lock["version"] = "1.0.0"
    lock["packages"][""] = {"name": lock["name"], "version": lock["version"], "dependencies": VERSIONS}
    validate_npm_lock(lock)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


def validate_npm_lock(lock: dict) -> None:
    for name, version in VERSIONS.items():
        if lock["packages"][f"node_modules/{name}"]["version"] != version:
            raise ValueError(f"Wrong locked {name} version")
    for name, package in lock["packages"].items():
        if not name:
            continue
        parsed = urlparse(package.get("resolved", ""))
        if parsed.scheme != "https" or parsed.hostname != "registry.npmjs.org" or parsed.username or parsed.password or not package.get("integrity", "").startswith("sha512-"):
            raise ValueError(f"Expected HTTPS npm registry URL and SHA512 integrity: {name}")


def download(url: str, target: Path, expected: str | None = None) -> str:
    if not target.exists():
        partial = target.with_suffix(target.suffix + ".partial")
        try:
            with urlopen(url, timeout=120) as response, partial.open("wb") as output:
                shutil.copyfileobj(response, output)
            if expected and digest(partial) != expected:
                raise ValueError(f"Downloaded asset failed SHA256: {target.name}")
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)
    measured = digest(target)
    if expected and measured != expected:
        raise ValueError(f"Cached asset failed SHA256: {target.name}")
    return measured


def python_url(asset: dict, python_version: str) -> str:
    if asset["kind"] == "python":
        return f"https://www.python.org/ftp/python/{python_version}/{asset['file']}"
    name, version = asset["file"].split("-")[:2]
    with urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=30) as response:
        metadata = json.load(response)
    match = next(item for item in metadata["urls"] if item["filename"] == asset["file"])
    if match["digests"]["sha256"] != asset["sha256"]:
        raise ValueError(f"PyPI metadata differs from locked SHA256: {asset['file']}")
    return match["url"]


def npm_archive(lock_path: Path, cache: Path) -> Path:
    lock = read(lock_path)
    validate_npm_lock(lock)
    archive = cache / "hyperframes-0.8.27-windows-npm.zip"
    with tempfile.TemporaryDirectory(prefix="hf-windows-npm-", dir=cache) as temporary:
        project = Path(temporary)
        (project / "package-lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        (project / "package.json").write_text(json.dumps({**lock["packages"][""], "private": True}), encoding="utf-8")
        subprocess.run(["npm", "ci", "--ignore-scripts", "--os=win32", "--cpu=x64", "--bin-links=false",
                        "--no-audit", "--no-fund", "--cache", str(cache / "npm-cache")], cwd=project, check=True)
        partial = archive.with_suffix(".partial")
        with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
            for path in sorted(project.rglob("*")):
                if path.is_symlink():
                    raise ValueError(f"Unexpected npm symlink: {path.relative_to(project)}")
                if path.is_file():
                    entry = zipfile.ZipInfo(path.relative_to(project).as_posix(), (2026, 1, 1, 0, 0, 0))
                    entry.external_attr = 0o644 << 16
                    bundle.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
        partial.replace(archive)
    return archive


def prepare(cache: Path, npm_lock: Path, output_lock: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    lock = read(REPO / "windows-runtime.lock.json")
    assets = [asset for asset in lock["assets"] if asset["kind"] in ("python", "wheel")]
    for asset in assets:
        target = cache / asset["file"]
        if target.exists():
            download("", target, asset["sha256"])
        else:
            download(python_url(asset, lock["python"]), target, asset["sha256"])
    with urlopen("https://nodejs.org/dist/v22.22.2/SHASUMS256.txt", timeout=30) as response:
        node_checksums = {fields[1].lstrip("*"): fields[0] for line in response.read().decode("ascii").splitlines() if (fields := line.split())}
    for source in ARCHIVES:
        asset = dict(source)
        expected = node_checksums[asset["file"]] if asset["target"] == "runtime/node" else None
        asset["sha256"] = download(asset["url"], cache / asset["file"], expected)
        assets.append(asset)
    npm = npm_archive(npm_lock, cache)
    assets.append({"kind": "npm-tree", "file": npm.name, "target": "runtime/npm", "sha256": digest(npm),
                   "package_lock_sha256": digest(npm_lock)})
    lock["assets"] = assets
    lock["versions"].update({"ffmpeg": "7.1.1", "ffprobe": "7.1.1"})
    lock.pop("pending_assets", None)
    # Check every required archive member before replacing the public lock.
    supplied = set()
    for asset in assets:
        if asset["kind"] in ("python", "wheel"):
            continue
        prefix = asset.get("strip_prefix", "").rstrip("/")
        with zipfile.ZipFile(cache / asset["file"]) as bundle:
            for name in bundle.namelist():
                if prefix and not name.startswith(prefix + "/"):
                    continue
                supplied.add(asset["target"] + "/" + (name[len(prefix) + 1:] if prefix else name))
    missing = sorted(set(lock["required_files"]) - supplied)
    if missing:
        raise ValueError("Prepared archives are incomplete: " + ", ".join(missing))
    output_lock.parent.mkdir(parents=True, exist_ok=True)
    output_lock.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(output_lock)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    seed = commands.add_parser("seed-lock", help="No downloads; merge a verified HF lock and local registry metadata")
    seed.add_argument("--from-npm-lock", type=Path, required=True)
    seed.add_argument("--metadata", type=Path, nargs=2, required=True)
    seed.add_argument("--output", type=Path, default=REPO / "windows-npm.lock.json")
    build = commands.add_parser("prepare", help="Explicit build-time downloads; obtain download authorization before running")
    build.add_argument("--cache", type=Path, required=True)
    build.add_argument("--npm-lock", type=Path, default=REPO / "windows-npm.lock.json")
    build.add_argument("--output-lock", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "seed-lock":
        seed_lock(args.from_npm_lock, args.metadata, args.output)
    else:
        prepare(args.cache.resolve(), args.npm_lock.resolve(), args.output_lock.resolve())


if __name__ == "__main__":
    main()
