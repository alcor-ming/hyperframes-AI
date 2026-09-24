"""Small, explicit-root research register. Documents remain the only content source."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

from component_harness import ComponentError, _atomic_json, _read_json, file_sha256, package_write_lock


def _validate_metadata(row):
    if row.get("kind") not in ("tool", "asset") or not isinstance(row.get("title"), str) or not row["title"].strip():
        raise ComponentError("Research requires kind tool/asset and a title")
    if not isinstance(row.get("path"), (str, Path)) or not str(row["path"]).strip():
        raise ComponentError("Research path must be a nonempty path")
    if not isinstance(row.get("topics", []), list) or not all(isinstance(t, str) for t in row.get("topics", [])):
        raise ComponentError("Research topics must be strings")
    if row.get("summary") is not None and not isinstance(row["summary"], str):
        raise ComponentError("Research summary must be text or null")
    if not isinstance(row.get("status", "researching"), str) or not row.get("status", "researching").strip():
        raise ComponentError("Research status must be nonempty text")
    links = row.get("links", [])
    if not isinstance(links, list):
        raise ComponentError("Research links must be a list")
    for link in links:
        if not isinstance(link, dict) or not isinstance(link.get("target"), str) or not link["target"].strip():
            raise ComponentError("Research links require a nonempty target")
        if "path" in link and (not isinstance(link["path"], str) or not Path(link["path"]).is_absolute()):
            raise ComponentError("Research link path must be absolute")


def _index(root):
    return Path(root).resolve() / "research-index.json"


def _load(root):
    path = _index(root)
    return _read_json(path) if path.exists() else {"schema_version": 1, "documents": {}}


def _view(record):
    result = dict(record)
    path = Path(record["path"])
    digest = file_sha256(path) if path.is_file() else None
    result["missing"] = digest is None
    result["current_sha256"] = digest
    result["unsynchronized"] = digest != record["sha256"]
    result["summary_stale"] = bool(record.get("summary")) and digest != record.get("summary_sha256")
    if result["summary_stale"]:
        result["summary"] = None
    result["invalid_links"] = [link for link in record.get("links", [])
                               if link.get("path") and not Path(link["path"]).exists()]
    result["reference_only"] = True
    return result


def query(root, query="", *, kind=None, related=None):
    rows = [_view(row) for row in _load(root)["documents"].values()]
    return {"documents": [row for row in rows if (not kind or row["kind"] == kind)
            and (not related or any(related == link["target"] for link in row.get("links", [])))
            and query.casefold() in json.dumps(row, ensure_ascii=False).casefold()]}


def register(root, path, *, kind, title, summary=None, topics=None):
    _validate_metadata({"kind": kind, "title": title, "path": path, "summary": summary,
                        "topics": [] if topics is None else topics})
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ComponentError("Research document does not exist")
    with package_write_lock(_index(root).with_suffix(".lock")):
        data = _load(root)
        for row in data["documents"].values():
            if row["path"] == str(path):
                return _view(row)
        identity = "research-" + uuid.uuid4().hex
        digest = file_sha256(path)
        row = {"id": identity, "title": title, "kind": kind, "path": str(path),
               "revision": 1, "sha256": digest, "updated_at": datetime.now(timezone.utc).isoformat(),
               "topics": topics or [], "status": "researching", "links": [], "references": []}
        if summary is not None:
            row.update(summary=summary, summary_sha256=digest)
        data["documents"][identity] = row
        _atomic_json(_index(root), data)
        return _view(row)


def create(root, *, kind, title, text=""):
    _validate_metadata({"kind": kind, "title": title, "path": "new.md"})
    if not isinstance(text, str):
        raise ComponentError("Research text must be a string")
    directory = Path(root).resolve() / kind
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (uuid.uuid4().hex + ".md")
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text or f"# {title}\n")
    # An index failure deliberately leaves the new document available for retry.
    try:
        return register(root, path, kind=kind, title=title)
    except (ComponentError, OSError) as error:
        raise ComponentError(f"Research index not synchronized; document retained at {path}: {error}") from error


def update(root, identity, *, expected_revision, changes=None, sync=False, reference=None, expected_sha256=None):
    changes = {} if changes is None else changes
    if not isinstance(changes, dict):
        raise ComponentError("Research metadata must be an object")
    if not isinstance(identity, str) or type(expected_revision) is not int:
        raise ComponentError("Research requires an ID and integer revision")
    if reference is not None and (not isinstance(reference, str) or not reference.strip()):
        raise ComponentError("Research reference target must be nonempty text")
    if set(changes) - {"title", "kind", "path", "topics", "status", "summary", "links"}:
        raise ComponentError("Unsupported research metadata field")
    with package_write_lock(_index(root).with_suffix(".lock")):
        data = _load(root)
        if identity not in data["documents"]:
            raise ComponentError("Unknown research ID")
        row = dict(data["documents"][identity])
        if row["revision"] != expected_revision:
            raise ComponentError("Research revision conflict; query again before updating")
        row.update(changes)
        _validate_metadata(row)
        path = Path(row["path"]).expanduser().resolve()
        row["path"] = str(path)
        if any(other["id"] != identity and other["path"] == str(path) for other in data["documents"].values()):
            raise ComponentError("Research path is already registered")
        if sync or "path" in changes or "summary" in changes or reference:
            if not path.is_file():
                raise ComponentError("Research document missing; index not synchronized")
            digest = file_sha256(path)
            expected = expected_sha256 or (row["sha256"] if "summary" in changes else None)
            if expected is not None and digest != expected:
                raise ComponentError("Research document changed; read the current body and supply its sha256")
            row["sha256"] = digest
        if "summary" in changes:
            row["summary_sha256"] = row["sha256"]
        if reference:
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != row["sha256"]:
                raise ComponentError("Research changed while recording reference; retry")
            snapshot = _index(root).parent / "references" / identity / f"{row['sha256']}.md"
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            if snapshot.exists():
                if snapshot.is_symlink() or snapshot.read_bytes() != content:
                    raise ComponentError("Research reference snapshot conflict")
            else:
                with tempfile.TemporaryDirectory(prefix=".reference-", dir=snapshot.parent) as staging:
                    temporary = Path(staging) / "document.md"
                    temporary.write_bytes(content)
                    os.replace(temporary, snapshot)
            row["references"] = [*row["references"], {"target": reference, "path": str(path),
                "snapshot_path": str(snapshot), "revision": row["revision"] + 1, "sha256": row["sha256"]}]
        row["revision"] += 1
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
        data["documents"][identity] = row
        _atomic_json(_index(root), data)
        return _view(row)


def register_cli(commands, api=None):
    parser = commands.add_parser("research", help="Explicit-root research document register")
    parser.add_argument("--root", required=True)
    sub = parser.add_subparsers(dest="research_command", required=True)
    for name in ("create", "register"):
        child = sub.add_parser(name)
        child.add_argument("--kind", choices=("tool", "asset"), required=True)
        child.add_argument("--title", required=True)
        child.add_argument("--path" if name == "register" else "--text", required=name == "register", default="")
    child = sub.add_parser("query")
    child.add_argument("query", nargs="?", default="")
    child.add_argument("--kind", choices=("tool", "asset"))
    child.add_argument("--related")
    for name in ("update", "sync", "link", "reference"):
        child = sub.add_parser(name)
        child.add_argument("id")
        child.add_argument("--revision", type=int, required=True)
        child.add_argument("--sha256", help="Expected current document hash when updating a summary")
        if name == "update":
            child.add_argument("--metadata", required=True, help="JSON metadata object")
        if name in {"link", "reference"}:
            child.add_argument("target")
        if name == "link":
            child.add_argument("--path")
    parser.set_defaults(handler=cli)


def cli(root, args):
    command = args.research_command
    if command == "query":
        result = query(args.root, args.query, kind=args.kind, related=args.related)
    elif command == "create":
        result = create(args.root, kind=args.kind, title=args.title, text=args.text)
    elif command == "register":
        result = register(args.root, args.path, kind=args.kind, title=args.title)
    else:
        try:
            changes = json.loads(args.metadata) if command == "update" else {}
        except ValueError as error:
            raise ComponentError(f"Invalid research metadata JSON: {error}") from error
        if command == "link":
            row = _load(args.root)["documents"].get(args.id)
            if row is None:
                raise ComponentError("Unknown research ID")
            changes["links"] = [*row["links"], {"target": args.target, **({"path": args.path} if args.path else {})}]
        result = update(args.root, args.id, expected_revision=args.revision, changes=changes,
                        sync=command == "sync", reference=args.target if command == "reference" else None,
                        expected_sha256=args.sha256)
    print(json.dumps(result, ensure_ascii=False, indent=2))
