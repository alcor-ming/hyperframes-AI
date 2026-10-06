"""Optional showcase art tools. Output is a standalone directory of media and a manifest."""
from hashlib import file_digest
from importlib import import_module
import json
import math
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4


VERSION = "1.0.0"
MANIFEST = "showcase-tool.json"


def _hash(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def _safe_path(path):
    path = Path(path).absolute()
    if any(part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction())
           for part in (path, *path.parents)):
        raise ValueError("showcase tool paths must not contain symlinks")
    return path.resolve()


def _destination(output, overwrite, tool):
    output = _safe_path(output)
    if not output.exists():
        return output
    if not output.is_dir() or not overwrite:
        raise FileExistsError(f"Output already exists; choose a new directory or explicitly overwrite: {output}")
    manifest = output / MANIFEST
    try:
        if manifest.is_symlink():
            raise ValueError("manifest symlink")
        previous = json.loads(manifest.read_text(encoding="utf-8"))
        files = previous["files"]
        if previous["tool"] != tool or not isinstance(files, list) or not files:
            raise ValueError("wrong tool or empty manifest")
        names = {item["path"] for item in files}
        if (len(names) != len(files) or MANIFEST in names
                or any(not isinstance(name, str) or Path(name).name != name for name in names)
                or {item.name for item in output.iterdir()} != names | {MANIFEST}):
            raise ValueError("output contains untracked files")
        for item in files:
            path = output / item["path"]
            if path.is_symlink() or not path.is_file() or _hash(path) != item["sha256"]:
                raise ValueError("generated file was changed")
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("Overwrite requires an intact output directory from this showcase tool; choose a new directory") from exc
    return output


def _art(name):
    dependencies = {}
    for package in ("numpy", "scipy", "PIL"):
        try:
            dependencies["Pillow" if package == "PIL" else package] = import_module(package).__version__
        except ImportError as exc:
            raise ValueError(f"Showcase tools require {package if package != 'PIL' else 'Pillow'}; install the managed image-tool dependencies") from exc
    return import_module(name), dependencies


