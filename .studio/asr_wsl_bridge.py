#!/usr/bin/env python3
"""Run the shared WSL ASR from the native Windows Harness."""

from __future__ import annotations

import os
import ntpath
from pathlib import Path
import subprocess
import sys


DEFAULT_DISTRO = "Ubuntu"
DEFAULT_ASR_SCRIPT = "/home/jym/workspace/_external/scripts/asr.sh"
WORKSTORE = r"D:\AI\AI+hyperframes"
WSL_EXE = r"C:\Windows\System32\wsl.exe"
WSL_COMMAND = (WSL_EXE, "--distribution", DEFAULT_DISTRO, "--exec", "/bin/sh", "-c")
WSL_SCRIPT = r'''
set -eu
: "${HYPERFRAMES_BRIDGE_ASR_SCRIPT:?missing WSL ASR script}"
: "${HYPERFRAMES_BRIDGE_VIDEO:?missing Windows video path}"
: "${HYPERFRAMES_BRIDGE_OUTPUT:?missing Windows output path}"
: "${HYPERFRAMES_BRIDGE_LANGUAGE:?missing language}"
command -v wslpath >/dev/null 2>&1 || { echo "asr-wsl: wslpath is unavailable" >&2; exit 127; }
test -x "$HYPERFRAMES_BRIDGE_ASR_SCRIPT" || { echo "asr-wsl: ASR script is unavailable: $HYPERFRAMES_BRIDGE_ASR_SCRIPT" >&2; exit 126; }
video=$(wslpath -a -u "$HYPERFRAMES_BRIDGE_VIDEO")
output=$(wslpath -a -u "$HYPERFRAMES_BRIDGE_OUTPUT")
test -f "$video" || { echo "asr-wsl: video is unavailable in WSL: $video" >&2; exit 2; }
mkdir -p "$output"
"$HYPERFRAMES_BRIDGE_ASR_SCRIPT" check
exec "$HYPERFRAMES_BRIDGE_ASR_SCRIPT" transcribe-faster "$video" --output-dir "$output" --language "$HYPERFRAMES_BRIDGE_LANGUAGE"
'''.strip()
BRIDGE_ENV = (
    "HYPERFRAMES_BRIDGE_ASR_SCRIPT",
    "HYPERFRAMES_BRIDGE_VIDEO",
    "HYPERFRAMES_BRIDGE_OUTPUT",
    "HYPERFRAMES_BRIDGE_LANGUAGE",
)


def usage() -> int:
    print(
        "usage: asr-wsl.cmd transcribe-faster VIDEO --output-dir DIR --language LANGUAGE",
        file=sys.stderr,
    )
    return 2


def parse(arguments: list[str]) -> tuple[str, str, str] | None:
    if (
        len(arguments) != 6
        or arguments[0] != "transcribe-faster"
        or arguments[2] != "--output-dir"
        or arguments[4] != "--language"
    ):
        return None
    video, output, language = arguments[1], arguments[3], arguments[5]
    if not video or not output or not language:
        return None
    return video, output, language


def workstore_path(value: str) -> str | None:
    if os.name == "nt":
        absolute = str(Path(value).resolve(strict=False))
        root = str(Path(WORKSTORE).resolve(strict=False))
    else:
        absolute = ntpath.abspath(value)
        root = ntpath.abspath(WORKSTORE)
    try:
        inside = ntpath.commonpath((ntpath.normcase(root), ntpath.normcase(absolute)))
    except ValueError:
        return None
    return absolute if inside == ntpath.normcase(root) else None


def bridge(arguments: list[str], environ: dict[str, str] | None = None) -> int:
    parsed = parse(arguments)
    if parsed is None:
        return usage()
    video, output, language = parsed
    video = workstore_path(video)
    output = workstore_path(output)
    if video is None or output is None:
        print(f"asr-wsl: video and output must stay inside {WORKSTORE}", file=sys.stderr)
        return 2
    env = dict(os.environ if environ is None else environ)
    env.update(
        {
            "HYPERFRAMES_BRIDGE_ASR_SCRIPT": DEFAULT_ASR_SCRIPT,
            "HYPERFRAMES_BRIDGE_VIDEO": video,
            "HYPERFRAMES_BRIDGE_OUTPUT": output,
            "HYPERFRAMES_BRIDGE_LANGUAGE": language,
        }
    )
    env["WSLENV"] = ":".join(BRIDGE_ENV)
    try:
        return subprocess.run((*WSL_COMMAND, WSL_SCRIPT), env=env, check=False).returncode
    except FileNotFoundError:
        print("asr-wsl: wsl.exe is unavailable", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(bridge(sys.argv[1:]))
