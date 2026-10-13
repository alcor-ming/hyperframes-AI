"""Read-only card -> referenced asset -> account -> Work relation report.

Source availability and frozen-copy integrity are reported separately: a source
that is missing, changed or behind an unconfigured legacy AssetStore never marks
an existing Variant's frozen vendor closure as damaged. Nothing here writes
caches, indexes, Work state or card files.
"""
from __future__ import annotations

import json
from pathlib import Path

import asset_store
import designs
from component_harness import ComponentError, validate_component_acceptance, validate_component_release

SOURCE_ERRORS = (ComponentError, designs.DesignError, OSError, ValueError, KeyError, TypeError)


def source_status(root: Path, ref: str, package_sha256: str | None, card_ref: str | None = None,
                  *, legacy: bool = False) -> dict:
    """Current source of one exact reference: available, changed, missing, not-accepted or store-unconfigured.

    Routing follows the appearance resolver ('/' means a card asset) unless an installed lock record
    already says which side owns the reference.
    """
    identity = ref.rsplit("@v", 1)[0]
    if card_ref is None and not legacy and "/" in identity:
        card_ref = identity
    if card_ref:
        try:
            _, item = asset_store.card_asset_reference(root, card_ref)
        except SOURCE_ERRORS as error:
            return {"origin": "card", "source": "missing", "error": str(error)}
        current = {"current_ref": item["ref"], "current_sha256": item["package_sha256"], "path": item["path"]}
        same = item["ref"] == ref and item["package_sha256"] == package_sha256
        return {"origin": "card", "source": "available" if same else "changed", **current}
    try:
        store = asset_store.asset_store_root(root)
    except ComponentError as error:
        return {"origin": "legacy-store", "source": "store-unconfigured", "error": str(error)}
    try:
        relative = asset_store._relative(ref)
        package = store / "packages" / relative
        record = store / "acceptances" / relative / "acceptance.json"
        if not package.is_dir() and (store / "candidates" / relative).exists():
            return {"origin": "legacy-store", "source": "not-accepted", "store": str(store)}
        if not package.is_dir():
            return {"origin": "legacy-store", "source": "missing", "store": str(store),
                    "error": f"Legacy AssetStore package is missing: {ref}"}
        report = asset_store._validate_package(package, ref)
    except SOURCE_ERRORS as error:
        return {"origin": "legacy-store", "source": "invalid", "store": str(store), "error": str(error)}
    if not record.is_file():
        return {"origin": "legacy-store", "source": "not-accepted", "store": str(store), "path": str(package)}
    try:
        validate_component_acceptance(json.loads(record.read_text(encoding="utf-8")), report, runtime_root=root)
    except SOURCE_ERRORS as error:
        return {"origin": "legacy-store", "source": "not-accepted", "store": str(store), "error": str(error)}
    same = package_sha256 is None or report["package_sha256"] == package_sha256
    return {"origin": "legacy-store", "source": "available" if same else "changed", "store": str(store),
            "path": str(package), "current_sha256": report["package_sha256"]}


def _frozen(project: Path, record: dict) -> dict:
    vendor = project / str(record.get("vendor_path", ""))
    try:
        if not vendor.resolve().is_relative_to(project.resolve()) or not vendor.is_dir():
            return {"frozen": "damaged", "error": f"Vendor copy is missing: {record.get('vendor_path')}"}
        release = validate_component_release(vendor, expected_ref=record["component_ref"], allow_unapproved=True)
    except SOURCE_ERRORS as error:
        return {"frozen": "damaged", "error": str(error)}
    if release["package_sha256"] != record.get("work_package_sha256"):
        return {"frozen": "damaged", "error": "Vendor copy differs from COMPONENT_LOCK.json"}
    return {"frozen": "intact"}


def _relation(frozen: str, source: str) -> str:
    if frozen == "damaged":
        return "frozen-damaged"
    if frozen == "not-installed":
        return "not-installed" if source == "available" else "not-installed-source-" + source
    if source == "available":
        return "in-sync"
    if source == "changed":
        return "older-frozen-copy"
    return "frozen-intact-source-" + source