def _generate(output, *, overwrite, tool, parameters, build, art_name, source=None):
    output = _destination(output, overwrite, tool)
    if source is not None and source.is_relative_to(output):
        raise ValueError("Output directory must not contain the source image")
    art, dependencies = _art(art_name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output.name}-", dir=output.parent) as temporary:
        staging = Path(temporary) / "generated"
        staging.mkdir()
        build(art, staging)
        from PIL import Image
        files = []
        for path in sorted(staging.iterdir()):
            with Image.open(path) as image:
                image.load()
                files.append({"path": path.name, "sha256": _hash(path), "width": image.width, "height": image.height})
        if not files:
            raise ValueError("Showcase tool produced no images")
        manifest = {"schema_version": 1, "tool": tool, "tool_version": VERSION,
                    "parameters": parameters, "dependencies": dependencies,
                    "implementation": {name: _hash(Path(__file__).with_name(name))
                                       for name in ("showcase_tools.py", f"{art_name}.py")},
                    "files": files}
        if source is not None:
            manifest["input"] = {"path": str(source), "sha256": parameters.pop("input_sha256")}
            if _hash(source) != manifest["input"]["sha256"]:
                raise ValueError("Source image changed during generation; retry with an immutable input")
        (staging / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _destination(output, overwrite, tool)
        backup = output.with_name(f".{output.name}-previous-{uuid4().hex}")
        if output.exists():
            output.rename(backup)
        try:
            staging.rename(output)
        except OSError:
            if backup.exists():
                try:
                    backup.rename(output)
                except OSError as exc:
                    raise OSError(f"Could not restore previous output; preserved at {backup}") from exc
            raise
        if backup.exists():
            shutil.rmtree(backup)
    return {**manifest, "output": str(output), "manifest": str(output / MANIFEST)}


def stage(output: Path, *, overwrite=False) -> dict:
    """Generate the deterministic paper-theatre preset for a 1920×1080 stage."""
    return _generate(output, overwrite=overwrite, tool="stage", art_name="stage_art",
                     parameters={"preset": "paper-theatre", "width": 1920, "height": 1080, "ratio": "16:9"},
                     build=lambda art, directory: art.generate(directory))


def cast(input: Path, output: Path, *, kind="sheet", overwrite=False,
         target_height=640, border=9, pose_scale=1.18, seed=7) -> dict:
    """Process one white three-view sheet or one alpha pose into reusable PNG media."""
    if kind not in ("sheet", "pose"):
        raise ValueError("kind must be sheet or pose")
    if type(target_height) is not int or not 16 <= target_height <= 4096:
        raise ValueError("target_height must be an integer from 16 to 4096")
    if type(border) is not int or not 0 <= border <= 64:
        raise ValueError("border must be an integer from 0 to 64")
    if (isinstance(pose_scale, bool) or not isinstance(pose_scale, (int, float))
            or not math.isfinite(pose_scale) or not 0.05 <= pose_scale <= 8):
        raise ValueError("pose_scale must be finite and from 0.05 to 8")
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be an integer from 0 to 4294967295")
    source = _safe_path(input)
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError("Input image must be a nonempty regular file")
    parameters = {"kind": kind, "border": border, "input_sha256": _hash(source)}
    parameters.update({"target_height": target_height, "seed": seed} if kind == "sheet" else {"pose_scale": pose_scale})

    def build(art, directory):
        from PIL import Image, UnidentifiedImageError
        import numpy as np
        try:
            with Image.open(source) as image:
                if image.format not in ("PNG", "JPEG", "WEBP") or getattr(image, "n_frames", 1) != 1:
                    raise ValueError("Only static PNG, JPEG or WebP images are supported")
                if min(image.size) < 16 or image.width * image.height > 25_000_000:
                    raise ValueError("Input must be at least 16 pixels per side and at most 25 megapixels")
                image.load()
                rgba = np.asarray(image.convert("RGBA")).astype(np.float32)
        except (OSError, UnidentifiedImageError) as exc:
            raise ValueError("Input is not a readable supported image") from exc
        alpha = rgba[..., 3]
        if kind == "pose":
            if not (alpha.max() > 115 and alpha.min() == 0):
                raise ValueError("pose requires a visible figure and a transparent background")
            if max(rgba.shape[:2]) * pose_scale > 8192:
                raise ValueError("Scaled pose must not exceed 8192 pixels per side")
            art.diecut(rgba, pose_scale, border).save(directory / "pose.png", optimize=True)
            return
        if alpha.min() != 255:
            raise ValueError("sheet requires an opaque near-white background; use pose for alpha images")
        rgb = rgba[..., :3]
        for view, mask in zip(("front", "side", "back"), art.figure_masks(rgb)):
            ys, xs = np.nonzero(mask)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            if (x1 - x0) * target_height / (y1 - y0) > 8192:
                raise ValueError("Scaled sheet figure must not exceed 8192 pixels wide")
            crop = rgb[y0:y1, x0:x1]
            mask = mask[y0:y1, x0:x1]
            soft = art.ndi.gaussian_filter(art.ndi.binary_erosion(mask, structure=art.disk(1)).astype(np.float32), 0.7)
            image = art.diecut(np.dstack([crop, soft * 255]), target_height / (y1 - y0), border)
            image.save(directory / f"{view}.png", optimize=True)
            if view == "front":
                art.kraft(image, seed).save(directory / "kraft.png", optimize=True)
                art.silhouette(image).save(directory / "silhouette.png", optimize=True)
                art.gray(image).save(directory / "gray.png", optimize=True)

    return _generate(output, overwrite=overwrite, tool="cast", parameters=parameters,
                     build=build, art_name="cast_art", source=source)
