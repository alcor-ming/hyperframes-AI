"""Use pinned upstream beat detection, never guess meter or downbeats."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from math_chain import make_beat_grid


def extract(audio, cli, beats_per_bar, first_downbeat):
    package = cli.parent.parent / "package.json"
    if json.loads(package.read_text(encoding="utf-8")).get("version") != "0.8.27":
        raise ValueError("Beat extraction requires pinned HyperFrames 0.8.27")
    browser = os.environ.get("HYPERFRAMES_BROWSER_PATH")
    if not browser or not Path(browser).is_file():
        raise ValueError("Beat extraction requires the installed browser; no automatic download")
    with audio.open("rb") as handle:
        audio_hash = hashlib.file_digest(handle, "sha256").hexdigest()
    with tempfile.TemporaryDirectory(prefix="hf-beats-") as directory:
        project = Path(directory)
        name = "audio" + audio.suffix.lower()
        shutil.copyfile(audio, project / name)
        (project / "index.html").write_text(f'<!doctype html><audio data-timeline-role="music" src="{name}"></audio>', encoding="utf-8")
        process = subprocess.run([os.environ.get("HYPERFRAMES_NODE", "node"), str(cli), "beats", str(project), "--json"],
                                 capture_output=True, text=True, timeout=180,
                                 env={**os.environ, "HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1"})
        if process.returncode:
            raise ValueError(f"Pinned beat extraction failed: {process.stderr or process.stdout}")
        data = json.loads((project / "beats" / (name + ".json")).read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1
                or data.get("audio") != name or not isinstance(data.get("beats"), list)
                or not all(isinstance(beat, dict) and "time" in beat for beat in data["beats"])):
            raise ValueError("Unexpected upstream beat file")
        with (project / name).open("rb") as handle:
            if hashlib.file_digest(handle, "sha256").hexdigest() != audio_hash:
                raise ValueError("Audio changed during beat extraction")
        with audio.open("rb") as handle:
            if hashlib.file_digest(handle, "sha256").hexdigest() != audio_hash:
                raise ValueError("Audio changed during beat extraction")
        return make_beat_grid([beat["time"] for beat in data["beats"]], audio_hash, beats_per_bar, first_downbeat)
