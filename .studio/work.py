#!/usr/bin/env python3
"""Local lifecycle CLI for HyperFrames AI works."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Iterable
import unicodedata
import uuid


WORKFLOWS = {"hyperframes_video", "podcast_quote_image"}
TEMPLATES = {"talking_head", "pure_hyperframes"}
PROFILES = {"optical_fluidity", "kami_editorial", "monochrome_atelier"}
RATIOS = {"16:9", "9:16", "source"}
SUBJECT_POSITIONS = {"left", "center", "right"}
WAIT_REASONS = {
    "script_approval": ("waiting_user", "Wait for SCRIPT.md approval"),
    "recording": ("waiting_asset", "Wait for the talking-head recording"),
    "plan_approval": ("waiting_user", "Wait for ANIMATION_PLAN.md approval"),
    "draft_feedback": ("waiting_user", "Wait for Draft feedback or acceptance"),
    "voiceover": ("waiting_asset", "Wait for the final voiceover"),
    "external_asset": ("waiting_asset", "Wait for an external media asset"),
    "quote_selection": ("waiting_user", "Wait for quote selection confirmation"),
    "transcript_fallback": ("waiting_user", "Wait for the transcript fallback decision"),
    "source_metadata": ("waiting_user", "Wait for source metadata"),
}
SNAPSHOT_ITEMS = ("index.html", "compositions", "DESIGN.md", "project-config.json")
ID_PATTERN = re.compile(r"^[\w.-]+$", re.UNICODE)


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


def slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).strip().lower()
    slug = "".join(char if char.isalnum() else "-" for char in normalized)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:48].rstrip("-") or "untitled"


def works_root(root: Path) -> Path:
    return root / "works"


def runtime_root(root: Path) -> Path:
    return root / ".studio" / ".runtime"


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
    for location in ("active", "parked"):
        candidate = works_root(root) / location / work_id
        if candidate.is_dir():
            return candidate, location
    for candidate in archived_work_paths(root):
        if candidate.name == work_id:
            return candidate, "archive"
    raise HarnessError(f"Unknown work: {work_id}")


def list_work_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for location in ("active", "parked"):
        parent = works_root(root) / location
        if parent.is_dir():
            for path in sorted(parent.iterdir()):
                if path.is_dir():
                    metadata = read_frontmatter(path / "WORK.md")
                    rows.append(
                        {
                            "id": path.name,
                            "title": str(metadata.get("title", "")),
                            "workflow": str(metadata.get("workflow", "hyperframes_video")),
                            "location": location,
                        }
                    )
    for path in archived_work_paths(root):
        metadata = read_frontmatter(path / "WORK.md")
        rows.append(
            {
                "id": path.name,
                "title": str(metadata.get("title", "")),
                "workflow": str(metadata.get("workflow", "hyperframes_video")),
                "location": "archive",
            }
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
    return [path for path in sorted(variants.iterdir()) if path.is_dir()]


def selected_variant(root: Path, work: Path, args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    variant_id = args.variant_override or read_pointer(root, "current-variant")
    if not variant_id or not (work / "variants" / variant_id).is_dir():
        variant_id = "main" if (work / "variants" / "main").is_dir() else None
    if not variant_id:
        available = ", ".join(path.name for path in variant_paths(work)) or "none"
        raise HarnessError(f"No current variant. Available: {available}")
    validate_id(variant_id, "variant id")
    path = work / "variants" / variant_id
    if not path.is_dir():
        raise HarnessError(f"Unknown variant: {variant_id}")
    return path, read_json(path / "variant.yaml")


def write_variant(path: Path, data: dict[str, Any]) -> None:
    write_json(path / "variant.yaml", data)


def create_video_variant(
    root: Path,
    work: Path,
    variant_id: str,
    *,
    template: str,
    profile: str,
    ratio: str,
    subject_position: str | None,
    copy_script_from: Path | None = None,
) -> Path:
    validate_id(variant_id, "variant id")
    if template not in TEMPLATES:
        raise HarnessError(f"Unknown template: {template}")
    if profile not in PROFILES:
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
        "PROFILE": json_string_content(profile),
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
    atomic_write(path / "PACKAGE.md", "# Package\n\n## 标题\n\n## 封面文字\n\n## 一句话\n\n")
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
        profile=profile or "optical_fluidity",
        ratio=ratio or "9:16",
        subject_position=subject_position,
        copy_script_from=copy_script_from,
    )


def command_new(root: Path, args: argparse.Namespace) -> None:
    if args.workflow == "podcast_quote_image" and any(
        value is not None for value in (args.template, args.profile, args.ratio, args.subject_position)
    ):
        raise HarnessError("podcast_quote_image does not accept video Template, Profile, Ratio, or subject options")
    ensure_roots(root)
    base_id = f"work-{datetime.now().astimezone():%Y%m%d}-{slugify(args.title)}"
    work_id = base_id
    suffix = 2
    while any(row["id"] == work_id for row in list_work_rows(root)):
        work_id = f"{base_id}-{suffix}"
        suffix += 1
    work = works_root(root) / "active" / work_id
    work.mkdir(parents=True)
    created_at = datetime.now().astimezone().date().isoformat()
    atomic_write(
        work / "WORK.md",
        template_text(
            root,
            "WORK.template.md",
            {
                "WORK_ID": json_string_content(work_id),
                "TITLE": json_string_content(args.title),
                "CREATED_AT": created_at,
                "WORKFLOW": json_string_content(args.workflow),
            },
        ),
    )
    atomic_write(work / "source.md", "# Source\n\n")
    (work / "materials").mkdir()
    create_variant(
        root,
        work,
        "main",
        workflow=args.workflow,
        template=args.template,
        profile=args.profile,
        ratio=args.ratio,
        subject_position=args.subject_position,
    )
    write_pointer(root, "current-work", work_id)
    write_pointer(root, "current-variant", "main")
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
    print(json.dumps(list_work_rows(root), ensure_ascii=False, indent=2))


def command_use(root: Path, args: argparse.Namespace) -> None:
    work, location = locate_work(root, args.work_id)
    if location == "archive":
        raise HarnessError(f"Work is archived; run 'work reopen {args.work_id}' first")
    write_pointer(root, "current-work", work.name)
    variants = variant_paths(work)
    variant_id = "main" if (work / "variants" / "main").is_dir() else (variants[0].name if variants else None)
    if variant_id:
        write_pointer(root, "current-variant", variant_id)
    else:
        clear_pointer(root, "current-variant")
    print(work.name)


def command_status(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args, allow_archive=True)
    variant, state = selected_variant(root, work, args)
    output = {
        "work": read_frontmatter(work / "WORK.md"),
        "location": location,
        "path": str(work),
        "variant": state,
        "variant_path": str(variant),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def command_variant_add(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    workflow = work_workflow(work)
    source = None
    if args.copy_from:
        if workflow != "hyperframes_video":
            raise HarnessError("--from is only available for hyperframes_video")
        source_path = work / "variants" / validate_id(args.copy_from, "source variant")
        if not source_path.is_dir():
            raise HarnessError(f"Unknown source variant: {args.copy_from}")
        source = source_path / "SCRIPT.md"
    path = create_variant(
        root,
        work,
        args.variant_id,
        workflow=workflow,
        template=args.template,
        profile=args.profile,
        ratio=args.ratio,
        subject_position=args.subject_position,
        copy_script_from=source,
    )
    write_pointer(root, "current-variant", path.name)
    print(path.name)


def command_variant_use(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    variant_id = validate_id(args.variant_id, "variant id")
    if not (work / "variants" / variant_id).is_dir():
        raise HarnessError(f"Unknown variant: {variant_id}")
    write_pointer(root, "current-variant", variant_id)
    print(variant_id)


def command_variant_list(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args, allow_archive=True)
    rows = []
    for path in variant_paths(work):
        state = read_json(path / "variant.yaml")
        rows.append({"id": path.name, "status": state.get("status"), "wait_for": state.get("wait_for")})
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
    restored_from_park = location == "parked"
    if location == "parked":
        work = restore_parked_work(root, work)
        write_pointer(root, "current-work", work.name)
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
        if roles.get("image") not in {3, 4}:
            raise HarnessError("podcast_quote_image Final requires 3 or 4 image artifacts")
        if roles.get("contact_sheet") != 1 or roles.get("package") != 1:
            raise HarnessError("podcast_quote_image Final requires one contact sheet and one package")
        if len(artifacts) != roles["image"] + 2:
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


def assert_snapshot_source(project: Path) -> None:
    missing = [name for name in SNAPSHOT_ITEMS if not (project / name).exists()]
    if missing:
        raise HarnessError(f"Project snapshot is incomplete: {', '.join(missing)}")
    for name in SNAPSHOT_ITEMS:
        source = project / name
        if source.is_symlink():
            raise HarnessError(f"Snapshot source cannot be a symlink: {source}")
        if source.is_dir():
            for directory, names, files in os.walk(source):
                directory_path = Path(directory)
                for child in [*names, *files]:
                    if (directory_path / child).is_symlink():
                        raise HarnessError(f"Snapshot source cannot contain symlinks: {directory_path / child}")


def snapshot_digest(project: Path) -> str:
    digest = hashlib.sha256()
    for name in SNAPSHOT_ITEMS:
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


def copy_snapshot(project: Path, destination: Path) -> None:
    destination.mkdir(parents=True)
    for name in SNAPSHOT_ITEMS:
        source = project / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def assert_preview_ready(variant: Path, state: dict[str, Any]) -> None:
    script = read_frontmatter(variant / "SCRIPT.md")
    plan = read_frontmatter(variant / "ANIMATION_PLAN.md")
    if script.get("approval") == "pending":
        raise HarnessError("SCRIPT.md still requires approval")
    if script.get("revision") != state.get("script_revision"):
        raise HarnessError("SCRIPT.md revision does not match variant.yaml")
    if plan.get("status") != "approved":
        raise HarnessError("ANIMATION_PLAN.md is not approved")
    if plan.get("revision") != state.get("plan_revision"):
        raise HarnessError("ANIMATION_PLAN.md revision does not match variant.yaml")
    if plan.get("script_revision") != state.get("script_revision"):
        raise HarnessError("ANIMATION_PLAN.md targets a different Script revision")
    if plan.get("research_revision") is not None:
        research = read_frontmatter(variant / "RESEARCH.md")
        if research.get("status") != "ready":
            raise HarnessError("RESEARCH.md is not ready")
        if research.get("revision") != plan.get("research_revision"):
            raise HarnessError("ANIMATION_PLAN.md targets a different Research revision")
        if research.get("script_revision") != state.get("script_revision"):
            raise HarnessError("RESEARCH.md targets a different Script revision")


def preview_metadata(path: Path) -> dict[str, Any]:
    return read_frontmatter(path / "preview.md")


def command_preview_register(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    assert_preview_ready(variant, state)
    draft = Path(args.draft_file).expanduser().resolve()
    if not draft.is_file() or draft.stat().st_size == 0:
        raise HarnessError(f"Draft file is missing or empty: {draft}")
    project = variant / "project"
    assert_snapshot_source(project)
    draft_digest = file_sha256(draft)
    source_digest = snapshot_digest(project)
    previews = variant / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    existing = sorted(path for path in previews.glob("draft-v[0-9][0-9][0-9]") if path.is_dir())
    for path in existing:
        metadata = preview_metadata(path)
        if (
            metadata.get("draft_sha256") == draft_digest
            and metadata.get("snapshot_sha256") == source_digest
            and metadata.get("script_revision") == state.get("script_revision")
            and metadata.get("plan_revision") == state.get("plan_revision")
        ):
            print(path.name)
            return
    version = max((int(path.name.removeprefix("draft-v")) for path in existing), default=0) + 1
    draft_id = f"draft-v{version:03d}"
    staging = previews / f".{draft_id}.staging-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        shutil.copy2(draft, staging / "draft.mp4")
        copy_snapshot(project, staging / "source-snapshot")
        metadata = {
            "id": draft_id,
            "registered_at": now(),
            "draft_sha256": draft_digest,
            "snapshot_sha256": source_digest,
            "script_revision": state.get("script_revision"),
            "plan_revision": state.get("plan_revision"),
        }
        atomic_write(
            staging / "preview.md",
            "---\n" + json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n---\n\n# Preview\n",
        )
        os.replace(staging, previews / draft_id)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    state.update(status="waiting_user", wait_for="draft_feedback", next_action=f"Review {draft_id}")
    write_variant(variant, state)
    print(draft_id)


def command_preview_accept(root: Path, args: argparse.Namespace) -> None:
    work, _ = selected_work(root, args)
    require_workflow(work, "hyperframes_video")
    variant, state = selected_variant(root, work, args)
    draft_id = validate_id(args.draft_id, "draft id")
    preview = variant / "previews" / draft_id
    if not preview.is_dir() or not (preview / "draft.mp4").is_file() or not (preview / "source-snapshot").is_dir():
        raise HarnessError(f"Incomplete preview: {draft_id}")
    metadata = preview_metadata(preview)
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


def required_variants(work: Path) -> list[str]:
    values = read_frontmatter(work / "WORK.md").get("required_variants")
    if not isinstance(values, list) or not values or not all(isinstance(value, str) for value in values):
        raise HarnessError("WORK.md requires a non-empty required_variants list")
    return [validate_id(value, "required variant") for value in values]


def all_required_finals_exist(work: Path) -> bool:
    workflow = work_workflow(work)
    for variant_id in required_variants(work):
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
    destination = archive_destination(root, work.name)
    if destination.exists():
        raise HarnessError(f"Archive destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_json(work / ".runtime" / "archive.json", {"outcome": outcome, "archived_at": now()})
    os.replace(work, destination)
    return destination


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

    if all_required_finals_exist(work):
        write_json(
            variant / ".runtime" / "finalize.json",
            {"state": "archive_pending", "final_manifest_sha256": candidate_digest},
        )
        try:
            archived = move_to_archive(root, work, "completed")
        except (OSError, HarnessError) as exc:
            raise HarnessError(f"Final is safe but archive is pending: {exc}") from exc
        archived_variant = archived / "variants" / variant.name
        write_json(
            archived_variant / ".runtime" / "finalize.json",
            {"state": "complete", "final_manifest_sha256": candidate_digest},
        )
        clear_current_if(root, work.name)
        print(str(archived_variant / "final"))
        return
    print(str(final_dir))


def command_finalize(root: Path, args: argparse.Namespace) -> None:
    work, location = selected_work(root, args, allow_archive=True)
    if work_workflow(work) == "podcast_quote_image":
        command_finalize_package(root, args, work, location)
        return
    command_finalize_video(root, args, work, location)


def command_finalize_video(
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
        write_json(manifest_path, manifest)
        write_json(
            variant / ".runtime" / "qa" / "final.json",
            {"passed": True, "final_sha256": candidate_digest, "recorded_at": now()},
        )
    state.update(current_final="final.mp4", status="active", wait_for="none", next_action="Finalize complete")
    write_variant(variant, state)
    write_json(variant / ".runtime" / "finalize.json", {"state": "promoted", "final_sha256": candidate_digest})

    if all_required_finals_exist(work):
        write_json(variant / ".runtime" / "finalize.json", {"state": "archive_pending", "final_sha256": candidate_digest})
        try:
            archived = move_to_archive(root, work, "completed")
        except (OSError, HarnessError) as exc:
            raise HarnessError(f"Final is safe but archive is pending: {exc}") from exc
        archived_variant = archived / "variants" / variant.name
        write_json(archived_variant / ".runtime" / "finalize.json", {"state": "complete", "final_sha256": candidate_digest})
        clear_current_if(root, work.name)
        print(str(archived_variant / "final" / "final.mp4"))
        return
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
    if location == "active":
        write_pointer(root, "current-work", work.name)
        print(str(work))
        return
    if location == "parked":
        work = restore_parked_work(root, work)
    else:
        destination = works_root(root) / "active" / work.name
        if destination.exists():
            raise HarnessError(f"Active work already exists: {work.name}")
        archive_path = work / ".runtime" / "archive.json"
        archive_record = read_json(archive_path) if archive_path.is_file() else {}
        history_path = work / ".runtime" / "archive-history.json"
        history = read_json(history_path) if history_path.is_file() else {"entries": []}
        entries = history.get("entries", [])
        if not isinstance(entries, list):
            entries = []
        entries.append({**archive_record, "reopened_at": now()})
        write_json(history_path, {"entries": entries})
        archive_path.unlink(missing_ok=True)
        os.replace(work, destination)
        work = destination
        for variant in variant_paths(work):
            state = read_json(variant / "variant.yaml")
            state.update(status="active", wait_for="none", next_action="Continue from the retained Final and history")
            write_variant(variant, state)
    write_pointer(root, "current-work", work.name)
    variants = variant_paths(work)
    variant_id = "main" if (work / "variants" / "main").is_dir() else (variants[0].name if variants else None)
    if variant_id:
        write_pointer(root, "current-variant", variant_id)
    print(str(work))


def add_variant_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--template", choices=sorted(TEMPLATES))
    parser.add_argument("--profile", choices=sorted(PROFILES))
    parser.add_argument("--ratio", choices=sorted(RATIOS))
    parser.add_argument("--subject-position", choices=sorted(SUBJECT_POSITIONS))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="work", description="Local creative Work lifecycle")
    parser.add_argument("--work", dest="work_override", help="temporarily select a Work")
    parser.add_argument("--variant", dest="variant_override", help="temporarily select a Variant")
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new")
    new.add_argument("title")
    new.add_argument("--workflow", choices=sorted(WORKFLOWS), required=True)
    add_variant_options(new)
    new.set_defaults(handler=command_new)

    commands.add_parser("current").set_defaults(handler=command_current)
    commands.add_parser("list").set_defaults(handler=command_list)
    use = commands.add_parser("use")
    use.add_argument("work_id")
    use.set_defaults(handler=command_use)
    commands.add_parser("status").set_defaults(handler=command_status)

    variant = commands.add_parser("variant")
    variant_commands = variant.add_subparsers(dest="variant_command", required=True)
    variant_add = variant_commands.add_parser("add")
    variant_add.add_argument("variant_id")
    variant_add.add_argument("--from", dest="copy_from")
    add_variant_options(variant_add)
    variant_add.set_defaults(handler=command_variant_add)
    variant_use = variant_commands.add_parser("use")
    variant_use.add_argument("variant_id")
    variant_use.set_defaults(handler=command_variant_use)
    variant_commands.add_parser("list").set_defaults(handler=command_variant_list)

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
    preview_register.add_argument("draft_file")
    preview_register.set_defaults(handler=command_preview_register)
    preview_accept = preview_commands.add_parser("accept")
    preview_accept.add_argument("draft_id")
    preview_accept.set_defaults(handler=command_preview_accept)

    finalize = commands.add_parser("finalize")
    finalize.add_argument("final_file")
    finalize.add_argument("--qa-passed", action="store_true")
    finalize.set_defaults(handler=command_finalize)
    archive = commands.add_parser("archive")
    archive.add_argument("--outcome", required=True, choices=("abandoned", "superseded"))
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
        args.handler(target_root, args)
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
