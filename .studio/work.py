#!/usr/bin/env python3
"""Local lifecycle CLI for HyperFrames AI works."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable
from types import SimpleNamespace
import unicodedata
import uuid
from urllib.parse import quote


try:
    from component_harness import (
        ComponentError,
        OPTIONAL_SNAPSHOT_ITEMS,
        install_component,
        parse_component_ref,
        validate_component_release,
        validate_snapshot_closure,
        validate_work_surface_inventory,
        verify_installation,
    )
except ModuleNotFoundError:  # Loading this file by path from repository tests.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from component_harness import (
        ComponentError,
        OPTIONAL_SNAPSHOT_ITEMS,
        install_component,
        parse_component_ref,
        validate_component_release,
        validate_snapshot_closure,
        validate_work_surface_inventory,
        verify_installation,
    )

from visual_plan import VisualPlanError, scene_projection, layout_projection, reference_projection, validate_dependencies, source_changes, serve
import work_requests
import studio_preview
import asset_store
import control_plane
import appearance
import storage
import appearance_rebind
import research_catalog
import work_migration
import work_successor

WORKFLOWS = {"hyperframes_video", "podcast_quote_image"}
TEMPLATES = {"talking_head", "pure_hyperframes"}
PROFILES = {"optical_fluidity", "kami_editorial", "monochrome_atelier"}
RATIOS = {"16:9", "4:3", "9:16", "source"}
SUBJECT_POSITIONS = {"left", "center", "right"}
WAIT_REASONS = {
    "script_approval": ("waiting_user", "Wait for SCRIPT.md approval"),
    "recording": ("waiting_asset", "Wait for the talking-head recording"),
    "plan_approval": ("waiting_user", "Wait for ANIMATION_PLAN.md approval"),
    "draft_feedback": ("waiting_user", "Wait for Draft feedback or acceptance"),
    "voiceover": ("waiting_asset", "Wait for the final voiceover"),
    "external_asset": ("waiting_asset", "Wait for an external media asset"),
    "article_selection": ("waiting_user", "Wait for one article plan selection"),
    "transcript_fallback": ("waiting_user", "Wait for the transcript fallback decision"),
    "source_metadata": ("waiting_user", "Wait for source metadata"),
}
SNAPSHOT_ITEMS = ("index.html", "compositions", "DESIGN.md", "project-config.json")
ID_PATTERN = re.compile(r"^[\w.-]+$", re.UNICODE)
NUMBERED_TITLE_PATTERN = re.compile(r"^(\d{3})-(.+)$")


class HarnessError(RuntimeError):
    pass


def repo_root() -> Path:
    override = os.environ.get("HYPERFRAMES_AI_ROOT")
    return Path(override).resolve() if override else Path(__file__).resolve().parents[1]


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def stale_naming_lock(lock: Path) -> bool:
    owner = lock / "owner.json"
    try:
        data = json.loads(owner.read_text(encoding="utf-8"))
        pid = int(data["pid"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False
    if data.get("host") != socket.gethostname() or data.get("platform") != sys.platform or pid <= 0:
        return False
    return storage.process_stopped(pid)


@contextmanager
def naming_lock(root: Path, timeout: float = 30.0, *, successor_recovery: bool = False) -> Iterable[None]:
    """Use one atomic directory lock that Windows and WSL can both observe."""
    lock = runtime_root(root) / "naming.lock.d"
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if stale_naming_lock(lock):
                (lock / "owner.json").unlink(missing_ok=True)
                try:
                    lock.rmdir()
                except FileNotFoundError:
                    pass
                continue
            if time.monotonic() >= deadline:
                owner = lock / "owner.json"
                detail = owner.read_text(encoding="utf-8").strip() if owner.is_file() else "unknown owner"
                raise HarnessError(f"Timed out waiting for naming lock {lock}: {detail}")
            time.sleep(0.1)
    try:
        write_json(
            lock / "owner.json",
            {"pid": os.getpid(), "host": socket.gethostname(), "platform": sys.platform, "acquired_at": now()},
        )
        if not successor_recovery and (runtime_root(root) / work_successor.JOURNAL).exists():
            raise HarnessError("Succession recovery pending; retry the original successor command")
        yield
    finally:
        (lock / "owner.json").unlink(missing_ok=True)
        try:
            lock.rmdir()
        except FileNotFoundError:
            pass


def write_json(path: Path, data: dict[str, Any]) -> None:
    # JSON is valid YAML 1.2 and keeps the CLI dependency-free.
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"Cannot read structured file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise HarnessError(f"Expected an object in {path}")
    return data


def read_frontmatter(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise HarnessError(f"Cannot read {path}: {exc}") from exc
    if not lines or lines[0] != "---":
        raise HarnessError(f"Missing JSON front matter in {path}")
    try:
        end = lines.index("---", 1)
        data = json.loads("\n".join(lines[1:end]))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HarnessError(f"Invalid JSON front matter in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise HarnessError(f"Expected an object in {path} front matter")
    return data


def document_body(path: Path) -> str:
    read_frontmatter(path)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    return "".join(lines[end + 1:])


def script_text(path: Path, *, anchors: bool = False) -> str:
    """Extract narration only; planning indexes never reach reading or alignment input."""
    body = document_body(path)
    start, end = "<!-- scene-index:start -->", "<!-- scene-index:end -->"
    if start in body or end in body:
        if body.count(start) != 1 or body.count(end) != 1 or body.index(start) > body.index(end):
            raise HarnessError("SCRIPT.md needs one paired scene-index:start/end block")
        before, rest = body.split(start)
        _, after = rest.split(end)
        body = before + after
    if not anchors:
        body = re.sub(r"<!--\s*P\d+\s*-->[ \t]*\n?", "", body)
    return body.strip()


def command_script_text(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args, allow_archive=True)
    require_workflow(work, "hyperframes_video")
    if not selected_variant_id(root, work, args) and (work / "shared" / "SCRIPT.md").is_file():
        print(script_text(work / "shared" / "SCRIPT.md", anchors=args.anchors))
    else:
        variant, _ = selected_variant(root, work, args)
        print(script_text(input_path(variant, "SCRIPT.md"), anchors=args.anchors))


def input_path(directory: Path, name: str) -> Path:
    return control_plane.input_path(SimpleNamespace(**globals()), directory, name)


def account_service(root: Path) -> control_plane.AccountService:
    return control_plane.AccountService(SimpleNamespace(**globals()), root)


def command_config(root: Path, args: argparse.Namespace) -> None:
    service = account_service(root)
    if args.operation == "put":
        record = service.put(args.command, args.identity, read_json(Path(args.file)))
    elif args.operation == "get":
        record = service.get(args.command, args.identity)
        if args.command == "series":
            record = {**record, "works": [row["id"] for row in list_work_rows(root)
                                         if read_frontmatter(locate_work(root, row["id"])[0] / "WORK.md").get("series") == args.identity]}
        elif args.command == "account":
            record = {**record, "variants": [
                {"work": row["id"], "series": row["series"], "series_number": row["series_number"], **variant}
                for row in list_work_rows(root) if row["workflow"] == "hyperframes_video"
                for variant in row["variants"] if variant["account"] == args.identity]}
    else:
        record = [read_json(path) for path in sorted((service.directory / args.command).glob("*.json"))]
    print(json.dumps(record, ensure_ascii=False, indent=2))


def appearance_options(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    path = getattr(args, "appearance_file", None)
    explicit = read_json(Path(path)) if path else {}
    for key in ("theme", "background", "mode", "ratio", "fps", "seed"):
        value = getattr(args, key, None)
        if value is not None:
            if key == "background" or key == "theme" and "@v" in value:
                package, _ = asset_store.resolve_component(root, value)
                report = validate_component_release(package, allow_unapproved=True)
                if report["metadata"].get("asset_type") != key:
                    raise HarnessError(f"Expected a {key} asset")
                value = {"ref": report["component_ref"], "kind": key, "package_sha256": report["package_sha256"]}
            explicit[key] = value
    return explicit


def command_appearance_resolve(root: Path, args: argparse.Namespace) -> None:
    service = account_service(root)
    account = service.get("account", args.account) if args.account else {}
    print(json.dumps(appearance.resolve(root, account, appearance_options(root, args)), ensure_ascii=False, indent=2))


def command_appearance_update(root: Path, args: argparse.Namespace) -> None:
    appearance_rebind.command(root, args, SimpleNamespace(**globals()))


def adopted_settings(root: Path, args: argparse.Namespace, work: Path | None = None) -> dict[str, Any]:
    service = account_service(root)
    purpose = read_frontmatter(work / "WORK.md").get("purpose", "standard") if work else args.purpose or "standard"
    account = service.get("account", args.account) if args.account else {}
    if (getattr(args, "workflow", None) == "hyperframes_video" or work and work_workflow(work) == "hyperframes_video") and purpose != "test" and not account:
        raise HarnessError("Production Variant requires --account; configure AccountService first")
    if purpose == "test" and account:
        raise HarnessError("test Work binds batches, not accounts")
    if purpose != "test" and args.batch:
        raise HarnessError("Only test Work accepts a batch")
    if work and purpose == "test":
        batch = args.batch or args.variant_id
        if any(read_json(path / "variant.yaml").get("batch") == batch for path in variant_paths(work)):
            raise HarnessError("A batch already has a Variant; revise that Variant")
    explicit = appearance_options(root, args)
    if appearance.is_asset_appearance({**account, **explicit}):
        lock = appearance.resolve(root, account, explicit)
        return {"theme": lock["selection"]["theme"], "background": lock["selection"]["background"],
                "motion": lock["selection"]["motion"], "mode": lock["mode"], "ratio": lock["ratio"],
                "appearance_lock": lock, "account": args.account, "account_revision": account.get("revision"),
                "account_settings": account, "batch": args.batch, "revision": 1}
    if set(explicit) - {"theme", "mode", "ratio"}:
        raise HarnessError("Appearance parameters require exact Theme and Background assets")
    settings = {key: explicit.get(key, account.get(key)) for key in ("theme", "mode", "ratio")}
    settings["mode"] = settings["mode"] or "text-led"
    if settings["theme"]:
        settings["ratio"] = settings["ratio"] or "16:9"
        settings["mode"] = settings["mode"] or "text-led"
    theme = service.appearance(settings)
    return {**settings, "account": args.account, "account_revision": account.get("revision"),
            "account_settings": account, "theme_revision": theme.get("revision"), "theme_settings": theme,
            "batch": args.batch, "revision": 1}


def adopt_variant(path: Path, settings: dict[str, Any], *, shared: bool = False, branch: str | None = None) -> None:
    state = read_json(path / "variant.yaml")
    state.update({key: value for key, value in settings.items() if value is not None})
    if settings.get("theme"):
        state["profile"] = None
        plan = path / "ANIMATION_PLAN.md"
        metadata = read_frontmatter(plan)
        metadata.update(theme=settings["theme"], mode=settings["mode"], ratio=settings["ratio"], profile=None)
        atomic_write(plan, "---\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n" + document_body(plan))
    work = path.parent.parent
    if shared:
        refs = {}
        for name in ("SCRIPT.md", "RESEARCH.md"):
            target = work / "shared" / name
            if not target.exists():
                target.parent.mkdir(exist_ok=True)
                shutil.copy2(path / name, target)
            refs[name] = target.relative_to(work).as_posix()
            (path / name).unlink(missing_ok=True)
        state["shared_inputs"] = refs
    if branch:
        state["content_branch"] = {"source_variant": branch, "input_sha256": {
            name: file_sha256(path / name) for name in ("SCRIPT.md", "RESEARCH.md")}}
    write_variant(path, state)


def create_adopted_variant(root: Path, work: Path, variant_id: str, settings: dict[str, Any], *,
                           shared: bool = False, branch: str | None = None, **options: Any) -> Path:
    destination = work / "variants" / validate_id(variant_id, "variant id")
    if destination.exists():
        raise HarnessError(f"Variant already exists: {variant_id}")
    staging_id = f".pending-{uuid.uuid4().hex}"
    staging = work / "variants" / staging_id
    try:
        if "appearance_lock" in settings and options.get("ratio") not in RATIOS:
            options["ratio"] = "source"
        create_variant(root, work, staging_id, **options)
        if "appearance_lock" in settings:
            appearance.materialize(root, staging / "project", settings["appearance_lock"])
        adopt_variant(staging, {**settings, "id": variant_id}, shared=shared, branch=branch)
        staging.rename(destination)
    except Exception:
        if staging.is_dir():
            shutil.rmtree(staging)
        raise
    return destination


def animation_plan_contains_component_ref(path: Path, component_ref: str) -> bool:
    """Check the approved Plan body for the exact requested Component ref."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        end = lines.index("---", 1)
    except (OSError, ValueError) as exc:
        raise HarnessError(f"Cannot read Animation Plan body {path}: {exc}") from exc
    pattern = re.compile(rf"(?<![A-Za-z0-9_.-]){re.escape(component_ref)}(?![A-Za-z0-9_.-])")
    return any(pattern.search(line) for line in lines[end + 1 :])


def work_workflow(work: Path) -> str:
    value = read_frontmatter(work / "WORK.md").get("workflow", "hyperframes_video")
    if value not in WORKFLOWS:
        raise HarnessError(f"Unknown workflow: {value}")
    return str(value)


def require_workflow(work: Path, expected: str) -> None:
    actual = work_workflow(work)
    if actual != expected:
        raise HarnessError(f"Command requires workflow {expected}; current Work uses {actual}")


def template_text(root: Path, name: str, values: dict[str, str]) -> str:
    path = root / ".studio" / "templates" / name
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HarnessError(f"Cannot read template {path}: {exc}") from exc
    for token, value in values.items():
        text = text.replace(f"__{token}__", value)
    if re.search(r"__[A-Z_]+__", text):
        raise HarnessError(f"Unresolved placeholder in {path}")
    return text


def json_string_content(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)[1:-1]


def validate_id(value: str, label: str) -> str:
    if not value or value in {".", ".."} or not ID_PATTERN.fullmatch(value):
        raise HarnessError(f"Invalid {label}: {value!r}")
    return value


def title_number(title: str) -> int | None:
    match = NUMBERED_TITLE_PATTERN.match(title)
    return int(match.group(1)) if match else None


def work_id_number(work_id: str, workflow: str) -> int | None:
    suffix = r"(?:-[\w.-]+)?" if workflow == "hyperframes_video" else ""
    match = re.fullmatch(rf"work-{re.escape(workflow)}-(\d{{3,}}){suffix}", work_id)
    return int(match.group(1)) if match else None


def semantic_title(value: str, *, video: bool = False) -> str:
    title = unicodedata.normalize("NFKC", value).strip()
    return title if video else NUMBERED_TITLE_PATTERN.sub(r"\2", title).strip(" -")


def work_slug(title: str) -> str:
    slug = re.sub(r"[^\w.-]+", "-", title, flags=re.UNICODE).strip(".-_")[:40].rstrip(".-_")
    return slug or "untitled"


def identity_path(root: Path) -> Path:
    return runtime_root(root) / "work-identity.json"


def identity_state(root: Path) -> dict[str, Any]:
    path = identity_path(root)
    state = read_json(path) if path.is_file() else {}
    if not isinstance(state, dict):
        raise HarnessError(f"Invalid Work identity state: {path}")
    for key in ("series_highwater", "aliases", "series_aliases", "successions"):
        if not isinstance(state.get(key, {}), dict):
            raise HarnessError(f"Invalid Work identity {key}: {path}")
    if not isinstance(state.get("video_highwater", 0), int) or state.get("video_highwater", 0) < 0:
        raise HarnessError(f"Invalid video highwater: {path}")
    if any(not isinstance(value, int) or value < 0 for value in state.get("series_highwater", {}).values()):
        raise HarnessError(f"Invalid series highwater: {path}")
    return {"video_highwater": state.get("video_highwater", 0),
            "series_highwater": state.get("series_highwater", {}),
            "aliases": state.get("aliases", {}),
            "series_aliases": state.get("series_aliases", {}),
            "successions": state.get("successions", {})}


def write_identity(root: Path, state: dict[str, Any]) -> None:
    write_json(identity_path(root), state)


def video_number(root: Path, rows: list[dict[str, Any]], state: dict[str, Any]) -> int:
    observed = [work_id_number(row["id"], "hyperframes_video") or 0 for row in rows
                if row["workflow"] == "hyperframes_video"]
    return max(int(state["video_highwater"]), *observed, 0) + 1


def series_number(root: Path, rows: list[dict[str, Any]], state: dict[str, Any], series: str) -> int:
    observed = [int(row.get("series_number") or 0) for row in rows if row.get("series") == series]
    return max(int(state["series_highwater"].get(series, 0)), *observed, 0) + 1


def next_work_number(rows: Iterable[dict[str, Any]], workflow: str) -> int:
    numbers: list[int] = []
    for row in rows:
        if row["workflow"] != workflow:
            continue
        number = work_id_number(row["id"], workflow)
        if number is None:
            number = title_number(row["title"])
        if number is not None:
            numbers.append(number)
    return max(numbers, default=0) + 1


def work_root_config_path(root: Path) -> Path:
    return root / ".studio" / ".runtime" / "work-root"


def configured_work_root(root: Path) -> Path | None:
    path = work_root_config_path(root)
    if os.environ.get("HYPERFRAMES_AI_WORK_ROOT"):
        value = os.environ["HYPERFRAMES_AI_WORK_ROOT"]
    elif os.environ.get("HYPERFRAMES_AI_CONFIG"):
        path = Path(os.environ["HYPERFRAMES_AI_CONFIG"])
        value = read_json(path).get("work_root", "")
    else:
        if not path.is_file():
            return None
        value = path.read_text(encoding="utf-8").strip()
    candidate = Path(value).expanduser() if value else None
    if candidate is None or not candidate.is_absolute():
        raise HarnessError(f"Invalid WorkStore root in {path}: {value!r}")
    resolved = candidate.resolve()
    if not resolved.is_dir():
        raise HarnessError(f"Configured WorkStore root is unavailable: {resolved}")
    return resolved


