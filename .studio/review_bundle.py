"""Copy only declared, Work-local evidence into an immutable review package."""
import json
from pathlib import Path
import shutil
import tempfile

from explainer import validate_cues
from work_requests import safe, identity, digest, write, RequestError


def build(store, work, variant, review_id, manifest):
    identity(review_id)
    if not isinstance(manifest, dict) or set(manifest) != {"scenes", "screenshots", "contact_sheet"}:
        raise RequestError("Review manifest requires scenes, screenshots and contact_sheet")
    if not isinstance(manifest["scenes"], list) or not manifest["scenes"] or not all(isinstance(p, str) for p in manifest["scenes"]):
        raise RequestError("Declare Scene source paths relative to the Work")
    shots = manifest["screenshots"]
    if not isinstance(shots, list) or not shots:
        raise RequestError("Declare screenshots with exact time and Work-relative path")
    from explainer import number
    for shot in shots:
        if not isinstance(shot, dict) or set(shot) != {"time", "path"} or not isinstance(shot["path"], str):
            raise RequestError("Invalid screenshot declaration")
        try:
            number(shot["time"], "screenshot time")
        except ValueError as error:
            raise RequestError(str(error)) from error
        if Path(shot["path"]).suffix.lower() != ".png":
            raise RequestError("Review screenshots must be PNG evidence")
    plan = (variant / "ANIMATION_PLAN.md").relative_to(work).as_posix()
    cues = (variant / "project/runtime/cues.json").relative_to(work).as_posix()
    names = [plan, cues, *manifest["scenes"], *(s["path"] for s in shots), manifest["contact_sheet"]]
    if not all(isinstance(name, str) for name in names):
        raise RequestError("Review paths must be strings")
    files = {name: safe(work, name) for name in names}
    for source in files.values():
        if not source.is_file() or source.stat().st_nlink != 1:
            raise RequestError("Review evidence must be regular unlinked files")
    try:
        timing = validate_cues(json.loads(files[cues].read_text(encoding="utf-8")))
    except ValueError as error:
        raise RequestError(str(error)) from error
    if "beat_grid" not in timing:
        raise RequestError("Review requires lyric timing and a beat grid")
    hashes = {name: digest(source) for name, source in files.items()}
    target = safe(store, "review/" + review_id)
    if target.exists():
        raise RequestError("Review package already exists; choose a new ID")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".pending-review-", dir=target.parent) as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        for name, source in files.items():
            destination = safe(staging, "evidence/" + name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            if digest(destination) != hashes[name] or digest(source) != hashes[name]:
                raise RequestError("Review input changed while copying")
        write(staging / "manifest.json", {"work": work.name, "variant": variant.name, "declaration": manifest, "files": hashes})
        (staging / "REVIEW.md").write_text("# 审查\n\n证据分【图】【码】【未实现】；未验证不写成通过。\n\n"
            "| 严重度 | 证据 | 问题 | 建议 |\n|---|---|---|---|\n\n"
            "| Scene | 推荐分镜 | 证据 |\n|---|---|---|\n\n只读审查，不代替用户观看与接受。\n", encoding="utf-8")
        staging.rename(target)
    return target
