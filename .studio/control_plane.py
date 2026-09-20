"""WorkStore-local configuration; no credentials, server, or second database."""
from __future__ import annotations

from pathlib import Path
from typing import Any


class AccountService:
    def __init__(self, api: Any, root: Path):
        self.api, self.root = api, root
        self.directory = api.runtime_root(root) / "control-plane"

    def get(self, kind: str, identity: str) -> dict:
        if not isinstance(identity, str):
            raise self.api.HarnessError(f"Invalid {kind} identity")
        identity = self.api.validate_id(identity, kind)
        return self.api.read_json(self.directory / kind / f"{identity}.json")

    def put(self, kind: str, identity: str, data: dict) -> dict:
        identity = self.api.validate_id(identity, kind)
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            raise self.api.HarnessError("Configuration requires a name")
        allowed = {"account": {"name", "theme", "background", "motion", "overrides", "fps", "seed", "ratio", "mode", "style", "delivery"},
                   "series": {"name", "route", "accounts", "ip"},
                   "theme": {"name", "ratios", "modes", "tokens"}}[kind]
        if set(data) - allowed:
            raise self.api.HarnessError("Unsupported configuration fields")
        if kind == "theme":
            if not isinstance(data.get("ratios"), list) or not data["ratios"] or not all(isinstance(item, str) for item in data["ratios"]) or not set(data["ratios"]).issubset(self.api.RATIOS - {"source"}):
                raise self.api.HarnessError("Theme requires explicit supported ratios")
        if kind == "account":
            self.appearance(data)
        if kind == "series":
            if not isinstance(data.get("accounts", []), list):
                raise self.api.HarnessError("Series accounts must be a list")
            for account in data.get("accounts", []):
                self.get("account", account)
        self.api.runtime_root(self.root).mkdir(parents=True, exist_ok=True)
        with self.api.naming_lock(self.root):
            path = self.directory / kind / f"{identity}.json"
            previous = self.api.read_json(path) if path.exists() else {}
            record = {**data, "id": identity, "revision": previous.get("revision", 0) + 1}
            if previous:
                self.api.write_json(self.directory / kind / "history" / identity / f"{previous['revision']}.json", previous)
            self.api.write_json(path, record)
        return record

    def appearance(self, settings: dict) -> dict:
        from appearance import is_asset_appearance, resolve
        from component_harness import ComponentError
        if is_asset_appearance(settings):
            try:
                return resolve(self.root, settings)
            except (ValueError, ComponentError) as error:
                raise self.api.HarnessError(str(error)) from error
        if any(key in settings for key in ("background", "overrides")):
            raise self.api.HarnessError("Background and overrides require exact appearance asset references")
        if settings.get("mode") not in (None, "text-led", "animation-led"):
            raise self.api.HarnessError("Unknown narrative mode")
        if settings.get("ratio") not in (None, *self.api.RATIOS):
            raise self.api.HarnessError("Unknown ratio")
        if settings.get("theme"):
            theme = self.get("theme", settings["theme"])
            if settings.get("ratio") and settings["ratio"] not in theme["ratios"]:
                raise self.api.HarnessError("Theme does not support the requested ratio")
            return theme
        return {}


def input_path(api: Any, directory: Path, name: str) -> Path:
    state_path = directory / "variant.yaml"
    if state_path.is_file():
        refs = api.read_json(state_path).get("shared_inputs", {})
        if not isinstance(refs, dict):
            raise api.HarnessError("shared_inputs must be an object")
        if name in refs:
            work = directory.parent.parent.resolve()
            if not isinstance(refs[name], str):
                raise api.HarnessError("Invalid shared input path")
            candidate = work / refs[name]
            path = candidate.resolve()
            if not path.is_relative_to(work) or any(p.is_symlink() for p in (candidate, *candidate.parents) if p.is_relative_to(work)):
                raise api.HarnessError("Shared input escapes Work")
            return path
    return directory / name