def variant_report(root: Path, variant: Path) -> dict:
    state = json.loads((variant / "variant.yaml").read_text(encoding="utf-8"))
    project = variant / "project"
    lock_path = project / "COMPONENT_LOCK.json"
    try:
        records = json.loads(lock_path.read_text(encoding="utf-8")).get("components", []) if lock_path.is_file() else []
    except (OSError, ValueError) as error:
        records = []
        lock_error = str(error)
    else:
        lock_error = None
    installed = {record.get("component_ref"): record for record in records if isinstance(record, dict)}
    wanted = {item["ref"]: item for item in (state.get("appearance_lock") or {}).get("assets", [])}
    assets = []
    for ref in sorted(set(installed) | set(wanted)):
        record = installed.get(ref)
        expected = (record or {}).get("work_package_sha256") or wanted[ref]["package_sha256"]
        frozen = _frozen(project, record) if record else {"frozen": "not-installed"}
        source = source_status(root, ref, expected, (record or {}).get("card_ref"),
                               legacy=bool(record) and not record.get("card_ref"))
        assets.append({"ref": ref, "kind": (record or {}).get("asset_kind") or wanted.get(ref, {}).get("kind"),
                       "role": "appearance" if ref in wanted else "component", **frozen,
                       "source_status": source, "relation": _relation(frozen["frozen"], source["source"])})
    report = {"variant": variant.name, "design": state.get("design"), "account": state.get("account"),
              "assets": assets}
    if lock_error:
        report["lock_error"] = lock_error
    receipt = state.get("design_files")
    if receipt:
        report["design_snapshot"] = _snapshot_report(variant, receipt)
    elif state.get("design_live") and state.get("design"):
        try:
            designs.require(state["design"])
            report["design_snapshot"] = {"frozen": "live-card", "source": "available"}
        except SOURCE_ERRORS as error:
            report["design_snapshot"] = {"frozen": "live-card", "source": "missing", "error": str(error)}
    damaged = [item["ref"] for item in assets if item["frozen"] == "damaged"]
    if report.get("design_snapshot", {}).get("frozen") == "damaged":
        damaged.append("design-snapshot")
    report["frozen_closure"] = "damaged" if damaged or lock_error else "intact"
    report["not_installed"] = [item["ref"] for item in assets if item["frozen"] == "not-installed"]
    return report


def _snapshot_report(variant: Path, receipt: dict) -> dict:
    import design_snapshot
    result = {}
    try:
        design_snapshot.verify(variant / receipt["path"], receipt)
        result["frozen"] = "intact"
    except SOURCE_ERRORS as error:
        result.update(frozen="damaged", frozen_error=str(error))
    try:
        changes = design_snapshot.changes(receipt)
    except SOURCE_ERRORS as error:
        result.update(source="missing", error=str(error))
        return result
    result["source"] = "changed" if changes["files"] or changes["references"] else "available"
    if result["source"] == "changed":
        result.update(changed_files=changes["files"], changed_references=changes["references"],
                      reinstall_assets=changes["reinstall_assets"])
    return result


def account_report(root: Path, account_id: str, account: dict, design: str | None = None) -> dict:
    rows = []
    for kind in ("theme", "background"):
        value = account.get(kind)
        if isinstance(value, dict):
            rows.append((kind, value))
        elif isinstance(value, str):
            rows.append((kind, {"settings_theme": value}))
    for slot, value in sorted((account.get("motion") or {}).items()):
        if isinstance(value, dict) and isinstance(value.get("asset"), dict):
            rows.append((f"motion.{slot}", value["asset"]))
    card = None
    if design:
        try:
            card = designs.require(design)
        except SOURCE_ERRORS as error:
            return {"account": account_id, "error": str(error), "bindings": []}
    bindings = []
    for slot, reference in rows:
        if "settings_theme" in reference:
            bindings.append({"slot": slot, "ref": reference["settings_theme"], "origin": "control-plane-theme",
                             "source_status": {"source": "settings", "note": "pre-asset settings theme; not a card or AssetStore asset"}})
            continue
        ref = reference.get("ref")
        if not isinstance(ref, str):
            bindings.append({"slot": slot, "source_status": {"source": "invalid", "error": "Account binding lacks an exact ref"}})
            continue
        row = {"slot": slot, "ref": ref, "source_status": source_status(root, ref, reference.get("package_sha256"))}
        identity = ref.rsplit("@v", 1)[0]
        if card is not None and "/" in identity:
            row["selected_card_scope"] = (identity.split("/")[0] == card["id"]
                                          or identity in card.get("references", []))
        bindings.append(row)
    return {"account": account_id, "revision": account.get("revision"), "bindings": bindings}


def design_report(root: Path, design: str) -> dict:
    result = asset_store.discover_components(root, design=design, audit=True)
    card_dir = designs.card_path(design, root=root)
    return {"design": design,
            "assets": [{key: row.get(key) for key in ("component_ref", "origin", "asset_type", "path", "usable_by")}
                       for row in result["assets"]],
            "errors": [item for item in result["errors"] if Path(item["path"]).is_relative_to(card_dir)]}
