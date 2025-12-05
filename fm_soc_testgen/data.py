from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

JsonDict = Dict[str, Any]
JsonList = List[JsonDict]


class JsonLoader:
    """Load JSON and NDJSON logs."""

    @staticmethod
    def load(path: str | Path) -> JsonList:
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]

        raise ValueError(f"Unsupported JSON format: {path}")

    @staticmethod
    def load_ndjson(path: str | Path) -> JsonList:
        events: JsonList = []
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if isinstance(obj, dict):
                    events.append(obj)
        return events
