"""Bind Windows creation commands to one immutable installed runtime."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def runtime_paths(root: Path) -> dict[str, Path]:
    npm = root / "runtime" / "npm" / "node_modules"
    return {
        "HYPERFRAMES_NODE": root / "runtime/node/node.exe",
        "HYPERFRAMES_CLI": npm / "hyperframes/bin/hyperframes.mjs",
        "HYPERFRAMES_DIST": npm / "hyperframes/dist",
        "HYPERFRAMES_BROWSER_PATH": root / "runtime/chromium/chrome-headless-shell.exe",
        "HYPERFRAMES_FFMPEG_PATH": root / "runtime/ffmpeg/bin/ffmpeg.exe",
        "HYPERFRAMES_FFPROBE_PATH": root / "runtime/ffmpeg/bin/ffprobe.exe",
        "GSAP_FILE": npm / "gsap/dist/gsap.min.js",
        "THREE_FILE": npm / "three/build/three.min.js",
    }


def environment(root: Path, home: Path, session: dict | None = None) -> dict[str, str]:
    if session and Path(session["release_root"]).resolve() != root.resolve():
        raise ValueError("Session runtime differs from launcher; start a new session")
    cache = home / "sessions" / (session["id"] if session else "diagnostics") / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in runtime_paths(root).items()})
    env.update({
        "HYPERFRAMES_AI_ROOT": str(root),
        "HYPERFRAMES_AI_CONFIG": str(home / "config/local.json"),
        "HYPERFRAMES_AI_REVIEW": "1" if session and session.get("review") else "0",
        "HYPERFRAMES_AI_VERSION": read_json(root / ".release.json")["release"],
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
        "TMP": str(cache), "TEMP": str(cache),
        "HYPERFRAMES_EXTRACT_CACHE_DIR": str(cache / "frames"),
        "PUPPETEER_CACHE_DIR": str(cache / "browser"),
        "HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1",
    })
    env["PATH"] = os.pathsep.join([str(root / "runtime/node"), str(root / "runtime/ffmpeg/bin"), env.get("PATH", "")])
    env["FFMPEG_PATH"] = env["HYPERFRAMES_FFMPEG_PATH"]
    env["FFPROBE_PATH"] = env["HYPERFRAMES_FFPROBE_PATH"]
    env["IMAGEIO_FFMPEG_EXE"] = env["FFMPEG_PATH"]
    if session:
        env["HYPERFRAMES_AI_CONFIG"] = str(home / "sessions" / session["id"] / "local.json")
        env["HYPERFRAMES_AI_WORK_ROOT"] = read_json(Path(env["HYPERFRAMES_AI_CONFIG"]))["work_root"]
    return env


def start_session(root: Path, home: Path, review_root: Path | None = None) -> Path:
    manifest = read_json(root / ".release.json")
    candidate = manifest.get("channel") == "candidate"
    if candidate and review_root is None:
        raise ValueError("Candidate sessions require --review-root (isolated WorkStore)")
    config = read_json(home / "config/local.json")
    if review_root:
        review_root = review_root.resolve()
        marker = review_root / ".runtime/review.json"
        if not marker.is_file():
            raise ValueError("Review WorkStore requires .runtime/review.json")
        if review_root == Path(config["work_root"]).resolve():
            raise ValueError("Review cannot use the production WorkStore")
        config["work_root"] = str(review_root)
    for name in ("active", "parked", "archive"):
        if not (Path(config["work_root"]) / "works" / name).is_dir():
            raise ValueError(f"WorkStore missing works/{name}")
    session_id = uuid.uuid4().hex
    directory = home / "sessions" / session_id
    directory.mkdir(parents=True)
    binding = {"id": session_id, "release_root": str(root.resolve()), "release": manifest["release"],
               "review": bool(review_root), "runtime": read_json(root / "windows-runtime.lock.json")}
    for name, value in (("session.json", binding), ("local.json", config)):
        (directory / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    # Each launcher carries its own binding; changing current cannot affect it.
    runtime_prefix = "%~dp0" + os.path.relpath(root.resolve(), directory.resolve()).replace("/", "\\").replace("%", "%%")
    (directory / "work.cmd").write_text(
        '@echo off\nsetlocal DisableDelayedExpansion\nset "PYTHONUTF8=1"\n'
        'set "HYPERFRAMES_AI_SESSION=%~dp0session.json"\n'
        f'"{runtime_prefix}\\runtime\\python\\python.exe" -B "{runtime_prefix}\\.studio\\windows_runtime.py" %*\n'
        'exit /b %ERRORLEVEL%\n', encoding="ascii")
    (directory / "work.ps1").write_text(
        '$env:HYPERFRAMES_AI_SESSION = Join-Path $PSScriptRoot "session.json"\n'
        f"& '{str(root / 'work.ps1').replace(chr(39), chr(39)*2)}' @args\nexit $LASTEXITCODE\n", encoding="utf-8-sig")
    (directory / "AGENTS.md").write_text(
        "# Windows Creation Session\n\n"
        f"Pinned runtime: `{root}`. Review: `{bool(review_root)}`.\n"
        "Use this directory's `work.cmd` for every command. Do not resolve current again.\n"
        f"Read the installed creation rules at `{root / 'AGENTS.md'}` and Skills under "
        f"`{root / '.agents/skills'}` by absolute path; never edit installed files.\n"
        "Work-local Slots, layout, timing and arrangement are creation; new reusable effects, "
        "shaders and Harness changes must be handed to WSL development.\n", encoding="utf-8")
    return directory


def doctor(root: Path, env: dict[str, str]) -> dict:
    lock = read_json(root / "windows-runtime.lock.json")
    result = {"release": read_json(root / ".release.json")["release"], "backend": "windows-native",
              "review": env["HYPERFRAMES_AI_REVIEW"] == "1", "runtime": str(root),
              "work_root": env.get("HYPERFRAMES_AI_WORK_ROOT") or (
                  read_json(Path(env["HYPERFRAMES_AI_CONFIG"])).get("work_root")
                  if Path(env["HYPERFRAMES_AI_CONFIG"]).is_file() else "not-configured"), "checks": {}}
    commands = {"node": [env["HYPERFRAMES_NODE"], "--version"],
                "hyperframes": [env["HYPERFRAMES_NODE"], env["HYPERFRAMES_CLI"], "--version"],
                "chromium": [env["HYPERFRAMES_BROWSER_PATH"], "--version"],
                "ffmpeg": [env["FFMPEG_PATH"], "-version"], "ffprobe": [env["FFPROBE_PATH"], "-version"]}
    for key, path in runtime_paths(root).items():
        result["checks"][key] = "available" if path.exists() else "not-installed"
    for relative in lock.get("required_files", []):
        result["checks"][relative] = "available" if (root / relative).is_file() else "not-installed"
    npm = root / "runtime/npm/node_modules"
    commands["native-modules"] = [env["HYPERFRAMES_NODE"], "-e",
        "const {createRequire}=require('node:module');const r=createRequire(process.argv[1]);"
        "for(const p of ['sharp','esbuild','onnxruntime-node'])r(p);console.log('available');",
        str(npm / "hyperframes/package.json")]
    commands["encoders"] = [env["FFMPEG_PATH"], "-hide_banner", "-encoders"]
    for name, command in commands.items():
        try:
            completed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30)
            result["checks"][name] = {"status": "available" if completed.returncode == 0 else "failed",
                                      "output": (completed.stdout or completed.stderr).splitlines()[:2]}
            expected = lock.get("versions", {}).get(name)
            if expected and expected not in completed.stdout + completed.stderr:
                result["checks"][name]["status"] = "version-mismatch"
            if name == "encoders":
                found = [codec for codec in ("libx264", "aac") if codec in completed.stdout]
                result["checks"][name] = {"status": "available" if len(found) == 2 and completed.returncode == 0 else "failed", "output": found}
        except (OSError, subprocess.TimeoutExpired) as error:
            result["checks"][name] = {"status": "unavailable", "error": str(error)}
    result["gpu"] = "pending-native-render-verification"
    result["fonts"] = "system-fonts; validate actual Work line breaks and glyph coverage"
    return result


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parent.parent
    binding_path = os.environ.get("HYPERFRAMES_AI_SESSION")
    session = read_json(Path(binding_path)) if binding_path else None
    home = Path(binding_path).resolve().parent.parent.parent if binding_path else Path(
        os.environ.get("HYPERFRAMES_AI_HOME") or str(Path(os.environ["LOCALAPPDATA"]) / "HyperFramesAI"))
    if argv[:2] == ["session", "start"]:
        parser = argparse.ArgumentParser()
        parser.add_argument("--review-root", type=Path)
        parsed = parser.parse_args(argv[2:])
        print(start_session(root, home, parsed.review_root))
        return 0
    env = environment(root, home, session)
    if argv == ["doctor"]:
        result = doctor(root, env)
        print(json.dumps(result, indent=2))
        return int(any(value == "not-installed" or isinstance(value, dict) and value["status"] != "available"
                       for value in result["checks"].values()))
    if not session and not (len(argv) == 3 and argv[:2] == ["review", "init"]):
        raise ValueError("Start a pinned creation session first: work.cmd session start")
    return subprocess.call([sys.executable, "-B", str(root / ".studio/work.py"), *argv], env=env)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as error:
        print(f"work: {error}", file=sys.stderr)
        raise SystemExit(1)