def works_root(root: Path) -> Path:
    return (configured_work_root(root) or root) / "works"


def runtime_root(root: Path) -> Path:
    configured = configured_work_root(root)
    return configured / ".runtime" if configured else root / ".studio" / ".runtime"


def ensure_roots(root: Path) -> None:
    for name in ("active", "parked", "archive"):
        (works_root(root) / name).mkdir(parents=True, exist_ok=True)
    runtime_root(root).mkdir(parents=True, exist_ok=True)


def pointer_path(root: Path, name: str) -> Path:
    return runtime_root(root) / name


def read_pointer(root: Path, name: str) -> str | None:
    path = pointer_path(root, name)
    if not path.is_file():
        return None
    value = path.read_text(encoding="utf-8").strip()
    return validate_id(value, name) if value else None


def write_pointer(root: Path, name: str, value: str) -> None:
    atomic_write(pointer_path(root, name), validate_id(value, name) + "\n")


def clear_pointer(root: Path, name: str) -> None:
    pointer_path(root, name).unlink(missing_ok=True)


def archived_work_paths(root: Path) -> Iterable[Path]:
    archive = works_root(root) / "archive"
    if not archive.is_dir():
        return []
    paths: list[Path] = []
    for month in sorted(archive.iterdir(), reverse=True):
        if month.is_dir():
            paths.extend(path for path in sorted(month.iterdir()) if path.is_dir() and (path / "WORK.md").is_file())
    return paths


def locate_work(root: Path, work_id: str) -> tuple[Path, str]:
    validate_id(work_id, "work id")
    work_id = identity_state(root)["aliases"].get(work_id, work_id)
    validate_id(work_id, "work id")
    for location in ("active", "parked"):
        candidate = works_root(root) / location / work_id
        if candidate.is_dir():
            return candidate, "archive" if (candidate / ".runtime" / "archive.json").is_file() else location
    for candidate in archived_work_paths(root):
        if candidate.name == work_id:
            return candidate, "archive"
    raise HarnessError(f"Unknown work: {work_id}")


def list_work_rows(root: Path, *, validate_identity: bool = True) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    def row_for(path: Path, location: str) -> dict[str, Any]:
        metadata = read_frontmatter(path / "WORK.md")
        variants = []
        for variant in variant_paths(path):
            state = read_json(variant / "variant.yaml")
            variants.append({"id": variant.name, "name": state.get("name") or variant.name,
                             "account": state.get("account"), "account_revision": state.get("account_revision"),
                             "status": state.get("status"), "wait_for": state.get("wait_for"),
                             "next_action": state.get("next_action")})
        only = variants[0] if len(variants) == 1 else {}
        return {"id": path.name, "title": str(metadata.get("title", "")),
                "created_at": str(metadata.get("created_at", "")),
                "workflow": str(metadata.get("workflow", "hyperframes_video")),
                "purpose": metadata.get("purpose", "standard"), "series": metadata.get("series"),
                "series_number": metadata.get("series_number"), "location": location,
                "status": only.get("status"), "wait_for": only.get("wait_for"),
                "next_action": only.get("next_action"), "variants": variants}
    for location in ("active", "parked"):
        parent = works_root(root) / location
        if parent.is_dir():
            for path in sorted(parent.iterdir()):
                if path.is_dir() and not path.name.startswith(".pending-"):
                    rows.append(row_for(path, "archive" if (path / ".runtime" / "archive.json").is_file() else location))
    for path in archived_work_paths(root):
        rows.append(row_for(path, "archive"))
    if validate_identity:
        work_successor.validate(rows, identity_state(root), SimpleNamespace(**globals()))
    location_order = {"active": 0, "parked": 1, "archive": 2}
    rows.sort(
        key=lambda row: (
            location_order[row["location"]],
            row["workflow"],
            row.get("series") or "",
            row.get("series_number") or title_number(row["title"]) or 0,
            row["created_at"],
            row["id"],
        )
    )
    return rows


def selected_work(root: Path, args: argparse.Namespace, *, allow_archive: bool = False) -> tuple[Path, str]:
    work_id = args.work_override or read_pointer(root, "current-work")
    if not work_id:
        available = ", ".join(row["id"] for row in list_work_rows(root)) or "none"
        raise HarnessError(f"No current work. Available: {available}")
    path, location = locate_work(root, work_id)
    if location == "archive" and not allow_archive:
        raise HarnessError(f"Work is archived; run 'work reopen {work_id}' first")
    return path, location


def variant_paths(work: Path) -> list[Path]:
    variants = work / "variants"
    if not variants.is_dir():
        return []
    return [path for path in sorted(variants.iterdir()) if path.is_dir() and not path.name.startswith(".pending-")]


def selected_variant_id(root: Path, work: Path, args: argparse.Namespace) -> str | None:
    variant_id = args.variant_override
    if variant_id and not (work / "variants" / validate_id(variant_id, "variant id")).is_dir():
        raise HarnessError(f"Unknown variant: {variant_id}")
    if work_workflow(work) == "podcast_quote_image":
        if not variant_id and not args.work_override:
            variant_id = read_pointer(root, "current-variant")
        if not variant_id or not (work / "variants" / variant_id).is_dir():
            variant_id = "main" if (work / "variants" / "main").is_dir() else None
        return variant_id
    if not variant_id and read_pointer(root, "current-work") == work.name:
        variant_id = read_pointer(root, "current-variant")
    if not variant_id or not (work / "variants" / variant_id).is_dir():
        candidates = variant_paths(work)
        variant_id = candidates[0].name if len(candidates) == 1 else None
    return variant_id


