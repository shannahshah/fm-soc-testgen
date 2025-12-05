from __future__ import annotations

import copy
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence, Mapping

import yaml

JsonDict = Dict[str, Any]
JsonList = List[JsonDict]


def _parse_iso8601(value: str) -> datetime | None:
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _format_iso8601(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def perturb_timestamp_drift(events: JsonList, field="@timestamp", max_offset_minutes=30) -> JsonList:
    out: JsonList = []
    for ev in events:
        ev_copy = copy.deepcopy(ev)
        raw = ev_copy.get(field)
        dt = _parse_iso8601(raw) if isinstance(raw, str) else None

        if dt:
            offset = random.randint(-max_offset_minutes, max_offset_minutes)
            ev_copy[field] = _format_iso8601(dt + timedelta(minutes=offset))

        out.append(ev_copy)
    return out


def perturb_identity_shift(events: JsonList, fields=("user", "username", "account"), suffix_pool=("_lab", "_srv", "_ext")) -> JsonList:
    out: JsonList = []
    for ev in events:
        ev_copy = copy.deepcopy(ev)
        for f in fields:
            val = ev_copy.get(f)
            if isinstance(val, str):
                suffix = random.choice(suffix_pool)
                ev_copy[f] = val + suffix
        out.append(ev_copy)
    return out


PERTURBATIONS = {
    "timestamp_drift": perturb_timestamp_drift,
    "identity_shift": perturb_identity_shift,
}


@dataclass
class ScenarioResult:
    events: JsonList
    name: str
    perturbations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def to_manifest(self, path: str | Path) -> None:
        manifest = {
            "scenario": self.name,
            "num_events": len(self.events),
            "perturbations": self.perturbations,
            "metadata": self.metadata,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)


class ScenarioRunner:
    def __init__(self, schema_path: str | None = None) -> None:
        self.schema_path = schema_path

    def run(self, events: Sequence[JsonDict], perturbations: Sequence[str], name="scenario", params=None) -> ScenarioResult:
        params = params or {}
        current = [copy.deepcopy(e) for e in events]

        for p_name in perturbations:
            fn = PERTURBATIONS[p_name]
            kwargs = params.get(p_name, {})
            current = fn(current, **kwargs)

        return ScenarioResult(events=current, name=name, perturbations=list(perturbations))


def run_scenario_from_yaml(events: JsonList, yaml_path: str | Path, schema_path=None) -> ScenarioResult:
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    name = raw.get("name", "scenario")
    steps = raw.get("perturbations", [])

    perturbation_names = [s["name"] for s in steps]
    params = {s["name"]: s.get("params", {}) for s in steps}

    runner = ScenarioRunner(schema_path=schema_path)
    result = runner.run(events, perturbation_names, name=name, params=params)

    result.metadata["yaml_path"] = str(yaml_path)
    result.metadata["description"] = raw.get("description", "")

    return result