def selected_variant(root: Path, work: Path, args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    variant_id = selected_variant_id(root, work, args)
    if not variant_id:
        available = ", ".join(path.name for path in variant_paths(work)) or "none"
        raise HarnessError(f"No current variant. Select --variant. Available: {available}")
    validate_id(variant_id, "variant id")
    path = work / "variants" / variant_id
    if not path.is_dir():
        raise HarnessError(f"Unknown variant: {variant_id}")
    if appearance_rebind.journal_path(path).exists() and getattr(args, "appearance_command", None) != "recover":
        raise HarnessError("Appearance recovery pending; run appearance recover with this exact --work and --variant")
    return path, read_json(path / "variant.yaml")


def focus_work(root: Path, work: Path, args: argparse.Namespace) -> None:
    if work_workflow(work) == "podcast_quote_image":
        variants = variant_paths(work)
        variant_id = "main" if (work / "variants" / "main").is_dir() else (variants[0].name if variants else None)
    else:
        variant_id = selected_variant_id(root, work, args)
    write_pointer(root, "current-work", work.name)
    if variant_id:
        write_pointer(root, "current-variant", variant_id)
    else:
        clear_pointer(root, "current-variant")


def write_variant(path: Path, data: dict[str, Any]) -> None:
    write_json(path / "variant.yaml", data)


def create_video_variant(
    root: Path,
    work: Path,
    variant_id: str,
    *,
    template: str,
    profile: str | None,
    ratio: str,
    subject_position: str | None,
    copy_script_from: Path | None = None,
) -> Path:
    validate_id(variant_id, "variant id")
    if template not in TEMPLATES:
        raise HarnessError(f"Unknown template: {template}")
    if profile is not None and profile not in PROFILES:
        raise HarnessError(f"Unknown profile: {profile}")
    if ratio not in RATIOS:
        raise HarnessError(f"Unknown ratio: {ratio}")
    if subject_position is not None and subject_position not in SUBJECT_POSITIONS:
        raise HarnessError(f"Unknown subject position: {subject_position}")

    path = work / "variants" / variant_id
    if path.exists():
        raise HarnessError(f"Variant already exists: {variant_id}")
    path.mkdir(parents=True)
    for directory in (
        "media",
        "project",
        "previews",
        "final/history",
        ".history",
        ".runtime/qa",
    ):
        (path / directory).mkdir(parents=True, exist_ok=True)

    source_research = copy_script_from.parent / "RESEARCH.md" if copy_script_from else None
    script_revision = read_frontmatter(copy_script_from).get("revision", 1) if copy_script_from else 1
    research_revision = read_frontmatter(source_research).get("revision", 1) if source_research and source_research.is_file() else 1
    values = {
        "VARIANT_ID": json_string_content(variant_id),
        "TEMPLATE": json_string_content(template),
        "PROFILE": json_string_content(profile or ""),
        "RATIO": json_string_content(ratio),
        "SUBJECT_POSITION": json.dumps(subject_position),
        "SCRIPT_REVISION": json.dumps(script_revision),
        "RESEARCH_REVISION": json.dumps(research_revision),
    }
    atomic_write(path / "variant.yaml", template_text(root, "VARIANT.template.yaml", values))
    if copy_script_from:
        shutil.copy2(copy_script_from, path / "SCRIPT.md")
    else:
        atomic_write(path / "SCRIPT.md", template_text(root, "SCRIPT.template.md", {}))
    if source_research and source_research.is_file():
        shutil.copy2(source_research, path / "RESEARCH.md")
    else:
        atomic_write(path / "RESEARCH.md", template_text(root, "RESEARCH.template.md", values))
    atomic_write(path / "PACKAGE.md", "# Package\n\n## 标题\n\n## 封面文字\n\n## 一句话\n\n## 内容概括\n\n")
    atomic_write(
        path / "ANIMATION_PLAN.md",
        template_text(root, "ANIMATION_PLAN.template.md", values),
    )
    return path


def create_podcast_quote_variant(root: Path, work: Path, variant_id: str) -> Path:
    validate_id(variant_id, "variant id")
    path = work / "variants" / variant_id
    if path.exists():
        raise HarnessError(f"Variant already exists: {variant_id}")
    path.mkdir(parents=True)
    for directory in ("materials", "artifacts", "frames", "render", "final/history", ".runtime/qa"):
        (path / directory).mkdir(parents=True, exist_ok=True)
    values = {"VARIANT_ID": json_string_content(variant_id)}
    atomic_write(path / "variant.yaml", template_text(root, "PODCAST_QUOTE_VARIANT.template.yaml", values))
    atomic_write(path / "RESEARCH.md", template_text(root, "PODCAST_QUOTE_RESEARCH.template.md", {}))
    atomic_write(path / "PACKAGE.md", template_text(root, "PODCAST_QUOTE_PACKAGE.template.md", {}))
    return path


def create_variant(
    root: Path,
    work: Path,
    variant_id: str,
    *,
    workflow: str,
    template: str | None = None,
    profile: str | None = None,
    ratio: str | None = None,
    subject_position: str | None = None,
    copy_script_from: Path | None = None,
) -> Path:
    if workflow == "podcast_quote_image":
        if any(value is not None for value in (template, profile, ratio, subject_position, copy_script_from)):
            raise HarnessError("podcast_quote_image does not accept video Template, Profile, Ratio, subject, or --from options")
        return create_podcast_quote_variant(root, work, variant_id)
    if workflow != "hyperframes_video":
        raise HarnessError(f"Unknown workflow: {workflow}")
    return create_video_variant(
        root,
        work,
        variant_id,
        template=template or "pure_hyperframes",
        profile=profile,
        ratio=ratio or "16:9",
        subject_position=subject_position,
        copy_script_from=copy_script_from,
    )


def command_new(root: Path, args: argparse.Namespace) -> None:
    if os.environ.get("HYPERFRAMES_AI_REVIEW") == "1":
        args.purpose = "test"
    if args.workflow == "hyperframes_video" and not args.purpose:
        raise HarnessError("Video Work requires --purpose standard, ip, or test")
    series = "test" if args.purpose == "test" else args.series
    if args.purpose == "test" and args.series not in (None, "test"):
        raise HarnessError("test Work must use the test series")
    if series and series != "test":
        account_service(root).get("series", series)
    if args.workflow == "hyperframes_video" and args.purpose != "test" and not series:
        raise HarnessError("Production video Work requires --series")
    if args.workflow == "podcast_quote_image" and any(
        value is not None for value in (args.template, args.profile, args.ratio, args.subject_position)
    ):
        raise HarnessError("podcast_quote_image does not accept video Template, Profile, Ratio, or subject options")
    ensure_roots(root)
    with naming_lock(root):
        create_initial_variant = (args.workflow != "hyperframes_video" or args.purpose == "test"
                                  or args.account is not None or getattr(args, "variant_id", None) is not None)
        if not create_initial_variant and any(getattr(args, key, None) is not None for key in (
            "batch", "theme", "background", "appearance_file", "fps", "seed", "mode", "template", "profile", "ratio", "subject_position"
        )):
            raise HarnessError("Variant settings require --account; omit them to prepare shared Work content")
        settings = adopted_settings(root, args) if create_initial_variant else {}
        variant_id = validate_id(getattr(args, "variant_id", None) or "main", "variant id")
        if args.workflow == "podcast_quote_image" and getattr(args, "variant_id", None):
            raise HarnessError("podcast_quote_image does not accept --variant-id")
        rows = list_work_rows(root)
        identity = identity_state(root)
        existing_ids = {row["id"] for row in rows}
        number = video_number(root, rows, identity) if args.workflow == "hyperframes_video" else next_work_number(rows, args.workflow)
        title_text = semantic_title(args.title, video=args.workflow == "hyperframes_video")
        if args.workflow == "hyperframes_video" and (not title_text or any(char in title_text for char in "\r\n")):
            raise HarnessError("Work title must be non-empty on one line")
        if args.workflow == "podcast_quote_image":
            title_text = title_text or "untitled"
        if args.workflow == "hyperframes_video" and args.purpose == "test" and not args.separate:
            existing = [row["id"] for row in rows if row["workflow"] == "hyperframes_video"
                        and row["purpose"] == "test" and row["title"] == title_text]
            if existing:
                raise HarnessError("Experiment already exists: " + ", ".join(existing) + "; use --separate for a new comparison")
        assigned_series_number = (series_number(root, rows, identity, series)
                                  if args.workflow == "hyperframes_video" and args.purpose != "test" else None)
        while True:
            if args.workflow == "podcast_quote_image" and number > 999:
                raise HarnessError("Work name sequence is exhausted")
            work_id = f"work-{args.workflow}-{number:03d}"
            if args.workflow == "hyperframes_video":
                work_id += f"-{work_slug(title_text)}"
            if work_id not in existing_ids:
                work = works_root(root) / "active" / work_id
                try:
                    staging = work.with_name(f".pending-{uuid.uuid4().hex}")
                    staging.mkdir()
                    break
                except FileExistsError:
                    pass
            number += 1

        try:
            title = title_text if args.workflow == "hyperframes_video" else f"{number:03d}-{title_text}"
            atomic_write(staging / "WORK.md", template_text(root, "WORK.template.md", {
                "WORK_ID": json_string_content(work_id), "TITLE": json_string_content(title),
                "CREATED_AT": now(), "WORKFLOW": json_string_content(args.workflow),
                "REQUIRED_VARIANTS": json.dumps(["main"] if args.workflow == "podcast_quote_image" else []),
            }))
            atomic_write(staging / "source.md", "# Source\n\n")
            (staging / "materials").mkdir()
            options = dict(workflow=args.workflow, template=args.template, profile=args.profile,
                           ratio=settings.get("ratio"), subject_position=args.subject_position)
            if args.workflow == "hyperframes_video":
                metadata = read_frontmatter(staging / "WORK.md")
                metadata.update(purpose=args.purpose, series=series, series_number=assigned_series_number, shared_source=True,
                                source_work=args.source_work, source_variant=args.source_variant, source_version=args.source_version)
                atomic_write(staging / "WORK.md", "---\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n" + document_body(staging / "WORK.md"))
                (staging / "shared").mkdir()
                (staging / "variants").mkdir()
                atomic_write(staging / "shared" / "SCRIPT.md", template_text(root, "SCRIPT.template.md", {}))
                atomic_write(staging / "shared" / "RESEARCH.md", template_text(root, "RESEARCH.template.md", {"SCRIPT_REVISION": "1"}))
                if args.purpose == "test":
                    settings["batch"] = args.batch or variant_id
                if create_initial_variant:
                    create_adopted_variant(root, staging, variant_id, settings, shared=True, **options)
            else:
                create_variant(root, staging, "main", **options)
            if args.workflow == "hyperframes_video":
                identity["video_highwater"] = number
                if assigned_series_number is not None:
                    identity["series_highwater"][series] = assigned_series_number
                write_identity(root, identity)
            staging.rename(work)
        except Exception:
            if staging.is_dir():
                shutil.rmtree(staging)
            raise
        if not args.detached:
            write_pointer(root, "current-work", work_id)
            if create_initial_variant:
                write_pointer(root, "current-variant", variant_id)
            else:
                clear_pointer(root, "current-variant")
    print(work_id)


def command_current(root: Path, args: argparse.Namespace) -> None:
    work_id = read_pointer(root, "current-work")
    variant_id = read_pointer(root, "current-variant")
    if not work_id:
        raise HarnessError("No current work")
    work, location = locate_work(root, work_id)
    print(json.dumps({"work": work_id, "variant": variant_id, "location": location, "path": str(work)}, ensure_ascii=False))


def command_list(root: Path, args: argparse.Namespace) -> None:
    ensure_roots(root)
    rows = list_work_rows(root)
    if args.tree:
        print("\n".join(tree_lines(root, rows)))
    else:
        print(json.dumps(rows, ensure_ascii=False, indent=2))


def display_name(root: Path, row: dict[str, Any]) -> str:
    if row["workflow"] != "hyperframes_video" or row["purpose"] == "test":
        return row["title"]
    if not row["series"] or not row["series_number"]:
        return row["title"]
    try:
        series_name = account_service(root).get("series", row["series"])["name"]
    except HarnessError:
        series_name = row["series"]
    return f"{series_name} {row['series_number']:03d} · {row['title']}"


def experiment_suffix(row: dict[str, Any]) -> str:
    number = work_id_number(row["id"], "hyperframes_video")
    return f"{number:03d}" if number is not None else row["id"][-6:]


def variant_account_label(row: dict[str, Any], variant: dict[str, Any]) -> str:
    if row["workflow"] != "hyperframes_video":
        return variant["account"] or "版本"
    if row["purpose"] == "test":
        return "实验"
    if not variant["account"]:
        return "历史未绑定"
    revision = variant["account_revision"]
    return f"{variant['account']} · r{revision}" if revision is not None else f"{variant['account']} · 历史版本未知"


def tree_lines(root: Path, rows: list[dict[str, Any]]) -> list[str]:
    lines = []
    experiment_names = [row["title"] for row in rows if row["purpose"] == "test"]
    groups = (
        ("生产系列", lambda row: row["workflow"] == "hyperframes_video" and row["purpose"] != "test" and row["location"] != "archive"),
        ("临时实验", lambda row: row["workflow"] == "hyperframes_video" and row["purpose"] == "test" and row["location"] != "archive"),
        ("历史归档", lambda row: row["workflow"] == "hyperframes_video" and row["location"] == "archive"),
        ("播客作品", lambda row: row["workflow"] == "podcast_quote_image"),
    )
    for heading, include in groups:
        members = [row for row in rows if include(row)]
        if not members:
            continue
        lines.append(heading)
        if heading in {"生产系列", "历史归档"}:
            members.sort(key=lambda row: (row["series"] or "", row["series_number"] or 0, row["id"]))
        previous_series = None
        for row in members:
            grouped = heading in {"生产系列", "历史归档"}
            if grouped and row["series"] != previous_series:
                try:
                    series_label = account_service(root).get("series", row["series"])["name"]
                except HarnessError:
                    series_label = row["series"] or "未登记系列"
                lines.append(f"  {series_label}")
                previous_series = row["series"]
            indent = "    " if grouped else "  "
            label = f"{row['series_number']:03d} · {row['title']}" if row["series_number"] else row["title"]
            if row["purpose"] == "test" and experiment_names.count(row["title"]) > 1:
                label += f" · {experiment_suffix(row)}"
            if row["location"] == "parked":
                label += " (停放)"
            lines.append(f"{indent}{label} [{row['id']}]")
            for variant in row["variants"]:
                lines.append(f"{indent}  {variant_account_label(row, variant)} · {variant['name']} "
                             f"[{variant['id']}] {variant['status'] or 'unknown'}")
    return lines


def refresh_browser(root: Path) -> None:
    store = works_root(root).parent
    lines = ["# 浏览目录", ""]
    rows = list_work_rows(root)
    if not any(row["workflow"] == "hyperframes_video" for row in rows) and not (store / "浏览目录.md").exists():
        return
    experiment_names = [row["title"] for row in rows if row["purpose"] == "test"]
    for row in rows:
        if row["workflow"] != "hyperframes_video":
            continue
        path, _ = locate_work(root, row["id"])
        label = display_name(root, row)
        if row["purpose"] == "test" and experiment_names.count(row["title"]) > 1:
            label += f" · {experiment_suffix(row)}"
        label = label.replace("]", "\\]")
        section = "历史归档" if row["location"] == "archive" else "临时实验" if row["purpose"] == "test" else "生产系列"
        link = quote(path.relative_to(store).as_posix(), safe="/")
        lines.append(f"- {section} / [{label}]({link})")
        for variant in row["variants"]:
            lines.append(f"  - {variant_account_label(row, variant)} · {variant['name']} · {variant['status'] or 'unknown'}")
    atomic_write(store / "浏览目录.md", "\n".join(lines) + "\n")


def command_browser_rebuild(root: Path, args: argparse.Namespace) -> None:
    refresh_browser(root)
    print(str(works_root(root).parent / "浏览目录.md"))


def command_migrate(root: Path, args: argparse.Namespace) -> None:
    api = sys.modules.get(__name__) or SimpleNamespace(**globals())
    if args.migrate_command == "dry-run":
        def overrides(path: str | None) -> dict[str, str]:
            if not path:
                return {}
            value = read_json(Path(path))
            if not isinstance(value, dict) or not all(isinstance(key, str) and isinstance(item, str)
                                                      for key, item in value.items()):
                raise HarnessError(f"Migration overrides must be a JSON string map: {path}")
            return value

        plan = work_migration.build_plan(root, api,
                                         title_overrides=overrides(args.title_overrides),
                                         purpose_overrides=overrides(args.purpose_overrides),
                                         only_ids=args.only or None)
        content = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output = Path(args.output).expanduser()
            if output.is_symlink() or output.resolve().is_relative_to(works_root(root).parent.resolve()):
                raise HarnessError("Migration mapping output must be a new file outside WorkStore")
            try:
                with output.open("x", encoding="utf-8") as handle:
                    handle.write(content)
            except OSError as exc:
                raise HarnessError(f"Cannot create migration mapping {output}: {exc}") from exc
        else:
            print(content, end="")
    else:
        plan = read_json(Path(args.mapping))
        result = work_migration.apply_plan(root, plan, api)
        args.migration_applied = result["applied"]
        print(json.dumps(result, ensure_ascii=False))


def command_find(root: Path, args: argparse.Namespace) -> None:
    rows, identity = list_work_rows(root), identity_state(root)
    key = work_successor.series_key(args.series, args.number)
    row = work_successor.current(rows, identity, key, SimpleNamespace(**globals()))
    chain = identity["successions"].get(key)
    if getattr(args, "history", False):
        ids = chain["chain"] if chain else [row["id"]] if row else []
        if not ids:
            raise HarnessError("No Work for this series number")
        by_id = {item["id"]: item for item in rows}
        print(json.dumps([{"work": work_id, "location": by_id.get(work_id, {}).get("location", "missing"),
                           "current": bool(row and row["id"] == work_id),
                           "successor": ids[index + 1] if index + 1 < len(ids) else None,
                           "request": chain["requests"].get(work_id) if chain else None}
                          for index, work_id in enumerate(ids)], ensure_ascii=False, indent=2))
        return
    if row is None:
        raise HarnessError("No current Work for this series number; historical number remains occupied")
    matches = [row]
    moved_from = ({"series": args.series, "series_number": args.number}
                  if row["series"] != args.series or row["series_number"] != args.number else None)
    result = []
    for row in matches:
        variants = [variant for variant in row["variants"] if not args.account or variant["account"] == args.account]
        result.extend({"work": row["id"], "series": row["series"], "series_number": row["series_number"],
                       "location": row["location"], "moved_from": moved_from, "variant": variant} for variant in variants)
        if not row["variants"] and not args.account:
            result.append({"work": row["id"], "series": row["series"], "series_number": row["series_number"],
                           "location": row["location"], "moved_from": moved_from, "variant": None})
    if not result:
        raise HarnessError("No Variant for this account and series number")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_successor(root: Path, args: argparse.Namespace) -> None:
    work_successor.command(root, args, SimpleNamespace(**globals()))


def command_series_move(root: Path, args: argparse.Namespace) -> None:
    account_service(root).get("series", args.identity)
    with naming_lock(root):
        work, _ = selected_work(root, args, allow_archive=True)
        if any(work.name in record["chain"][:-1] for record in identity_state(root)["successions"].values()):
            raise HarnessError("Succession predecessor must remain archived and read-only")
        metadata_path = work / "WORK.md"
        metadata = read_frontmatter(metadata_path)
        if metadata.get("workflow") != "hyperframes_video" or metadata.get("purpose", "standard") == "test":
            raise HarnessError("Only production video Works can move between series")
        old_series, old_number = metadata.get("series"), metadata.get("series_number")
        if old_series == args.identity:
            print(json.dumps({"work": work.name, "series": old_series, "series_number": old_number}))
            return
        rows, identity = list_work_rows(root), identity_state(root)
        new_number = series_number(root, rows, identity, args.identity)
        if old_series and old_number:
            key = f"{old_series}:{old_number}"
            if key in identity["series_aliases"] and identity["series_aliases"][key] != work.name:
                raise HarnessError("Historical series number already points to another Work")
            identity["series_aliases"][key] = work.name
        metadata.update(series=args.identity, series_number=new_number)
        identity["series_highwater"][args.identity] = new_number
        write_identity(root, identity)
        atomic_write(metadata_path, "---\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n" + document_body(metadata_path))
    print(json.dumps({"work": work.name, "series": args.identity, "series_number": new_number}))


def command_variant_name(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    name = checked_variant_name(args.name)
    state["name"] = name
    write_variant(variant, state)
    print(name)


def checked_variant_name(value: str) -> str:
    name = unicodedata.normalize("NFKC", value).strip()
    if not name or any(char in name for char in "\r\n") or len(name) > 40:
        raise HarnessError("Variant name must contain 1-40 characters on one line")
    return name


def command_root_show(root: Path, args: argparse.Namespace) -> None:
    configured = configured_work_root(root)
    active = configured or root
    print(
        json.dumps(
            {
                "configured": configured is not None,
                "work_root": str(active),
                "works": str(active / "works"),
                "runtime": str(runtime_root(root)),
            },
            ensure_ascii=False,
        )
    )


def command_root_set(root: Path, args: argparse.Namespace) -> None:
    default_config = os.environ.get("HYPERFRAMES_AI_DEFAULT_CONFIG")
    if os.environ.get("HYPERFRAMES_AI_REVIEW") == "1":
        raise HarnessError("Review cannot change production defaults")
    if os.environ.get("HYPERFRAMES_AI_WORK_ROOT") and not default_config:
        raise HarnessError("An explicit environment WorkRoot cannot change persistent configuration")
    target = Path(args.path).expanduser()
    if not target.is_absolute() or target.is_symlink():
        raise HarnessError("WorkStore root must be an existing absolute directory, not a symlink")
    target = target.resolve()
    required = [target / "works" / name for name in ("active", "parked", "archive")]
    missing = [str(path) for path in required if not path.is_dir()]
    if missing:
        raise HarnessError("WorkStore root is missing required directories: " + ", ".join(missing))
    try:
        (target / ".runtime").mkdir(exist_ok=True)
    except OSError as exc:
        raise HarnessError(f"WorkStore runtime directory is unavailable: {exc}") from exc
    if default_config or os.environ.get("HYPERFRAMES_AI_CONFIG"):
        config_path = Path(default_config or os.environ["HYPERFRAMES_AI_CONFIG"])
        config = read_json(config_path) if config_path.is_file() else {}
        config["work_root"] = str(target)
        write_json(config_path, config)
    else:
        atomic_write(work_root_config_path(root), str(target) + "\n")
    if default_config:
        print(json.dumps({"work_root": str(target), "scope": "next-command"}))
    else:
        command_root_show(root, args)


def command_name(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    new_title = semantic_title(args.title, video=work_workflow(work) == "hyperframes_video")
    if not new_title or any(char in new_title for char in "\r\n") or len(new_title) > 40:
        raise HarnessError("Work name must contain 1-40 characters on one line")

    ensure_roots(root)
    with naming_lock(root):
        metadata_path = work / "WORK.md"
        metadata = read_frontmatter(metadata_path)
        workflow = work_workflow(work)
        if workflow == "hyperframes_video":
            title = new_title
        else:
            number = work_id_number(work.name, workflow)
            if number is None:
                number = title_number(str(metadata.get("title", "")))
            if number is None:
                number = next_work_number(list_work_rows(root), workflow)
            if number > 999:
                raise HarnessError("Work name sequence is exhausted")
            title = f"{number:03d}-{new_title}"

        lines = metadata_path.read_text(encoding="utf-8").splitlines()
        frontmatter_end = lines.index("---", 1)
        metadata["title"] = title
        body = lines[frontmatter_end + 1 :]
        for index, line in enumerate(body):
            if line.startswith("# "):
                body[index] = f"# {title}"
                break
        atomic_write(
            metadata_path,
            "---\n"
            + json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))
            + "\n---\n"
            + "\n".join(body)
            + "\n",
        )
    print(title)


def command_use(root: Path, args: argparse.Namespace) -> None:
    work, location = locate_work(root, args.work_id)
    if location == "archive":
        raise HarnessError(f"Work is archived; run 'work reopen {args.work_id}' first")
    focus_work(root, work, args)
    print(work.name)


def command_status(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args, allow_archive=True)
    variant_id = selected_variant_id(root, work, args)
    variant, state = selected_variant(root, work, args) if variant_id or work_workflow(work) == "podcast_quote_image" else (None, None)
    output = {
        "work": read_frontmatter(work / "WORK.md"),
        "location": location,
        "path": str(work),
        "variant": state,
        "variant_path": str(variant) if variant else None,
        "variants": [path.name for path in variant_paths(work)],
        "message": "尚未创建制作版本" if not variant_paths(work) else None,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def command_component_validate(root: Path, args: argparse.Namespace) -> None:
    if args.candidate:
        source = Path(args.component).expanduser()
        if not source.is_absolute():
            source = root / source
        acceptance = None
    else:
        source, acceptance = asset_store.resolve_component(root, args.component)
    release = validate_component_release(source, allow_unapproved=args.candidate or acceptance is not None)
    print(json.dumps({key: release.get(key) for key in ("component_ref", "ratio", "profile", "subtemplate", "package_sha256", "files")}, ensure_ascii=False, indent=2))


def command_component_store(root: Path, args: argparse.Namespace) -> None:
    action = args.component_command
    if action == "root":
        result = asset_store.configure_asset_store(root, Path(args.path)) if args.path else {"asset_root": str(asset_store.asset_store_root(root))}
    elif action == "list":
        result = asset_store.discover_components(root, args.query, kind=args.kind, ratio=args.ratio, tag=args.tag,
            recommendation=args.recommendation, rebuild=args.rebuild, research_root=args.research_root)
    else:
        store = asset_store.asset_store_root(root)
        from component_harness import package_write_lock
        # ponytail: one short store-write lock; split by asset only if contention matters.
        with package_write_lock(asset_store._target(store, ".asset-write.lock")):
            if action == "source-add":
                result = asset_store.register_source(store, Path(args.path))
            elif action == "import":
                result = asset_store.import_component(store, Path(args.path))
            elif action == "pack":
                result = asset_store.pack_source(store, Path(args.path))
            else:
                result = asset_store.accept_component(store, args.component_ref, args.sha256, args.note, runtime_root=root)
        try:
            discovery = asset_store.discover_components(root)
            result = {**result, "discovery_sync": {"synchronized": not discovery["errors"], "errors": discovery["errors"]}}
        except (ComponentError, OSError, ValueError) as exc:
            result = {**result, "discovery_sync": {"synchronized": False, "error": str(exc)}}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_component_install(root: Path, args: argparse.Namespace) -> None:
    if args.project:
        project = asset_store.authoring_project(root, Path(args.project))
    else:
        work, _ = selected_work(root, args)
        require_workflow(work, "hyperframes_video")
        variant, state = selected_variant(root, work, args)
        plan_path = variant / "ANIMATION_PLAN.md"
        plan = read_frontmatter(plan_path)
        if args.purpose == "plan":
            assert_preview_ready(variant, state, purpose="plan", kind="reference")
        elif plan.get("status") != "approved":
            raise HarnessError("ANIMATION_PLAN.md must be approved before Component installation")
        if not animation_plan_contains_component_ref(plan_path, args.component_ref):
            raise HarnessError(f"ANIMATION_PLAN.md does not approve Component {args.component_ref}")
        project = variant / "project"
    component_id, version = parse_component_ref(args.component_ref)
    source, acceptance = asset_store.resolve_component(root, args.source or args.component_ref)
    validate_component_release(source, expected_ref=args.component_ref, allow_unapproved=acceptance is not None)
    if not args.binding_file:
        raise HarnessError("Component installation requires --binding-file/--binding")
    binding_path = Path(args.binding_file).expanduser()
    if not binding_path.is_absolute():
        binding_path = root / binding_path
    binding = binding_path.resolve()
    if not binding.is_file():
        raise HarnessError(f"Binding file is missing: {binding}")
    from component_harness import package_write_lock
    with package_write_lock(work_requests.safe(project.parent, ".runtime/component-install.lock")):
        result = install_component(
            source, project, binding, binding_path=args.destination_binding,
            expected_ref=args.component_ref, acceptance=acceptance)
    result.update({"component_ref": f"{component_id}@v{version}", "project": str(project)})
    if not args.project:
        result.update({"work": work.name, "variant": variant.name})
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_component_verify(root: Path, args: argparse.Namespace) -> None:
    if args.project:
        project = asset_store.authoring_project(root, Path(args.project))
        print(json.dumps(verify_installation(project, component_ref=args.component_ref), ensure_ascii=False, indent=2))
        return
    work, _ = selected_work(root, args)
    require_workflow(work, "hyperframes_video")
    variant, _ = selected_variant(root, work, args)
    result = verify_installation(variant / "project", component_ref=args.component_ref)
    result.update({"work": work.name, "variant": variant.name})
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_variant_add(root: Path, args: argparse.Namespace) -> None:
    with naming_lock(root):
        _command_variant_add(root, args)


def _command_variant_add(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    workflow = work_workflow(work)
    name = checked_variant_name(args.name) if workflow == "hyperframes_video" and args.name is not None else None
    settings = adopted_settings(root, args, work)
    source = None
    if args.copy_from:
        if workflow != "hyperframes_video":
            raise HarnessError("--from is only available for hyperframes_video")
        source_path = work / "variants" / validate_id(args.copy_from, "source variant")
        if not source_path.is_dir():
            raise HarnessError(f"Unknown source variant: {args.copy_from}")
        source = input_path(source_path, "SCRIPT.md")
    elif workflow == "hyperframes_video" and (work / "shared" / "SCRIPT.md").is_file():
        source = work / "shared" / "SCRIPT.md"
    options = dict(workflow=workflow, template=args.template, profile=args.profile,
                   ratio=settings.get("ratio"), subject_position=args.subject_position, copy_script_from=source)
    if workflow == "hyperframes_video":
        metadata = read_frontmatter(work / "WORK.md")
        if metadata.get("purpose") == "test":
            settings["batch"] = args.batch or args.variant_id
        path = create_adopted_variant(root, work, args.variant_id, settings,
                                      shared=not args.copy_from,
                                      branch=args.copy_from, **options)
        if name is not None:
            state = read_json(path / "variant.yaml")
            state["name"] = name
            write_variant(path, state)
    else:
        path = create_variant(root, work, args.variant_id, **options)
    if not args.work_override:
        write_pointer(root, "current-variant", path.name)
    print(path.name)


def command_variant_use(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    variant_id = validate_id(args.variant_id, "variant id")
    if not (work / "variants" / variant_id).is_dir():
        raise HarnessError(f"Unknown variant: {variant_id}")
    if work_workflow(work) == "hyperframes_video":
        write_pointer(root, "current-work", work.name)
    write_pointer(root, "current-variant", variant_id)
    print(variant_id)


def command_variant_list(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args, allow_archive=True)
    rows = []
    for path in variant_paths(work):
        state = read_json(path / "variant.yaml")
        rows.append({"id": path.name, "name": state.get("name") or path.name,
                     "account": state.get("account"), "account_revision": state.get("account_revision"),
                     "status": state.get("status"), "wait_for": state.get("wait_for")})
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def command_wait(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    variant, state = selected_variant(root, work, args)
    status, action = WAIT_REASONS[args.reason]
    state.update(status=status, wait_for=args.reason, next_action=args.next_action or action)
    write_variant(variant, state)
    print(f"{variant.name}: {status}/{args.reason}")


def restore_parked_work(root: Path, work: Path) -> Path:
    destination = works_root(root) / "active" / work.name
    if destination.exists():
        raise HarnessError(f"Active work already exists: {work.name}")
    os.replace(work, destination)
    parked_state_path = destination / ".runtime" / "parked.json"
    parked_state = read_json(parked_state_path) if parked_state_path.is_file() else {"variants": {}}
    saved = parked_state.get("variants", {})
    for variant in variant_paths(destination):
        state = read_json(variant / "variant.yaml")
        prior = saved.get(variant.name, {}) if isinstance(saved, dict) else {}
        state.update(
            status=prior.get("status", "active"),
            wait_for=prior.get("wait_for", "none"),
            next_action=prior.get("next_action", "Continue current production"),
        )
        write_variant(variant, state)
    parked_state_path.unlink(missing_ok=True)
    return destination


def command_resume(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args)
    variant_id = selected_variant_id(root, work, args)
    restored_from_park = location == "parked"
    if location == "parked":
        work = restore_parked_work(root, work)
        if not args.work_override:
            write_pointer(root, "current-work", work.name)
    if not variant_id and work_workflow(work) == "hyperframes_video":
        print(f"{work.name}: active; variants: " + (", ".join(path.name for path in variant_paths(work)) or "尚未创建制作版本"))
        return
    variant, state = selected_variant(root, work, args)
    if not restored_from_park and state.get("status") != "active":
        state.update(status="active", wait_for="none", next_action=args.next_action or "Continue current production")
        write_variant(variant, state)
    print(f"{work.name}/{variant.name}: {state.get('status')}")


def command_park(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args)
    if location == "parked":
        print(work.name)
        return
    saved: dict[str, Any] = {"parked_at": now(), "variants": {}}
    for variant in variant_paths(work):
        state = read_json(variant / "variant.yaml")
        saved["variants"][variant.name] = {
            "status": state.get("status"),
            "wait_for": state.get("wait_for"),
            "next_action": state.get("next_action"),
        }
        state.update(status="parked", wait_for="none", next_action="Resume the parked work")
        write_variant(variant, state)
    write_json(work / ".runtime" / "parked.json", saved)
    destination = works_root(root) / "parked" / work.name
    os.replace(work, destination)
    print(destination.name)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_artifact(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or not relative or ".." in candidate.parts:
        raise HarnessError(f"Invalid Final artifact path: {relative!r}")
    path = root / candidate
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        raise HarnessError(f"Final artifact is missing, empty, or a symlink: {relative}")
    return path


def validate_deliverable_manifest(directory: Path, expected_workflow: str) -> dict[str, Any]:
    if directory.is_symlink() or not directory.is_dir():
        raise HarnessError(f"Final candidate must be a regular directory: {directory}")
    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise HarnessError("Final candidate is missing manifest.json")
    manifest = read_json(manifest_path)
    if manifest.get("schema_version") != 1:
        raise HarnessError("Final manifest schema_version must be 1")
    if manifest.get("workflow") != expected_workflow:
        raise HarnessError(f"Final manifest workflow must be {expected_workflow}")
    if manifest.get("qa") != "passed":
        raise HarnessError("Final manifest QA must be passed")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise HarnessError("Final manifest requires a non-empty artifacts array")

    roles: dict[str, int] = {}
    paths: set[str] = set()
    for item in artifacts:
        if not isinstance(item, dict):
            raise HarnessError("Final manifest artifacts must be objects")
        relative = item.get("path")
        digest = item.get("sha256")
        role = item.get("role")
        if not isinstance(relative, str) or relative in paths:
            raise HarnessError(f"Final manifest has an invalid or duplicate path: {relative!r}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise HarnessError(f"Final manifest has an invalid sha256 for {relative}")
        if not isinstance(role, str) or not role:
            raise HarnessError(f"Final manifest has an invalid role for {relative}")
        path = _manifest_artifact(directory, relative)
        if file_sha256(path) != digest:
            raise HarnessError(f"Final artifact digest mismatch: {relative}")
        paths.add(relative)
        roles[role] = roles.get(role, 0) + 1

    if expected_workflow == "podcast_quote_image":
        if roles.get("image", 0) not in range(8, 13):
            raise HarnessError("podcast_quote_image Final requires 8 to 12 image artifacts")
        if roles.get("contact_sheet") != 1 or roles.get("package") != 1:
            raise HarnessError("podcast_quote_image Final requires one contact sheet and one package")
        publish_payloads = roles.get("publish_payload", 0)
        if manifest.get("publish_contract") == "xiaohongshu_creator_draft_v1" and publish_payloads != 1:
            raise HarnessError("Xiaohongshu Creator draft Final requires one publish payload")
        if publish_payloads not in (0, 1) or len(artifacts) != roles["image"] + 2 + publish_payloads:
            raise HarnessError("podcast_quote_image Final contains unsupported artifact roles")
    actual_files: set[str] = set()
    for path in directory.rglob("*"):
        relative = path.relative_to(directory)
        if relative.parts and relative.parts[0] == "history":
            continue
        if path.is_symlink():
            raise HarnessError(f"Final candidate contains a symlink: {relative.as_posix()}")
        if path.is_file():
            actual_files.add(relative.as_posix())
    expected_files = paths | {"manifest.json"}
    if actual_files != expected_files:
        extras = sorted(actual_files - expected_files)
        missing = sorted(expected_files - actual_files)
        raise HarnessError(f"Final manifest file set mismatch: extras={extras}, missing={missing}")
    return manifest


def next_directory_history_path(final_dir: Path) -> Path:
    versions = []
    for path in (final_dir / "history").glob("final-v[0-9][0-9][0-9]"):
        if path.is_dir():
            versions.append(int(path.name.removeprefix("final-v")))
    return final_dir / "history" / f"final-v{max(versions, default=0) + 1:03d}"


def copy_directory_without_history(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True)
    for path in source.iterdir():
        if path.name == "history":
            continue
        target = destination / path.name
        if path.is_dir():
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)


def snapshot_items(project: Path) -> tuple[str, ...]:
    """Keep legacy snapshots unchanged while freezing installed Components when present."""

    closure = storage.snapshot_files(project)
    if closure is not None:
        return closure
    return SNAPSHOT_ITEMS + tuple(
        name for name in OPTIONAL_SNAPSHOT_ITEMS if (project / name).exists() or (project / name).is_symlink()
    )


def assert_snapshot_source(project: Path) -> None:
    items = snapshot_items(project)
    required = ("index.html", "DESIGN.md", "project-config.json") if storage.snapshot_files(project) is not None else SNAPSHOT_ITEMS
    missing = [name for name in required if not (project / name).exists()]
    if missing:
        raise HarnessError(f"Project snapshot is incomplete: {', '.join(missing)}")
    for name in items:
        source = project / name
        if source.is_symlink():
            raise HarnessError(f"Snapshot source cannot be a symlink: {source}")
        if source.is_dir():
            for directory, names, files in os.walk(source):
                directory_path = Path(directory)
                for child in [*names, *files]:
                    if (directory_path / child).is_symlink():
                        raise HarnessError(f"Snapshot source cannot contain symlinks: {directory_path / child}")


def snapshot_digest(project: Path, kind: str = "executable") -> str:
    digest = hashlib.sha256()
    names = () if kind == "reference" else validate_dependencies(project, layout=True) if kind == "layout" else snapshot_items(project)
    if kind == "reference" and (not project.is_dir() or project.is_symlink() or any(project.iterdir())):
        raise HarnessError("Reference Plan has no source sample; its snapshot must be empty")
    for name in names:
        source = project / name
        paths = [source]
        if source.is_dir():
            paths.extend(sorted(path for path in source.rglob("*") if path.is_file()))
        for path in paths:
            if path.is_file():
                relative = path.relative_to(project).as_posix().encode()
                digest.update(len(relative).to_bytes(4, "big"))
                digest.update(relative)
                digest.update(bytes.fromhex(file_sha256(path)))
    return digest.hexdigest()


def snapshot_tree_manifest(project: Path) -> dict[str, str]:
    """Hash every frozen file when comparing legacy receipt mirrors."""

    if not project.is_dir() or project.is_symlink():
        raise HarnessError(f"Snapshot directory is unavailable: {project}")
    manifest: dict[str, str] = {}
    for path in sorted(project.rglob("*")):
        if path.is_symlink():
            raise HarnessError(f"Snapshot cannot contain symlinks: {path}")
        if path.is_file():
            manifest[path.relative_to(project).as_posix()] = file_sha256(path)
    return manifest


def copy_snapshot(project: Path, destination: Path, kind: str = "executable") -> None:
    destination.mkdir(parents=True)
    if kind == "reference":
        return
    for name in validate_dependencies(project, layout=True) if kind == "layout" else snapshot_items(project):
        source = project / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def assert_preview_ready(variant: Path, state: dict[str, Any], *, purpose: str = "draft", kind: str = "executable") -> None:
    script = read_frontmatter(input_path(variant, "SCRIPT.md"))
    plan = read_frontmatter(variant / "ANIMATION_PLAN.md")
    if script.get("approval") == "pending":
        raise HarnessError("SCRIPT.md still requires approval")
    if script.get("revision") != state.get("script_revision"):
        raise HarnessError("SCRIPT.md revision does not match variant.yaml")
    if purpose != "plan" and plan.get("status") != "approved":
        raise HarnessError("ANIMATION_PLAN.md is not approved")
    if plan.get("revision") != state.get("plan_revision"):
        raise HarnessError("ANIMATION_PLAN.md revision does not match variant.yaml")
    if plan.get("script_revision") != state.get("script_revision"):
        raise HarnessError("ANIMATION_PLAN.md targets a different Script revision")
    if purpose == "plan" and plan.get("research_revision") is None:
        raise HarnessError("Visual Plan requires the current Research revision")
    if plan.get("research_revision") is not None:
        research = read_frontmatter(input_path(variant, "RESEARCH.md"))
        if research.get("status") != "ready":
            raise HarnessError("RESEARCH.md is not ready")
        if research.get("revision") != plan.get("research_revision"):
            raise HarnessError("ANIMATION_PLAN.md targets a different Research revision")
        if research.get("script_revision") != state.get("script_revision"):
            raise HarnessError("RESEARCH.md targets a different Script revision")


def preview_metadata(path: Path) -> dict[str, Any]:
    return read_frontmatter(path / "preview.md")


def assert_full_draft(metadata: dict[str, Any]) -> None:
    if (metadata.get("purpose", "draft") != "draft"
            or metadata.get("scope", "full") != "full"
            or metadata.get("media_readiness", "complete") != "complete"):
        raise HarnessError("Only a full, media-complete Draft can be accepted or finalized")


PREVIEW_DOCUMENTS = ("SCRIPT.md", "RESEARCH.md", "ANIMATION_PLAN.md")


def preview_input_hashes(directory: Path) -> dict[str, str]:
    if any(not input_path(directory, name).is_file() for name in PREVIEW_DOCUMENTS):
        raise HarnessError("Preview requires frozen SCRIPT.md, RESEARCH.md and ANIMATION_PLAN.md inputs")
    return {name: file_sha256(input_path(directory, name)) for name in PREVIEW_DOCUMENTS}


def document_content(path: Path, ignored: tuple[str, ...] = ()) -> tuple[dict[str, Any], str]:
    metadata = read_frontmatter(path)
    return {key: value for key, value in metadata.items() if key not in ignored}, document_body(path)


def same_preview_inputs(preview: Path, variant: Path) -> bool:
    return all(document_content(preview / name, ("status", "visual_plan") if name == "ANIMATION_PLAN.md" else ())
               == document_content(input_path(variant, name), ("status", "visual_plan") if name == "ANIMATION_PLAN.md" else ())
               for name in PREVIEW_DOCUMENTS)


def assert_preview_inputs(preview: Path, metadata: dict[str, Any], current: Path | None = None) -> None:
    frozen_lock = metadata.get("adopted_settings", {}).get("appearance_lock")
    if frozen_lock is not None and metadata.get("kind", "executable") == "executable":
        appearance.verify(preview / "source-snapshot", frozen_lock)
    if "input_sha256" not in metadata:
        return  # Legacy previews cannot prove compatibility, but retain their original lifecycle.
    if preview_input_hashes(preview) != metadata["input_sha256"]:
        raise HarnessError("Frozen preview inputs changed")
    if current is not None and not same_preview_inputs(preview, current):
        raise HarnessError("Preview inputs changed; register the current content before accepting or finalizing")
    if current is not None and "adopted_settings" in metadata:
        state = read_json(current / "variant.yaml")
        if metadata["adopted_settings"] != {key: state.get(key) for key in metadata["adopted_settings"]}:
            raise HarnessError("Adopted Variant settings changed; register and accept a new Draft")


def assert_plan_baseline(variant: Path, state: dict[str, Any], baseline: Path, project: Path) -> None:
    metadata = preview_metadata(baseline)
    if snapshot_digest(baseline / "source-snapshot", metadata.get("kind", "executable")) != metadata.get("snapshot_sha256"):
        raise HarnessError("Accepted Visual Plan snapshot changed")
    assert_preview_inputs(baseline, metadata)
    same_revision = all(metadata.get(key) == state.get(key) for key in ("script_revision", "plan_revision"))
    if same_revision and ("input_sha256" not in metadata or same_preview_inputs(baseline, variant)):
        return
    feedback = variant / ".runtime" / "feedback.json"
    if "input_sha256" in metadata and feedback.is_file():
        for entry in read_json(feedback).get("entries", []):
            if (entry.get("from") == baseline.name and entry.get("compatible") is True
                    and entry.get("baseline_inputs") == metadata["input_sha256"]
                    and entry.get("baseline_snapshot") == metadata["snapshot_sha256"]
                    and entry.get("current_inputs") == preview_input_hashes(variant)
                    and entry.get("current_snapshot") == snapshot_digest(project)):
                return
    raise HarnessError("Draft requires the current Visual Plan to be accepted or a scoped --compatible check")


def preview_source(variant: Path, metadata: dict[str, Any]) -> Path:
    source = (variant / metadata.get("sample_dir", "project")).resolve()
    if not source.is_relative_to(variant.resolve()) or any(source.is_relative_to((variant / name).resolve()) for name in ("previews", "final", ".runtime")):
        raise HarnessError("Sample directory must be Variant-local and outside frozen/runtime directories")
    return source


def command_preview_register(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    purpose = args.purpose
    kind = args.kind
    layout = kind == "layout"
    reference = kind == "reference"
    scene = args.scope == "scene"
    if scene and (kind != "executable" or purpose != "plan" or len(args.scene) != 1):
        raise HarnessError("Scene reference requires --kind executable --purpose plan and exactly one --scene")
    if reference and purpose != "plan":
        raise HarnessError("Reference-only registration requires --purpose plan")
    if layout and (purpose != "plan" or not args.sample_dir or not args.scene):
        raise HarnessError("Layout requires --purpose plan, --sample-dir and --scene")
    if not layout and not scene and (args.sample_dir or args.scene):
        raise HarnessError("--sample-dir and --scene require --kind layout")
    assert_preview_ready(variant, state, purpose=purpose, kind=kind)
    draft = Path(args.draft_file).expanduser().resolve() if args.draft_file else None
    studio_draft = purpose == "draft" and draft is None
    if draft is not None and (not draft.is_file() or draft.stat().st_size == 0):
        raise HarnessError(f"Draft file is missing or empty: {draft}")
    if purpose == "plan" and draft is not None:
        raise HarnessError("Visual Plan uses executable source, not a replacement MP4")
    project = preview_source(variant, {"sample_dir": args.sample_dir}) if args.sample_dir else variant / "project"
    if state.get("appearance_lock") is not None and kind == "executable":
        appearance.verify(project, state["appearance_lock"])
    if kind == "executable":
        assert_snapshot_source(project)
    if kind == "executable" and (project / "COMPONENT_LOCK.json").is_file():
        verify_installation(project)
    elif kind == "executable" and (project / "scene-slots.json").is_file():
        validate_work_surface_inventory(project)
    plan_text = (variant / "ANIMATION_PLAN.md").read_text(encoding="utf-8")
    visual = purpose == "plan" or studio_draft or bool(state.get("accepted_visual_plan"))
    scenes = reference_projection(plan_text) if reference else layout_projection(project, plan_text, args.scene) if layout else scene_projection(project, plan_text, args.scene if scene else None) if visual else None
    if not reference and visual:
        validate_dependencies(project, layout=layout)
    draft_digest = file_sha256(draft) if draft else None
    source_digest = hashlib.sha256().hexdigest() if reference else snapshot_digest(project, kind)
    plan_digest = file_sha256(variant / "ANIMATION_PLAN.md") if visual else None
    input_hashes = preview_input_hashes(variant) if all(input_path(variant, name).is_file() for name in PREVIEW_DOCUMENTS) else None
    if studio_draft:
        input_hashes = preview_input_hashes(variant)
    if purpose == "draft" and state.get("accepted_visual_plan"):
        assert_plan_baseline(variant, state, variant / "previews" / validate_id(state["accepted_visual_plan"], "Visual Plan"), project)
    if draft_digest:
        assert_draft_source(variant, draft_digest, source_digest)
    previews = variant / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    existing = sorted(path for path in previews.glob(f"{purpose}-v[0-9][0-9][0-9]") if path.is_dir())
    for path in existing:
        metadata = preview_metadata(path)
        if (
            metadata.get("draft_sha256") == draft_digest
            and metadata.get("snapshot_sha256") == source_digest
            and metadata.get("script_revision") == state.get("script_revision")
            and metadata.get("plan_revision") == state.get("plan_revision")
            and metadata.get("plan_sha256") == plan_digest
            and metadata.get("input_sha256") == input_hashes
            and ("adopted_settings" not in metadata or metadata["adopted_settings"] == {
                key: state.get(key) for key in metadata["adopted_settings"]})
            and metadata.get("kind", "executable") == kind
            and metadata.get("scope", "full") == args.scope
            and metadata.get("media_readiness", "complete") == args.media_readiness
            and (not (layout or scene) or (metadata.get("sample_scenes") == args.scene and metadata.get("sample_dir") == project.relative_to(variant.resolve()).as_posix()))
        ):
            assert_preview_inputs(path, metadata)
            if snapshot_digest(path / "source-snapshot", kind) != metadata.get("snapshot_sha256"):
                raise HarnessError("Preview snapshot changed")
            print(path.name)
            return
    version = max((int(path.name.removeprefix(f"{purpose}-v")) for path in existing), default=0) + 1
    draft_id = f"{purpose}-v{version:03d}"
    staging = previews / f".{draft_id}.staging-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        if draft:
            shutil.copy2(draft, staging / "draft.mp4")
            if file_sha256(staging / "draft.mp4") != draft_digest:
                raise HarnessError("Draft changed during registration")
        copy_snapshot(project, staging / "source-snapshot", kind)
        if kind == "executable":
            validate_snapshot_closure(project, staging / "source-snapshot")
        if snapshot_digest(staging / "source-snapshot", kind) != source_digest:
            raise HarnessError("Project changed during registration")
        if not reference and visual:
            validate_dependencies(staging / "source-snapshot", layout=layout)
        metadata = {
            "id": draft_id,
            "purpose": purpose,
            "kind": kind,
            "scope": args.scope,
            "media_readiness": args.media_readiness,
            "approval_purpose": "direction" if purpose == "plan" else "full-version",
            "registered_at": now(),
            "draft_sha256": draft_digest,
            "snapshot_sha256": source_digest,
            "script_revision": state.get("script_revision"),
            "plan_revision": state.get("plan_revision"),
            "plan_sha256": plan_digest,
            "adopted_settings": {key: state.get(key) for key in (
                "template", "profile", "theme", "theme_revision", "theme_settings", "mode", "ratio", "subject_position", "account", "account_revision", "account_settings", "batch",
                "background", "motion", "appearance_lock")},
        }
        if input_hashes is not None:
            metadata["input_sha256"] = input_hashes
        if studio_draft:
            metadata["review_mode"] = "studio"
        if layout:
            metadata.update(sample_dir=project.relative_to(variant.resolve()).as_posix(), sample_scenes=args.scene,
                            demonstrated="Sample layout, colors, typography and text hierarchy",
                            unverified="Other scenes, motion, reading speed, media and rendering")
        if scene:
            metadata.update(sample_dir=project.relative_to(variant.resolve()).as_posix(), sample_scenes=args.scene,
                            demonstrated="Direction in the selected executable Scene only",
                            unverified="Other Scenes, full assembly and final media")
        if reference:
            metadata.update(sample_scenes=[], demonstrated="Existing accepted asset previews referenced per Scene in Plan",
                            unverified="Current Work assembly, media, timing and rendering")
        if os.environ.get("HYPERFRAMES_AI_REVIEW") == "1":
            metadata["review"] = work_requests.review_identity(configured_work_root(root) or root)
        for name in PREVIEW_DOCUMENTS:
            if input_path(variant, name).is_file():
                shutil.copy2(input_path(variant, name), staging / name)
        assert_preview_inputs(staging, metadata)
        if visual:
            write_json(staging / "visual-plan.json", {"id": draft_id, "scenes": scenes})
        if state.get("accepted_visual_plan"):
            baseline = variant / "previews" / validate_id(state["accepted_visual_plan"], "Visual Plan")
            baseline_metadata = preview_metadata(baseline)
            assert_preview_inputs(baseline, baseline_metadata)
            metadata["source_plan"] = baseline.name
            metadata["source_plan_sha256"] = baseline_metadata["snapshot_sha256"]
            if snapshot_digest(baseline / "source-snapshot", baseline_metadata.get("kind", "executable")) != metadata["source_plan_sha256"]:
                raise HarnessError("Accepted Visual Plan snapshot changed")
            metadata["changed_files"] = source_changes(baseline / "source-snapshot", staging / "source-snapshot")
        atomic_write(
            staging / "preview.md",
            "---\n" + json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n---\n\n# Preview\n",
        )
        os.replace(staging, previews / draft_id)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    state.update(status="waiting_user", wait_for="plan_approval" if purpose == "plan" else "draft_feedback", next_action=f"Review {draft_id}")
    write_variant(variant, state)
    print(draft_id)


def command_preview_accept(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    if read_frontmatter(work / "WORK.md").get("purpose") == "test":
        raise HarnessError("test Work does not grant production acceptance")
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    draft_id = validate_id(args.draft_id, "draft id")
    preview = variant / "previews" / draft_id
    if draft_id.startswith("plan-v"):
        metadata = preview_metadata(preview)
        assert_preview_inputs(preview, metadata)
        kind = metadata.get("kind", "executable")
        assert_preview_ready(variant, state, purpose="plan", kind=kind)
        if metadata.get("purpose") != "plan" or not (preview / "visual-plan.json").is_file():
            raise HarnessError("Incomplete Visual Plan")
        if kind == "executable":
            assert_snapshot_source(preview / "source-snapshot")
            if metadata.get("scope") == "scene":
                scenes = scene_projection(preview / "source-snapshot", (preview / "ANIMATION_PLAN.md").read_text(encoding="utf-8"), metadata.get("sample_scenes"))
                if read_json(preview / "visual-plan.json") != {"id": draft_id, "scenes": scenes}:
                    raise HarnessError("Scene reference projection changed")
        if snapshot_digest(preview / "source-snapshot", kind) != metadata.get("snapshot_sha256"):
            raise HarnessError("Visual Plan snapshot changed")
        if kind == "layout":
            frozen_plan = preview / "ANIMATION_PLAN.md"
            if file_sha256(frozen_plan) != metadata.get("plan_sha256"):
                raise HarnessError("Frozen Animation Plan changed")
            scenes = layout_projection(preview / "source-snapshot", frozen_plan.read_text(encoding="utf-8"), metadata["sample_scenes"])
            if read_json(preview / "visual-plan.json") != {"id": draft_id, "scenes": scenes}:
                raise HarnessError("Layout sample projection changed")
        if kind == "reference" and read_json(preview / "visual-plan.json") != {
                "id": draft_id, "scenes": reference_projection((preview / "ANIMATION_PLAN.md").read_text(encoding="utf-8"))}:
            raise HarnessError("Reference Plan projection changed")
        for field in ("script_revision", "plan_revision"):
            if metadata.get(field) != state.get(field):
                raise HarnessError(f"Visual Plan has a stale {field}")
        assert_preview_inputs(preview, metadata, variant)
        if kind != "reference" and snapshot_digest(preview_source(variant, metadata), kind) != metadata.get("snapshot_sha256"):
            raise HarnessError("Project changed; register the current Visual Plan before accepting")
        if state.get("accepted_visual_plan") == draft_id:
            current = read_frontmatter(variant / "ANIMATION_PLAN.md")
            original = read_frontmatter(preview / "ANIMATION_PLAN.md")
            for value in (current, original):
                value.pop("status", None)
                value.pop("visual_plan", None)
            current_body = (variant / "ANIMATION_PLAN.md").read_text(encoding="utf-8").split("\n---", 1)[1]
            original_body = (preview / "ANIMATION_PLAN.md").read_text(encoding="utf-8").split("\n---", 1)[1]
            if current != original or current_body != original_body:
                raise HarnessError("Animation Plan changed; register the current Visual Plan before accepting")
            print(draft_id)
            return
        if metadata.get("plan_sha256") != file_sha256(variant / "ANIMATION_PLAN.md"):
            raise HarnessError("Animation Plan changed; register the current Visual Plan before accepting")
        plan_path = variant / "ANIMATION_PLAN.md"
        text = plan_path.read_text(encoding="utf-8")
        end = text.index("\n---", 3)
        plan = read_frontmatter(plan_path)
        plan.update(status="approved", visual_plan=draft_id)
        atomic_write(plan_path, "---\n" + json.dumps(plan, ensure_ascii=False) + text[end:])
        state.update(accepted_visual_plan=draft_id, accepted_preview=None, accepted_plan_revision=None,
                     accepted_script_revision=None, status="active", wait_for="none",
                     next_action="Build each Scene from its confirmed Plan and exact assets; samples apply only to their listed Scenes")
        write_variant(variant, state)
        print(draft_id)
        return
    if not preview.is_dir() or not (preview / "source-snapshot").is_dir():
        raise HarnessError(f"Incomplete preview: {draft_id}")
    metadata = preview_metadata(preview)
    assert_full_draft(metadata)
    assert_preview_inputs(preview, metadata, variant)
    if metadata.get("review_mode") == "studio":
        record = bound_studio(variant, draft_id)
        if (record.get("snapshot_sha256") != metadata.get("snapshot_sha256")
                or snapshot_digest(Path(record["project"])) != metadata.get("snapshot_sha256")):
            raise HarnessError("Studio review source changed; register and review the current Draft")
        if snapshot_digest(variant / "project") != metadata.get("snapshot_sha256"):
            raise HarnessError("Project changed; register the current Draft before accepting")
    elif not (preview / "draft.mp4").is_file() or file_sha256(preview / "draft.mp4") != metadata.get("draft_sha256"):
        raise HarnessError("Draft media changed or missing")
    if snapshot_digest(preview / "source-snapshot") != metadata.get("snapshot_sha256"):
        raise HarnessError("Draft snapshot changed")
    if metadata.get("source_plan") or metadata.get("review_mode") == "studio":
        assert_preview_ready(variant, state)
    if metadata.get("script_revision") != state.get("script_revision"):
        raise HarnessError("Preview targets a different Script revision")
    if metadata.get("plan_revision") != state.get("plan_revision"):
        raise HarnessError("Preview targets a different Plan revision")
    state.update(
        accepted_preview=draft_id,
        accepted_script_revision=metadata.get("script_revision"),
        accepted_plan_revision=metadata.get("plan_revision"),
        status="active",
        wait_for="none",
        next_action="Prepare the final render from the accepted snapshot",
    )
    write_variant(variant, state)
    print(draft_id)


def runtime_path(value: str | None, variable: str) -> Path:
    configured = os.environ.get(variable)
    if not value and not configured:
        raise HarnessError(f"Runtime is not configured: {variable}")
    result = Path(value or configured).expanduser().resolve()
    if configured and result != Path(configured).expanduser().resolve():
        raise HarnessError(f"Runtime override must match the pinned session: {variable}")
    return result


def assert_draft_source(variant: Path, output_hash: str, source_hash: str) -> None:
    records = [read_json(path) for path in (variant / ".runtime").glob("render*/render.json")]
    latest = variant / ".runtime" / "render.json"
    if latest.is_file():
        records.append(read_json(latest))
    records += [preview_metadata(path.parent) for path in (variant / "previews").glob("draft-v*/preview.md")]
    matching = [row for row in records if row.get("output_sha256", row.get("draft_sha256")) == output_hash]
    if matching and not any(row.get("snapshot_sha256") == source_hash for row in matching):
        raise HarnessError("Draft output belongs to different source; render the changed project before registration")


def checked_preview(variant: Path, preview_id: str) -> tuple[Path, dict[str, Any]]:
    preview = variant / "previews" / validate_id(preview_id, "preview")
    metadata = preview_metadata(preview)
    assert_preview_inputs(preview, metadata)
    kind = metadata.get("kind", "executable")
    if snapshot_digest(preview / "source-snapshot", kind) != metadata.get("snapshot_sha256"):
        raise HarnessError("Preview snapshot changed")
    if metadata.get("plan_sha256") and file_sha256(preview / "ANIMATION_PLAN.md") != metadata["plan_sha256"]:
        raise HarnessError("Frozen Animation Plan changed")
    if (preview / "visual-plan.json").is_file():
        plan_text = (preview / "ANIMATION_PLAN.md").read_text(encoding="utf-8")
        scenes = reference_projection(plan_text) if kind == "reference" else layout_projection(preview / "source-snapshot", plan_text, metadata["sample_scenes"]) if kind == "layout" else scene_projection(preview / "source-snapshot", plan_text, metadata.get("sample_scenes") if metadata.get("scope") == "scene" else None)
        if read_json(preview / "visual-plan.json") != {"id": preview.name, "scenes": scenes}:
            raise HarnessError("Visual Plan projection changed; it must be generated from the frozen sources")
    return preview, metadata


def studio_record(variant: Path, target: str) -> Path:
    return variant / ".runtime" / f"studio-{validate_id(target, 'preview')}.json"


def bound_studio(variant: Path, target: str) -> dict[str, Any]:
    path = studio_record(variant, target)
    if not path.is_file():
        raise HarnessError("No Studio process record; use preview open for this exact target first")
    record = read_json(path)
    project = Path(record["project"]).resolve()
    expected = variant / "project" if target == "current" else variant / ".runtime" / record["review_directory"] / target
    if (record.get("target") != target or record.get("work") != variant.parent.parent.name
            or record.get("variant") != variant.name or project != expected.resolve()
            or target != "current" and not project.is_relative_to((variant / ".runtime").resolve())):
        raise HarnessError("Studio process record does not match this Work/Variant/target")
    return record


def command_preview_open(root: Path, args: argparse.Namespace) -> None:
    with naming_lock(root):
        _command_preview_open(root, args)


def _command_preview_open(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args, allow_archive=True)
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    target = validate_id(args.preview_id, "preview")
    if target == "current" and (args.legacy or location == "archive"):
        raise HarnessError("Current project is editable; choose a registered preview for historical review")
    if target == "current":
        project, kind, metadata = variant / "project", "executable", {}
        if state.get("appearance_lock") is not None:
            appearance.verify(project, state["appearance_lock"])
    else:
        preview, metadata = checked_preview(variant, target)
        kind = metadata.get("kind", "executable")
        if kind == "reference":
            raise HarnessError(f"This Plan has no new sample; use the accepted asset Preview references in {preview / 'ANIMATION_PLAN.md'}")
        if args.legacy:
            if not (preview / "visual-plan.json").is_file():
                raise HarnessError("Legacy review needs visual-plan.json; use Studio or the registered MP4")
            serve(preview, None if kind == "layout" else runtime_path(args.hyperframes_dist, "HYPERFRAMES_DIST"), args.port,
                  metadata.get("review"), layout=kind == "layout")
            return
        if studio_record(variant, target).is_file():
            previous = bound_studio(variant, target)
            if previous.get("snapshot_sha256") != metadata["snapshot_sha256"]:
                raise HarnessError("Studio review source differs from the registered snapshot")
            project = Path(previous["project"])
        else:
            project = variant / ".runtime" / f"studio-review-{uuid.uuid4().hex}" / target
            if kind == "executable":
                assert_snapshot_source(preview / "source-snapshot")
            copy_snapshot(preview / "source-snapshot", project, kind)
            if snapshot_digest(project, kind) != metadata["snapshot_sha256"]:
                raise HarnessError("Studio review copy differs from the registered snapshot")
            if kind == "layout":
                studio_preview.adapt_layout(project)
    if not (project / "index.html").is_file():
        raise HarnessError(f"Studio project has no index.html: {project}")
    if project.is_symlink() or any(path.is_symlink() for path in project.rglob("*")):
        raise HarnessError("Editable Studio projects cannot contain symlinks to frozen or external files")
    validate_dependencies(project, layout=kind == "layout")
    if (project / "COMPONENT_LOCK.json").is_file():
        verify_installation(project)
    cli = runtime_path(args.hyperframes_cli, "HYPERFRAMES_CLI")
    session = studio_preview.start(cli, project.resolve(), args.port, no_open=args.no_open, layout=kind == "layout")
    previous = read_json(studio_record(variant, target)) if studio_record(variant, target).is_file() else {}
    record = {"work": work.name, "variant": variant.name, "target": target, "project": str(project.resolve()),
              "kind": kind, "port": session["port"], "url": session["studioUrl"], "pid": session.get("pid"),
              "snapshot_sha256": metadata.get("snapshot_sha256"), "cli_sha256": file_sha256(cli),
              "opened_source_sha256": previous.get("opened_source_sha256", snapshot_digest(project, kind)), "opened_at": now()}
    if os.environ.get("HYPERFRAMES_AI_RESOLVED_CONFIG"):
        config = json.loads(os.environ["HYPERFRAMES_AI_RESOLVED_CONFIG"])
        record["tool_root"] = str(root)
        record["tool_release"] = os.environ.get("HYPERFRAMES_AI_VERSION")
        record["content_roots"] = {key: config.get(key) for key in ("work_root", "asset_root", "asset_source_roots", "review")}
    if session.get("browser_profile"):
        record["browser_profile"] = session["browser_profile"]
    if target != "current":
        record["review_directory"] = project.parent.name
    write_json(studio_record(variant, target), record)
    print(json.dumps(record, ensure_ascii=False, indent=2))


def command_preview_studio(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args, allow_archive=True)
    require_workflow(work, "hyperframes_video")
    variant, _ = selected_variant(root, work, args)
    record = bound_studio(variant, args.preview_id)
    cli = runtime_path(args.hyperframes_cli, "HYPERFRAMES_CLI")
    if file_sha256(cli) != record["cli_sha256"]:
        raise HarnessError("Studio runtime changed; close the old process and reopen this target")
    project = Path(record["project"])
    if args.preview_command == "stop":
        result = studio_preview.stop(cli, project, record["port"])
        write_json(studio_record(variant, args.preview_id), {**record, "stopped_at": now()})
    else:
        result = studio_preview.context(cli, project, record["port"], args.fields, args.detail)
        result["work"] = {key: record[key] for key in ("work", "variant", "target", "url")}
        result["source_changed"] = snapshot_digest(project, record["kind"]) != record["opened_source_sha256"]
        render = variant / ".runtime" / "render.json"
        if args.preview_id == "current" and render.is_file():
            result["render_matches_source"] = read_json(render).get("snapshot_sha256") == snapshot_digest(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_preview_diff(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args, allow_archive=not bool(args.note))
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    preview = variant / "previews" / validate_id(args.preview_id, "preview")
    metadata = preview_metadata(preview)
    assert_preview_inputs(preview, metadata)
    kind = metadata.get("kind", "executable")
    if snapshot_digest(preview / "source-snapshot", kind) != metadata.get("snapshot_sha256"):
        raise HarnessError("Preview snapshot changed")
    with tempfile.TemporaryDirectory() as temp:
        candidate = Path(temp) / "source"
        source = variant / "project" if args.compatible or kind == "reference" else preview_source(variant, metadata)
        source_kind = "executable" if args.compatible or kind == "reference" else kind
        if source_kind == "executable":
            assert_snapshot_source(source)
        copy_snapshot(source, candidate, source_kind)
        changed = source_changes(preview / "source-snapshot", candidate)
    projection = preview / "visual-plan.json"
    scenes = read_json(projection)["scenes"] if projection.is_file() else []
    if args.compatible:
        if preview.name != state.get("accepted_visual_plan") or not args.note or not args.scene:
            raise HarnessError("--compatible requires the accepted Visual Plan, --scene and a checked --note")
        if "input_sha256" not in metadata:
            raise HarnessError("Legacy preview has no frozen inputs for compatibility")
        assert_preview_ready(variant, state)
        ignored = ("status", "visual_plan", "revision", "script_revision", "research_revision")
        if document_content(preview / "ANIMATION_PLAN.md", ignored) != document_content(variant / "ANIMATION_PLAN.md", ignored):
            raise HarnessError("Animation Plan intent changed; confirm the affected Plan instead of --compatible")
        if script_text(preview / "SCRIPT.md", anchors=True) != script_text(input_path(variant, "SCRIPT.md"), anchors=True):
            raise HarnessError("Narration changed; confirm the affected Plan instead of --compatible")
        for name in PREVIEW_DOCUMENTS:
            before, after = read_frontmatter(preview / name), read_frontmatter(input_path(variant, name))
            changed_content = document_content(preview / name, ("revision", "status", "visual_plan")) != document_content(input_path(variant, name), ("revision", "status", "visual_plan"))
            if changed_content and (not isinstance(after.get("revision"), int) or after["revision"] <= before.get("revision", 0)):
                raise HarnessError(f"{name} changed without an increased revision")
        scenes = scene_projection(source, (variant / "ANIMATION_PLAN.md").read_text(encoding="utf-8"))
        outside = [s["id"] for s in scenes if s["source"] in changed
                   and (preview / "source-snapshot" / s["source"]).is_file() and s["id"] not in args.scene]
        if outside:
            raise HarnessError(f"Changed Scene files outside checked scope: {', '.join(outside)}")
    if set(args.scene) - {s["id"] for s in scenes}:
        raise HarnessError("Feedback Scene must exist in this preview")
    selected = [s for s in scenes if s["id"] in args.scene]
    if args.range and kind in {"layout", "reference"}:
        raise HarnessError("Static layout feedback has no time range; use --scene")
    if args.range and (not selected or not min(s["start"] for s in selected) <= args.range[0] <= args.range[1]
                       or args.range[1] > max(s["start"] + s["duration"] for s in selected)):
        raise HarnessError("Feedback range needs a Scene and must lie within the preview")
    if args.note and not args.scene:
        raise HarnessError("Feedback note requires --scene")
    affected = [s["id"] for s in scenes if s["source"] in changed]
    shared = [p for p in changed if p not in {s["source"] for s in scenes}]
    result = {"from": preview.name, "changed_files": changed, "affected_scenes": affected,
              "shared_changes": shared, "requested_scenes": args.scene, "range": args.range,
              "note": args.note or "Shared changes require checking dependent Scenes and handoffs"}
    if args.compatible:
        result.update(compatible=True, baseline_inputs=metadata["input_sha256"], baseline_snapshot=metadata["snapshot_sha256"],
                      current_inputs=preview_input_hashes(variant), current_snapshot=snapshot_digest(source))
    if args.note:
        feedback_path = variant / ".runtime" / "feedback.json"
        feedback = read_json(feedback_path) if feedback_path.exists() else {"entries": []}
        feedback["entries"].append({**result, "recorded_at": now()})
        write_json(feedback_path, feedback)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def measured_process(command: list[str], evidence: Path | None, operation: str, **kwargs: Any) -> subprocess.CompletedProcess:
    if evidence is None:
        return subprocess.run(command, **kwargs)
    telemetry = read_json(evidence) if evidence.is_file() else {"schema_version": 1, "calls": []}
    call = {"operation": operation, "started_at": now(), "state": "running", "launch_attempts": 1,
            "completed_process_calls": 0, "elapsed_seconds": None, "returncode": None,
            "wrapper_retries": 0, "tool_retries": None, "cache_hits": None, "tokens": None, "cost": None}
    telemetry["calls"].append(call)
    write_json(evidence, telemetry)
    started = time.perf_counter()
    try:
        result = subprocess.run(command, **kwargs)
        call.update(completed_process_calls=1, returncode=result.returncode,
                    state="succeeded" if result.returncode == 0 else "failed")
        return result
    except BaseException:
        call["state"] = "interrupted-or-launch-failed"
        raise
    finally:
        call["elapsed_seconds"] = time.perf_counter() - started
        write_json(evidence, telemetry)


def command_preview_render(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    if (not args.final or read_frontmatter(work / "WORK.md").get("purpose") == "test"
            or os.environ.get("HYPERFRAMES_AI_REVIEW") == "1"):
        raise HarnessError("Draft and test video export is forbidden; use Studio")
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    review = os.environ.get("HYPERFRAMES_AI_REVIEW") == "1"
    assert_preview_ready(variant, state, purpose="plan" if review else "draft")
    if args.fps <= 0:
        raise HarnessError("Render fps must be positive")
    preview_id = validate_id(args.preview_id, "preview")
    expected = state.get("accepted_preview" if args.final else "accepted_visual_plan")
    if preview_id != expected and not review:
        raise HarnessError("Render must start from the accepted Draft (Final) or Visual Plan (Draft)")
    baseline = variant / "previews" / preview_id
    metadata = preview_metadata(baseline)
    if args.final:
        assert_full_draft(metadata)
    assert_preview_inputs(baseline, metadata, variant if args.final else None)
    if args.final or review:
        for field in ("script_revision", "plan_revision"):
            if metadata.get(field) != state.get(field):
                raise HarnessError(f"Render baseline has a stale {field}")
    if snapshot_digest(baseline / "source-snapshot", metadata.get("kind", "executable")) != metadata.get("snapshot_sha256"):
        raise HarnessError("Render baseline snapshot changed")
    source = baseline / "source-snapshot" if args.final or (review and metadata.get("kind", "executable") == "executable") else variant / "project"
    if args.refined_project:
        source = Path(args.refined_project).expanduser().resolve()
        if not source.is_relative_to(variant.resolve()) or source.is_relative_to((variant / "previews").resolve()):
            raise HarnessError("Refined project must be Work-local and outside frozen previews")
    if not args.final and not review:
        assert_plan_baseline(variant, state, baseline, source)
    assert_snapshot_source(source)
    validate_dependencies(source)
    cli = runtime_path(args.hyperframes_cli, "HYPERFRAMES_CLI")
    if not cli.is_file():
        raise HarnessError(f"HyperFrames CLI is missing: {cli}")
    for key in ("HYPERFRAMES_NODE", "HYPERFRAMES_BROWSER_PATH", "HYPERFRAMES_FFMPEG_PATH", "HYPERFRAMES_FFPROBE_PATH"):
        if os.environ.get(key) and not Path(os.environ[key]).is_file():
            raise HarnessError(f"Pinned render dependency is missing: {key}; repair the installation, not the Work")
    output = Path(args.output).expanduser().resolve()
    if review and not output.is_relative_to(variant.resolve()):
        raise HarnessError("Review test renders must stay inside the Review Variant")
    if output.exists():
        raise HarnessError("Render output already exists; choose a new path")
    if output.is_relative_to((variant / "previews").resolve()) or output.is_relative_to((variant / "final").resolve()):
        raise HarnessError("Render outside frozen previews and Final; finalize performs promotion")
    render_id = f"render-{uuid.uuid4().hex[:12]}"
    render_dir = variant / ".runtime" / render_id
    frozen = render_dir / "source-snapshot"
    copy_snapshot(source, frozen)
    validate_snapshot_closure(source, frozen)
    validate_dependencies(frozen)
    source_hash = snapshot_digest(frozen)
    if args.final and source_hash != metadata.get("snapshot_sha256"):
        raise HarnessError("Final source differs from the accepted Draft; register and accept a new Draft")
    command = [os.environ.get("HYPERFRAMES_NODE", "node"), str(cli), "render", "--output", str(output), "--fps", str(args.fps), "--quality", "high" if args.final else "draft"]
    if args.software_gl:
        command.append("--no-browser-gpu")
    result = measured_process(command, render_dir / "telemetry.json", "hyperframes-render",
                              cwd=frozen, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    atomic_write(render_dir / "render.log", result.stdout)
    print(result.stdout, end="")
    if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        raise HarnessError(f"HyperFrames render failed ({result.returncode}); diagnostic source retained at {render_dir}")
    if re.search(r"PAGEERROR|sub_timeline_readiness_timeout|Error creating WebGL context", result.stdout):
        raise HarnessError(f"HyperFrames reported a runtime failure despite producing a file; inspect {render_dir / 'render.log'}")
    if snapshot_digest(frozen) != source_hash:
        raise HarnessError("Render source changed during rendering")
    record = {"purpose": "review-test" if review else "final" if args.final else "draft", "source_preview": preview_id,
              "parent_snapshot_sha256": metadata["snapshot_sha256"], "snapshot_sha256": source_hash,
              "source_snapshot": str(frozen.relative_to(variant)), "changed_files": source_changes(baseline / "source-snapshot", frozen),
              "output_sha256": file_sha256(output), "fps": args.fps, "quality": "high" if args.final else "draft",
              "software_gl": args.software_gl, "hyperframes_cli_sha256": file_sha256(cli),
              "script_revision": state["script_revision"], "plan_revision": state["plan_revision"], "rendered_at": now()}
    record["telemetry"] = str((render_dir / "telemetry.json").relative_to(variant))
    if os.environ.get("HYPERFRAMES_AI_RESOLVED_CONFIG"):
        config = json.loads(os.environ["HYPERFRAMES_AI_RESOLVED_CONFIG"])
        record["tool_root"] = str(root)
        record["tool_release"] = os.environ.get("HYPERFRAMES_AI_VERSION")
        record["content_roots"] = {key: config.get(key) for key in ("work_root", "asset_root", "asset_source_roots", "review")}
    if review:
        record["review"] = work_requests.review_identity(configured_work_root(root) or root)
    write_json(render_dir / "render.json", record)
    write_json(variant / ".runtime" / "render.json", record)
    print(str(output))


def required_variants(work: Path) -> list[str]:
    values = read_frontmatter(work / "WORK.md").get("required_variants")
    if values is None and work_workflow(work) == "hyperframes_video":
        return []
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise HarnessError("WORK.md requires a required_variants list")
    if not values and work_workflow(work) == "podcast_quote_image":
        raise HarnessError("WORK.md requires a non-empty required_variants list")
    return [validate_id(value, "required variant") for value in values]


def all_required_finals_exist(work: Path) -> bool:
    workflow = work_workflow(work)
    required = required_variants(work)
    if not required:
        return False
    for variant_id in required:
        variant = work / "variants" / variant_id
        if not variant.is_dir():
            raise HarnessError(f"Required variant does not exist: {variant_id}")
        state = read_json(variant / "variant.yaml")
        current = state.get("current_final")
        if workflow == "hyperframes_video":
            if current != "final.mp4" or not (variant / "final" / "final.mp4").is_file():
                return False
        elif current != "manifest.json":
            return False
        else:
            validate_deliverable_manifest(variant / "final", workflow)
    return True


def next_final_history_path(final_dir: Path) -> Path:
    versions = []
    for path in (final_dir / "history").glob("final-v[0-9][0-9][0-9].mp4"):
        versions.append(int(path.stem.removeprefix("final-v")))
    return final_dir / "history" / f"final-v{max(versions, default=0) + 1:03d}.mp4"


def archive_destination(root: Path, work_id: str) -> Path:
    return works_root(root) / "archive" / f"{datetime.now().astimezone():%Y-%m}" / work_id


def move_to_archive(root: Path, work: Path, outcome: str) -> Path:
    write_json(work / ".runtime" / "archive.json", {"outcome": outcome, "archived_at": now(), "soft": True})
    return work


def clear_current_if(root: Path, work_id: str) -> None:
    if read_pointer(root, "current-work") == work_id:
        clear_pointer(root, "current-work")
        clear_pointer(root, "current-variant")


def promote_final_directory(candidate: Path, final_dir: Path, workflow: str) -> str:
    validate_deliverable_manifest(candidate, workflow)
    candidate_digest = file_sha256(candidate / "manifest.json")
    existing_manifest = final_dir / "manifest.json"
    if existing_manifest.is_file() and file_sha256(existing_manifest) == candidate_digest:
        validate_deliverable_manifest(final_dir, workflow)
        return candidate_digest
    if candidate == final_dir or final_dir in candidate.parents:
        raise HarnessError("Final candidate cannot be the target Final directory or one of its children")

    staging = final_dir.parent / f".final.staging-{uuid.uuid4().hex}"
    backup = final_dir.parent / f".final.backup-{uuid.uuid4().hex}"
    try:
        copy_directory_without_history(candidate, staging)
        validate_deliverable_manifest(staging, workflow)
        if final_dir.is_dir():
            existing_history = final_dir / "history"
            if existing_history.is_dir():
                shutil.copytree(existing_history, staging / "history")
            if existing_manifest.is_file():
                history_path = next_directory_history_path(staging)
                copy_directory_without_history(final_dir, history_path)
            os.replace(final_dir, backup)
        os.replace(staging, final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        if backup.exists() and not final_dir.exists():
            os.replace(backup, final_dir)
        raise
    finally:
        shutil.rmtree(backup, ignore_errors=True)
    return candidate_digest


def command_finalize_package(
    root: Path,
    args: argparse.Namespace,
    work: Path,
    location: str,
) -> None:
    candidate = Path(args.final_file).expanduser().resolve()
    workflow = work_workflow(work)
    if workflow != "podcast_quote_image":
        raise HarnessError(f"Unsupported packaged Final workflow: {workflow}")
    validate_deliverable_manifest(candidate, workflow)
    candidate_digest = file_sha256(candidate / "manifest.json")
    variant, state = selected_variant(root, work, args)
    final_dir = variant / "final"

    if location == "archive":
        archived_manifest = final_dir / "manifest.json"
        if archived_manifest.is_file() and file_sha256(archived_manifest) == candidate_digest:
            validate_deliverable_manifest(final_dir, workflow)
            write_json(
                variant / ".runtime" / "finalize.json",
                {"state": "complete", "final_manifest_sha256": candidate_digest},
            )
            clear_current_if(root, work.name)
            print(str(final_dir))
            return
        raise HarnessError("Archived work has a different Final; reopen it before finalizing")
    if not args.qa_passed:
        raise HarnessError("Final QA must pass before finalize; use --qa-passed after the required checks")

    candidate_digest = promote_final_directory(candidate, final_dir, workflow)
    write_json(
        variant / ".runtime" / "qa" / "final.json",
        {
            "passed": True,
            "workflow": workflow,
            "final_manifest_sha256": candidate_digest,
            "recorded_at": now(),
        },
    )
    state.update(current_final="manifest.json", status="active", wait_for="none", next_action="Finalize complete")
    write_variant(variant, state)
    write_json(
        variant / ".runtime" / "finalize.json",
        {"state": "promoted", "final_manifest_sha256": candidate_digest},
    )

    write_json(variant / ".runtime" / "finalize.json", {"state": "complete", "final_manifest_sha256": candidate_digest})
    print(str(final_dir))


def command_finalize(root: Path, args: argparse.Namespace) -> None:
    # ponytail: one WorkStore lock; use per-Work locks if concurrent Finalize throughput matters.
    with naming_lock(root):
        _command_finalize(root, args)


def reclaim_final_candidates(variant: Path, completed: Path | None = None) -> list[str]:
    """Run only under naming_lock; candidates are registered after successful promotion."""
    runtime = variant / ".runtime"
    registry_path = runtime / "final-candidates.json"
    registry = read_json(registry_path) if registry_path.is_file() else {"schema_version": 1, "entries": []}
    if not isinstance(registry.get("entries"), list) or not all(isinstance(entry, dict) for entry in registry["entries"]):
        raise HarnessError("Invalid Final candidate cleanup registry; retaining temporary files")
    if completed is not None:
        relative = completed.relative_to(runtime).as_posix()
        storage.scoped_path(runtime, relative)
        registry["entries"].append({"path": relative, "state": "succeeded", "rebuildable": True,
                                    "sha256": file_sha256(completed), "registered_at": now()})
        write_json(registry_path, registry)
    final = variant / "final" / "final.mp4"
    manifest_path = variant / "final" / "manifest.json"
    if not final.is_file() or not manifest_path.is_file():
        return []
    manifest = read_json(manifest_path)
    digest = file_sha256(final)
    if manifest.get("final_sha256") != digest:
        return []
    references = set()
    for receipt in (manifest.get("render", {}), read_json(runtime / "render.json") if (runtime / "render.json").is_file() else {}):
        if not isinstance(receipt, dict):
            raise HarnessError("Invalid render reference; retaining temporary files")
        source = receipt.get("source_snapshot")
        if source:
            resolved = storage.scoped_path(variant, source)
            if resolved.is_relative_to(runtime):
                references.add(resolved.relative_to(runtime).as_posix())
    removed = []
    for entry in registry["entries"]:
        if entry.get("state") != "succeeded" or entry.get("sha256") != digest:
            continue
        candidate = storage.scoped_path(runtime, entry["path"])
        if not candidate.is_file() or file_sha256(candidate) != digest:
            continue
        qa_path = candidate.parent / "qa.json"
        if not qa_path.is_file():
            continue
        qa = read_json(qa_path)
        if qa.get("passed") is not True or qa.get("sha256") != digest:
            continue
        reclaimed = storage.reclaim(runtime, [entry], references)
        if reclaimed:
            entry.update(state="removed", removed_at=now())
            removed.extend(reclaimed)
    if removed:
        write_json(registry_path, registry)
    return removed


def _command_finalize(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args, allow_archive=True)
    if read_frontmatter(work / "WORK.md").get("purpose") == "test":
        raise HarnessError("test Work cannot Finalize or export video")
    if work_workflow(work) == "podcast_quote_image":
        if not args.final_file:
            raise HarnessError("Package Finalize requires a deliverable directory")
        command_finalize_package(root, args, work, location)
        return
    variant, state = selected_variant(root, work, args)
    if location != "archive":
        try:
            reclaim_final_candidates(variant)
        except (OSError, HarnessError, storage.StorageError) as exc:
            print(f"Prior temporary cleanup retained: {exc}", file=sys.stderr)
    if not args.final_file:
        if location == "archive":
            raise HarnessError("Reopen before Finalize")
        accepted = state.get("accepted_preview")
        if not accepted:
            raise HarnessError("No accepted preview")
        job = variant / ".runtime" / f"finalize-{uuid.uuid4().hex[:12]}"
        job.mkdir(parents=True)
        render_args = argparse.Namespace(**vars(args))
        render_args.preview_id, render_args.final = accepted, True
        render_args.output, render_args.refined_project = str(job / "candidate.mp4"), None
        try:
            command_preview_render(root, render_args)
            qa = encoded_video_qa(Path(render_args.output), evidence=job / "telemetry.json")
            write_json(job / "qa.json", qa)
            promote_args = argparse.Namespace(**vars(args))
            promote_args.final_file, promote_args.qa_passed = render_args.output, True
            command_finalize_video(root, promote_args, work, location)
        except (HarnessError, OSError) as exc:
            write_json(job / "failure.json", {"error": str(exc), "at": now()})
            raise HarnessError(f"Finalize failed; inspect failure/recovery evidence at {job}: {exc}") from exc
        try:
            removed = reclaim_final_candidates(variant, Path(render_args.output))
            write_json(job / "cleanup.json", {"removed": removed})
        except (OSError, HarnessError, storage.StorageError) as exc:
            print(f"Final is complete; temporary cleanup deferred: {exc}", file=sys.stderr)
        return
    command_finalize_video(root, args, work, location)


def encoded_video_qa(candidate: Path, *, evidence: Path | None = None) -> dict[str, Any]:
    probe = os.environ.get("HYPERFRAMES_FFPROBE_PATH", "ffprobe")
    decoder = os.environ.get("HYPERFRAMES_FFMPEG_PATH", "ffmpeg")
    result = measured_process([probe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(candidate)],
                              evidence, "ffprobe-qa", check=False, capture_output=True, text=True)
    try:
        metadata = json.loads(result.stdout)
        videos = [stream for stream in metadata["streams"] if stream.get("codec_type") == "video"]
        valid = (result.returncode == 0 and len(videos) == 1 and videos[0].get("width", 0) > 0
                 and videos[0].get("height", 0) > 0 and float(metadata["format"]["duration"]) > 0)
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise HarnessError("Encoded output QA failed: invalid video stream or duration")
    decoded = measured_process([decoder, "-v", "error", "-xerror", "-i", str(candidate), "-f", "null", "-"],
                               evidence, "ffmpeg-decode-qa", check=False, capture_output=True, text=True)
    if decoded.returncode or decoded.stderr.strip():
        raise HarnessError(f"Encoded output QA failed during full decode: {decoded.stderr}")
    return {"passed": True, "sha256": file_sha256(candidate), "probe": metadata, "full_decode": True}


def command_finalize_video(
    root: Path, args: argparse.Namespace, work: Path, location: str,
) -> None:
    variant, _ = selected_variant(root, work, args)
    journal = variant / ".runtime" / "final-promotion"
    files = ("final/final.mp4", "final/manifest.json", "variant.yaml", ".runtime/finalize.json", ".runtime/qa/final.json")

    def restore() -> None:
        originals = read_json(journal / "prepared.json")
        for name in files:
            target = variant / name
            if originals[name]:
                temporary = target.with_name(f".{target.name}.restore-{uuid.uuid4().hex}")
                shutil.copy2(journal / name, temporary)
                os.replace(temporary, target)
            else:
                target.unlink(missing_ok=True)

    if (journal / "prepared.json").is_file():
        restore()
    if journal.exists():
        shutil.rmtree(journal)
    journal.mkdir(parents=True)
    originals = {}
    for name in files:
        source = variant / name
        originals[name] = source.is_file()
        if source.is_file():
            backup = journal / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, backup)
    write_json(journal / "prepared.json", originals)
    try:
        _command_finalize_video(root, args, work, location)
        os.replace(journal / "prepared.json", journal / "committed.json")
    except BaseException:
        try:
            restore()
            os.replace(journal / "prepared.json", journal / "restored.json")
        except OSError as recovery_error:
            raise HarnessError(f"Final promotion recovery pending at {journal}: {recovery_error}") from recovery_error
        raise
    else:
        try:
            shutil.rmtree(journal)
        except OSError:
            pass  # Committed recovery evidence is harmless and cleaned on the next operation.


def _command_finalize_video(
    root: Path,
    args: argparse.Namespace,
    work: Path,
    location: str,
) -> None:
    candidate = Path(args.final_file).expanduser().resolve()
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise HarnessError(f"Final file is missing or empty: {candidate}")
    candidate_digest = file_sha256(candidate)
    variant, state = selected_variant(root, work, args)
    final_dir = variant / "final"
    final_file = final_dir / "final.mp4"
    manifest_path = final_dir / "manifest.json"

    if location == "archive":
        if final_file.is_file() and file_sha256(final_file) == candidate_digest:
            write_json(variant / ".runtime" / "finalize.json", {"state": "complete", "final_sha256": candidate_digest})
            clear_current_if(root, work.name)
            print(str(final_file))
            return
        raise HarnessError("Archived work has a different Final; reopen it before finalizing")
    if not args.qa_passed:
        raise HarnessError("Final QA must pass before finalize; use --qa-passed after the required checks")
    accepted = state.get("accepted_preview")
    if not accepted:
        raise HarnessError("No accepted preview")
    if state.get("accepted_script_revision") != state.get("script_revision"):
        raise HarnessError("Accepted preview targets a different Script revision")
    if state.get("accepted_plan_revision") != state.get("plan_revision"):
        raise HarnessError("Accepted preview targets a different Plan revision")
    accepted_path = variant / "previews" / validate_id(str(accepted), "accepted preview")
    if not (accepted_path / "source-snapshot").is_dir():
        raise HarnessError("Accepted preview source snapshot is missing")
    assert_preview_ready(variant, state)
    accepted_metadata = preview_metadata(accepted_path)
    assert_full_draft(accepted_metadata)
    assert_preview_inputs(accepted_path, accepted_metadata, variant)
    accepted_source = accepted_path / "source-snapshot"
    recorded_snapshot_digest = accepted_metadata.get("snapshot_sha256")
    current_snapshot_digest = snapshot_digest(accepted_source)

    render_record = None
    frozen = None
    legacy_compatibility = None
    if state.get("accepted_visual_plan") or accepted_metadata.get("review_mode") == "studio":
        render_record = read_json(variant / ".runtime" / "render.json")
        if (render_record.get("purpose") != "final" or render_record.get("source_preview") != accepted
                or render_record.get("output_sha256") != candidate_digest
                or render_record.get("parent_snapshot_sha256") != recorded_snapshot_digest
                or render_record.get("script_revision") != state.get("script_revision")
                or render_record.get("plan_revision") != state.get("plan_revision")):
            raise HarnessError("Final needs a matching preview render --final result from the accepted Draft")
        frozen = (variant / str(render_record.get("source_snapshot", ""))).resolve()
        if not frozen.is_relative_to((variant / ".runtime").resolve()) or not frozen.is_dir():
            raise HarnessError("Final render source snapshot changed or escaped the Work")
        frozen_snapshot_digest = snapshot_digest(frozen)
        if accepted_metadata.get("review_mode") == "studio" and (
                render_record.get("snapshot_sha256") != recorded_snapshot_digest
                or current_snapshot_digest != recorded_snapshot_digest):
            raise HarnessError("Final source differs from the accepted Studio Draft")
        if current_snapshot_digest == recorded_snapshot_digest:
            if frozen_snapshot_digest != render_record.get("snapshot_sha256"):
                raise HarnessError("Final render source snapshot changed or escaped the Work")
        else:
            if (render_record.get("snapshot_sha256") != recorded_snapshot_digest
                    or render_record.get("changed_files") != []):
                raise HarnessError("Accepted Draft snapshot changed")
            accepted_tree = snapshot_tree_manifest(accepted_source)
            frozen_tree = snapshot_tree_manifest(frozen)
            if accepted_tree != frozen_tree:
                raise HarnessError("Accepted Draft snapshot changed; legacy final-render snapshot differs")
            legacy_compatibility = {
                "schema_version": 1,
                "accepted_preview": accepted,
                "recorded_snapshot_sha256": recorded_snapshot_digest,
                "current_snapshot_sha256": current_snapshot_digest,
                "mirror_snapshot": str(frozen.relative_to(variant)),
                "mirror_current_snapshot_sha256": frozen_snapshot_digest,
                "verified_file_count": len(accepted_tree),
                "basis": "byte-identical accepted and final-render snapshots with an unchanged render receipt",
                "verified_at": now(),
            }
    elif current_snapshot_digest != recorded_snapshot_digest:
        raise HarnessError("Accepted Draft snapshot changed")

    final_dir.mkdir(parents=True, exist_ok=True)
    (final_dir / "history").mkdir(exist_ok=True)
    current_digest = file_sha256(final_file) if final_file.is_file() else None
    if current_digest != candidate_digest:
        if final_file.is_file():
            history_digests = {
                file_sha256(path) for path in (final_dir / "history").glob("final-v[0-9][0-9][0-9].mp4")
            }
            if current_digest not in history_digests:
                history_path = next_final_history_path(final_dir)
                temporary_history = history_path.with_name(f".{history_path.name}.{uuid.uuid4().hex}")
                shutil.copy2(final_file, temporary_history)
                os.replace(temporary_history, history_path)
        staging = final_dir / f".final.staging-{uuid.uuid4().hex}.mp4"
        shutil.copy2(candidate, staging)
        if file_sha256(staging) != candidate_digest:
            staging.unlink(missing_ok=True)
            raise HarnessError("Final staging digest mismatch")
        os.replace(staging, final_file)

    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    registered = (
        manifest.get("schema_version") == 1
        and manifest.get("workflow") == "hyperframes_video"
        and manifest.get("artifacts") == [{"path": "final.mp4", "role": "video", "sha256": candidate_digest}]
        and manifest.get("final_sha256") == candidate_digest
        and manifest.get("source_preview") == accepted
        and manifest.get("script_revision") == state.get("script_revision")
        and manifest.get("plan_revision") == state.get("plan_revision")
        and manifest.get("qa") == "passed"
    )
    if not registered:
        manifest = {
            "schema_version": 1,
            "workflow": "hyperframes_video",
            "artifacts": [{"path": "final.mp4", "role": "video", "sha256": candidate_digest}],
            "final_sha256": candidate_digest,
            "source_preview": accepted,
            "script_revision": state.get("script_revision"),
            "plan_revision": state.get("plan_revision"),
            "finalized_at": now(),
            "qa": "passed",
        }
        if render_record:
            manifest["render"] = render_record
        write_json(manifest_path, manifest)
        write_json(
            variant / ".runtime" / "qa" / "final.json",
            {"passed": True, "final_sha256": candidate_digest, "recorded_at": now()},
        )
    if legacy_compatibility:
        compatibility_path = variant / ".runtime" / "qa" / "legacy-snapshot-compatibility.json"
        compatibility_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(compatibility_path, legacy_compatibility)
    state.update(current_final="final.mp4", status="active", wait_for="none", next_action="Finalize complete")
    write_variant(variant, state)
    write_json(variant / ".runtime" / "finalize.json", {"state": "promoted", "final_sha256": candidate_digest})

    write_json(variant / ".runtime" / "finalize.json", {"state": "complete", "final_sha256": candidate_digest})
    print(str(final_file))


def command_archive(root: Path, args: argparse.Namespace) -> None:
    work_id = args.work_override or read_pointer(root, "current-work")
    if not work_id:
        raise HarnessError("No current work")
    work, location = locate_work(root, work_id)
    if location == "archive":
        metadata_path = work / ".runtime" / "archive.json"
        metadata = read_json(metadata_path) if metadata_path.is_file() else {}
        if metadata.get("outcome") != args.outcome:
            raise HarnessError(f"Work is already archived with outcome {metadata.get('outcome')}")
        print(str(work))
        return
    archived = move_to_archive(root, work, args.outcome)
    clear_current_if(root, work.name)
    print(str(archived))


def command_reopen(root: Path, args: argparse.Namespace) -> None:
    work, location = locate_work(root, args.work_id)
    if any(work.name in record["chain"][:-1] for record in identity_state(root)["successions"].values()):
        raise HarnessError("Succession predecessor must remain archived")
    if location == "archive":
        archive_path = work / ".runtime" / "archive.json"
        record = read_json(archive_path) if archive_path.is_file() else {}
        if not record.get("soft"):
            raise HarnessError("Legacy physical archive remains read-only; create a new Work for further production")
        history_path = work / ".runtime" / "archive-history.json"
        history = read_json(history_path) if history_path.is_file() else {"entries": []}
        history["entries"].append({**record, "reopened_at": now()})
        write_json(history_path, history)
        archive_path.unlink()
        location = "parked" if work.parent.name == "parked" else "active"
    if location == "parked":
        work = restore_parked_work(root, work)
    focus_work(root, work, args)
    print(str(work))


def add_variant_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--account")
    parser.add_argument("--batch")
    parser.add_argument("--theme")
    parser.add_argument("--background", help="accepted background id@vN")
    parser.add_argument("--appearance-file", help="JSON selections, motion slots and parameter overrides")
    parser.add_argument("--fps", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--mode", choices=("text-led", "animation-led"))
    parser.add_argument("--template", choices=sorted(TEMPLATES))
    parser.add_argument("--profile", choices=sorted(PROFILES))
    parser.add_argument("--ratio", choices=sorted(RATIOS))
    parser.add_argument("--subject-position", choices=sorted(SUBJECT_POSITIONS))


def command_review_init(root: Path, args: argparse.Namespace) -> None:
    print(work_requests.init_review(configured_work_root(root) or root, args.review_id))


def command_request(root: Path, args: argparse.Namespace) -> None:
    store = configured_work_root(root) or root
    action = args.request_command
    if action == "freeze":
        work, _ = selected_work(root, args, allow_archive=True)
        variant, _ = selected_variant(root, work, args)
        with naming_lock(root):
            result = work_requests.freeze(store, work, variant, args.request_id, Path(args.brief), args.scene,
                                          args.file, args.context_file, args.preview)
    else:
        revision = Path(args.revision).expanduser().resolve()
        if action == "export":
            result = work_requests.export_request(revision, Path(args.output).expanduser().resolve())
        elif action == "deliver":
            result = work_requests.deliver(revision, args.delivery_id, Path(args.source).expanduser().resolve(),
                                          Path(args.component).resolve() if args.component else None,
                                          Path(args.binding).resolve() if args.binding else None)
        else:
            delivery = Path(args.delivery).expanduser().resolve()
            if action == "review":
                result = work_requests.review(store, revision, delivery, read_json, write_variant)
            elif action == "feedback":
                request, candidate = work_requests.checked_pair(revision, delivery)
                result = revision.parent / "feedback" / f"{uuid.uuid4().hex}.json"
                write_json(result, {"request_id": request["request_id"], "revision": request["revision"],
                                    "delivery_id": candidate["delivery_id"], "delivery_sha256": file_sha256(delivery / "delivery.json"),
                                    "note": args.note, "recorded_at": now()})
            else:
                if not revision.is_relative_to(store / "requests"):
                    raise HarnessError("Accept the handoff in the production WorkStore requests directory")
                work, _ = selected_work(root, args)
                variant, _ = selected_variant(root, work, args)
                result = work_requests.accept(store, revision, delivery, variant,
                                              Path(args.approved_component).resolve() if args.approved_component else None)
    print(str(result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="work", description="Local creative Work lifecycle")
    parser.add_argument("--work", dest="work_override", help="temporarily select a Work")
    parser.add_argument("--variant", dest="variant_override", help="temporarily select a Variant")
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new")
    new.add_argument("title")
    new.add_argument("--purpose", choices=("standard", "ip", "test"))
    new.add_argument("--series")
    new.add_argument("--source-work")
    new.add_argument("--source-variant")
    new.add_argument("--source-version")
    new.add_argument("--variant-id", help="ID for an optional initial video Variant (requires --account for production)")
    new.add_argument("--workflow", choices=sorted(WORKFLOWS), required=True)
    new.add_argument("--detached", action="store_true", help="create without changing the foreground Current Work")
    new.add_argument("--separate", action="store_true", help="Create a separate test Work with the same name")
    add_variant_options(new)
    new.set_defaults(handler=command_new)

    commands.add_parser("current").set_defaults(handler=command_current)
    listing = commands.add_parser("list")
    listing.add_argument("--tree", action="store_true")
    listing.set_defaults(handler=command_list)
    browser = commands.add_parser("browser", help="Rebuild the disposable WorkStore directory")
    browser.add_argument("action", choices=("rebuild",))
    browser.set_defaults(handler=command_browser_rebuild)
    find = commands.add_parser("find", help="Find video Variants by series number")
    find.add_argument("--series", required=True)
    find.add_argument("--number", type=int, required=True)
    find.add_argument("--account")
    find.add_argument("--history", action="store_true", help="Show the retained succession chain")
    find.set_defaults(handler=command_find)
    successor = commands.add_parser("successor", help="Adopt an archived accepted video into a new Work at the same series number")
    successor.add_argument("source_work")
    successor.add_argument("--source-variant", required=True)
    successor.add_argument("--source-version", required=True)
    successor.add_argument("--account", required=True)
    successor.add_argument("--variant-id", default="main")
    successor.add_argument("--title")
    successor.add_argument("--detached", action="store_true")
    successor.set_defaults(handler=command_successor)
    migrate = commands.add_parser("migrate", help="One-time RC2 video identity migration")
    migrations = migrate.add_subparsers(dest="migrate_command", required=True)
    dry_run = migrations.add_parser("dry-run")
    dry_run.add_argument("--title-overrides", help="JSON map of old Work ID to semantic title")
    dry_run.add_argument("--purpose-overrides", help="JSON map of old Work ID to explicit purpose")
    dry_run.add_argument("--only", action="append", help="Migrate a safe Work subset; repeat for multiple IDs")
    dry_run.add_argument("--output", help="Write the exact mapping for later apply")
    dry_run.set_defaults(handler=command_migrate)
    apply = migrations.add_parser("apply")
    apply.add_argument("--mapping", required=True, help="Mapping produced by migrate dry-run")
    apply.set_defaults(handler=command_migrate)
    research_catalog.register_cli(commands)
    appearance_parser = commands.add_parser("appearance", help="Resolve or explicitly rebind exact appearance assets")
    appearance_commands = appearance_parser.add_subparsers(dest="appearance_command", required=True)
    resolve = appearance_commands.add_parser("resolve")
    add_variant_options(resolve)
    resolve.set_defaults(handler=command_appearance_resolve)
    rebind = appearance_commands.add_parser("rebind", help="Preview an exact Variant update; --apply commits it")
    add_variant_options(rebind)
    rebind.add_argument("--apply", action="store_true")
    rebind.add_argument("--upgrade-runtime", action="store_true", help="Upgrade a known old runtime in the editable project only")
    rebind.set_defaults(handler=command_appearance_update)
    appearance_commands.add_parser("recover", help="Recover a pending update of the explicit Work/Variant").set_defaults(handler=command_appearance_update)
    for kind in ("account", "series", "theme"):
        config_parser = commands.add_parser(kind)
        operations = config_parser.add_subparsers(dest="operation", required=True)
        for operation in ("put", "get", "list"):
            operation_parser = operations.add_parser(operation)
            if operation != "list":
                operation_parser.add_argument("identity")
            if operation == "put":
                operation_parser.add_argument("--file", required=True)
            operation_parser.set_defaults(handler=command_config)
        if kind == "series":
            move = operations.add_parser("move", help="Move the selected production video Work to another series")
            move.add_argument("identity")
            move.set_defaults(handler=command_series_move)
    root_command = commands.add_parser("root", help="Show or set the external WorkStore root")
    root_commands = root_command.add_subparsers(dest="root_command", required=True)
    root_commands.add_parser("show").set_defaults(handler=command_root_show)
    root_set = root_commands.add_parser("set")
    root_set.add_argument("path")
    root_set.set_defaults(handler=command_root_set)
    name = commands.add_parser("name")
    name.add_argument("title")
    name.set_defaults(handler=command_name)
    use = commands.add_parser("use")
    use.add_argument("work_id")
    use.set_defaults(handler=command_use)
    commands.add_parser("status").set_defaults(handler=command_status)

    script = commands.add_parser("script")
    script_commands = script.add_subparsers(dest="script_command", required=True)
    script_output = script_commands.add_parser("text", help="Narration for reading, counts, TTS or alignment")
    script_output.add_argument("--anchors", action="store_true", help="Keep stable paragraph Anchor comments")
    script_output.set_defaults(handler=command_script_text)

    review = commands.add_parser("review", help="Create an isolated Harness test WorkStore")
    reviews = review.add_subparsers(dest="review_command", required=True)
    review_init = reviews.add_parser("init")
    review_init.add_argument("review_id")
    review_init.set_defaults(handler=command_review_init)

    request = commands.add_parser("request", help="Freeze private input, deliver and review exact candidates")
    requests = request.add_subparsers(dest="request_command", required=True)
    freeze = requests.add_parser("freeze")
    freeze.add_argument("request_id")
    freeze.add_argument("--brief", required=True)
    freeze.add_argument("--scene", action="append", required=True)
    freeze.add_argument("--file", action="append", required=True, help="Affected project-relative file; may be new")
    freeze.add_argument("--context-file", action="append", default=[], help="Read-only project-relative reproduction input")
    freeze.add_argument("--preview", help="Use this frozen preview rather than the working project")
    freeze.set_defaults(handler=command_request)
    export = requests.add_parser("export")
    export.add_argument("revision")
    export.add_argument("--output", required=True)
    export.set_defaults(handler=command_request)
    deliver = requests.add_parser("deliver")
    deliver.add_argument("revision")
    deliver.add_argument("delivery_id")
    deliver.add_argument("--source", required=True, help="Patch directory containing only affected project-relative files")
    deliver.add_argument("--component", help="Optional immutable component package")
    deliver.add_argument("--binding", help="Reviewed Scene Binding for the component")
    deliver.set_defaults(handler=command_request)
    for name in ("review", "feedback", "accept"):
        command = requests.add_parser(name)
        command.add_argument("revision")
        command.add_argument("--delivery", required=True)
        if name == "feedback":
            command.add_argument("--note", required=True)
        if name == "accept":
            command.add_argument("--approved-component")
        command.set_defaults(handler=command_request)

    component = commands.add_parser("component", help="Validate and install immutable Component Releases")
    component_commands = component.add_subparsers(dest="component_command", required=True)
    component_validate = component_commands.add_parser("validate")
    component_validate.add_argument("component")
    component_validate.add_argument("--candidate", action="store_true", help="Validate a package path without declaring it accepted or production-ready")
    component_validate.set_defaults(handler=command_component_validate)
    component_root = component_commands.add_parser("root", help="Show or configure the independent AssetStore")
    component_root.add_argument("path", nargs="?")
    component_root.set_defaults(handler=command_component_store)
    for name in ("source-add", "import", "pack"):
        command = component_commands.add_parser(name)
        command.add_argument("path")
        command.set_defaults(handler=command_component_store)
    component_list = component_commands.add_parser("list", help="Discover packages from their metadata, not a Harness allowlist")
    component_list.add_argument("--query", default="")
    component_list.add_argument("--kind", choices=("component", "module", "media", "audio", "theme", "background", "motion"))
    component_list.add_argument("--ratio")
    component_list.add_argument("--tag")
    component_list.add_argument("--recommendation", choices=("recommended", "historical", "pending"))
    component_list.add_argument("--rebuild", action="store_true", help="Rebuild the derived discovery cache")
    component_list.add_argument("--research-root", type=Path, help="Include explicitly registered reference documents")
    component_list.set_defaults(handler=command_component_store)
    component_accept = component_commands.add_parser("accept", help="Accept an exact locally reviewed asset version")
    component_accept.add_argument("component_ref")
    component_accept.add_argument("--sha256", required=True)
    component_accept.add_argument("--note", required=True)
    component_accept.set_defaults(handler=command_component_store)
    component_install = component_commands.add_parser("install")
    component_install.add_argument("--project", help="Standalone sample inside a registered AssetSource; never a Work")
    component_install.add_argument("component_ref")
    component_install.add_argument("--source", help="Component package path or component ref")
    component_install.add_argument(
        "--binding-file",
        "--binding",
        dest="binding_file",
        required=True,
        help="Required reviewed Scene Binding JSON; no component-id inference is performed",
    )
    component_install.add_argument("--destination-binding")
    component_install.add_argument("--purpose", choices=("plan", "draft"), default="draft")
    component_install.set_defaults(handler=command_component_install)
    component_verify = component_commands.add_parser("verify")
    component_verify.add_argument("--project", help="Verify a standalone AssetSource sample")
    component_verify.add_argument("component_ref", nargs="?")
    component_verify.set_defaults(handler=command_component_verify)

    variant = commands.add_parser("variant")
    variant_commands = variant.add_subparsers(dest="variant_command", required=True)
    variant_add = variant_commands.add_parser("add")
    variant_add.add_argument("variant_id")
    variant_add.add_argument("--from", dest="copy_from")
    variant_add.add_argument("--name")
    add_variant_options(variant_add)
    variant_add.set_defaults(handler=command_variant_add)
    variant_use = variant_commands.add_parser("use")
    variant_use.add_argument("variant_id")
    variant_use.set_defaults(handler=command_variant_use)
    variant_commands.add_parser("list").set_defaults(handler=command_variant_list)
    variant_name = variant_commands.add_parser("name")
    variant_name.add_argument("name")
    variant_name.set_defaults(handler=command_variant_name)

    wait = commands.add_parser("wait")
    wait.add_argument("reason", choices=sorted(WAIT_REASONS))
    wait.add_argument("--next-action")
    wait.set_defaults(handler=command_wait)
    resume = commands.add_parser("resume")
    resume.add_argument("--next-action")
    resume.set_defaults(handler=command_resume)
    commands.add_parser("park").set_defaults(handler=command_park)

    preview = commands.add_parser("preview")
    preview_commands = preview.add_subparsers(dest="preview_command", required=True)
    preview_register = preview_commands.add_parser("register")
    preview_register.add_argument("draft_file", nargs="?", help="Optional legacy MP4; omit to freeze an executable Draft for Studio review")
    preview_register.add_argument("--purpose", choices=("plan", "draft"), default="draft")
    preview_register.add_argument("--kind", choices=("reference", "layout", "executable"), default="executable")
    preview_register.add_argument("--scope", choices=("full", "scene"), default="full", help="Single executable Scene direction reference or full project")
    preview_register.add_argument("--media-readiness", choices=("complete", "planned_placeholders"), default="complete", help="Declare planned media placeholders; these versions cannot authorize Final")
    preview_register.add_argument("--sample-dir", help="Variant-local layout or single Scene project containing index.html")
    preview_register.add_argument("--scene", action="append", default=[])
    preview_register.set_defaults(handler=command_preview_register)
    preview_accept = preview_commands.add_parser("accept")
    preview_accept.add_argument("draft_id")
    preview_accept.set_defaults(handler=command_preview_accept)
    preview_open = preview_commands.add_parser("open")
    preview_open.add_argument("preview_id", nargs="?", default="current", help="Editable current project or a registered version reviewed in isolation")
    preview_open.add_argument("--legacy", action="store_true", help="Explicit historical custom viewer, never the default Studio route")
    preview_open.add_argument("--no-open", action="store_true", help="Return the actual Studio URL without launching a browser")
    preview_open.add_argument("--hyperframes-cli", help="Pinned official CLI (defaults to the bound runtime)")
    preview_open.add_argument("--hyperframes-dist", help="Player bundles for --legacy only")
    preview_open.add_argument("--port", type=int, default=0)
    preview_open.set_defaults(handler=command_preview_open)
    for name in ("context", "stop"):
        studio_command = preview_commands.add_parser(name)
        studio_command.add_argument("preview_id", nargs="?", default="current")
        studio_command.add_argument("--hyperframes-cli")
        if name == "context":
            studio_command.add_argument("--fields", default="selection", help="Comma-separated selection, lint, server, capabilities")
            studio_command.add_argument("--detail", choices=("compact", "full"), default="compact")
        studio_command.set_defaults(handler=command_preview_studio)
    preview_diff = preview_commands.add_parser("diff")
    preview_diff.add_argument("preview_id")
    preview_diff.add_argument("--scene", action="append", default=[])
    preview_diff.add_argument("--range", nargs=2, type=float, metavar=("START", "END"))
    preview_diff.add_argument("--note", help="Record this scoped feedback in existing Work runtime notes")
    preview_diff.add_argument("--compatible", action="store_true", help="Record checked local equivalent edits, not a new acceptance")
    preview_diff.set_defaults(handler=command_preview_diff)
    preview_render = preview_commands.add_parser("render")
    preview_render.add_argument("preview_id")
    preview_render.add_argument("--hyperframes-cli")
    preview_render.add_argument("--output", required=True)
    preview_render.add_argument("--final", action="store_true")
    preview_render.add_argument("--refined-project")
    preview_render.add_argument("--fps", type=int, default=60)
    preview_render.add_argument("--software-gl", action="store_true", help="Use HyperFrames software WebGL on hosts without a hardware context")
    preview_render.set_defaults(handler=command_preview_render)

    finalize = commands.add_parser("finalize")
    finalize.add_argument("final_file", nargs="?")
    finalize.add_argument("--hyperframes-cli")
    finalize.add_argument("--fps", type=int, default=60)
    finalize.add_argument("--software-gl", action="store_true")
    finalize.add_argument("--qa-passed", action="store_true")
    finalize.set_defaults(handler=command_finalize)
    archive = commands.add_parser("archive")
    archive.add_argument("--outcome", default="stored", choices=("stored", "abandoned", "superseded", "completed"))
    archive.set_defaults(handler=command_archive)
    reopen = commands.add_parser("reopen")
    reopen.add_argument("work_id")
    reopen.set_defaults(handler=command_reopen)
    return parser


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    target_root = (root or repo_root()).resolve()
    try:
        store = configured_work_root(target_root) or target_root
        review = os.environ.get("HYPERFRAMES_AI_REVIEW") == "1"
        release_file = Path(__file__).resolve().parents[1] / ".release.json"
        if not release_file.is_file():
            release_file = target_root / ".release.json"
        if release_file.is_file() and read_json(release_file).get("channel") == "candidate" and not review:
            if (args.command not in {"status", "current", "review"}
                    and not (args.command == "root" and args.root_command == "show")):
                raise HarnessError("Candidate Harness requires an isolated Review root")
        migration_journal = runtime_root(target_root) / work_migration.JOURNAL
        if migration_journal.is_file() and not (args.command == "migrate" and args.migrate_command == "apply"):
            raise HarnessError(f"RC2 migration is incomplete; resume with migrate apply: {migration_journal}")
        successor_journal = runtime_root(target_root) / work_successor.JOURNAL
        if successor_journal.exists() and args.command != "successor":
            raise HarnessError("Succession recovery pending; retry the original successor command")
        if review or (store / ".runtime" / "review.json").exists():
            identity = work_requests.review_identity(store)
            if not review:
                raise HarnessError("Review WorkStore requires an isolated root configuration")
            if identity.get("work") and (args.command == "new" or args.work_override not in (None, identity["work"])
                                         or args.variant_override not in (None, identity["variant"])
                                         or args.command == "use" and args.work_id != identity["work"]):
                raise HarnessError("Request Review is pinned to its exact Work/Variant")
            if (args.command in {"finalize", "archive", "reopen", "park", "review", "migrate", "successor"}
                    or args.command == "root" and args.root_command == "set"
                    or args.command == "preview" and (args.preview_command == "accept" or getattr(args, "final", False))
                    or args.command == "component" and args.component_command in {"install", "accept"}
                    and not os.environ.get("HYPERFRAMES_AI_ASSET_REVIEW_ROOT")
                    or args.command == "request" and args.request_command not in {"freeze", "export", "feedback"}):
                raise HarnessError("Review forbids production acceptance, installation and lifecycle promotion")
        if (args.command in {"archive", "reopen", "park", "resume"}
                or args.command == "preview" and args.preview_command == "render"):
            ensure_roots(target_root)
            with naming_lock(target_root):
                args.handler(target_root, args)
        else:
            args.handler(target_root, args)
        if (args.command in {"new", "successor", "name", "wait", "resume", "park", "archive", "reopen", "finalize"}
                or args.command == "variant" and args.variant_command in {"add", "name"}
                or args.command == "series" and args.operation in {"put", "move"}
                or args.command == "account" and args.operation == "put"
                or args.command == "preview" and args.preview_command == "accept"
                or args.command == "migrate" and args.migrate_command == "apply" and args.migration_applied):
            try:
                refresh_browser(target_root)
            except (HarnessError, OSError) as exc:
                print(f"warning: browser directory not refreshed: {exc}", file=sys.stderr)
    except (HarnessError, ComponentError, VisualPlanError, appearance.AppearanceError, storage.StorageError,
            work_requests.RequestError, work_migration.MigrationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
