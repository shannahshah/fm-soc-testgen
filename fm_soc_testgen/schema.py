from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft7Validator

JsonDict = Dict[str, Any]
JsonList = List[JsonDict]


class SchemaValidator:
    """Validate events against a JSON schema."""

    def __init__(self, schema_path: str | Path) -> None:
        p = Path(schema_path)
        with p.open("r", encoding="utf-8") as f:
            schema = json.load(f)

        self.schema = schema
        self.validator = Draft7Validator(schema)

    def validate(self, events: JsonList) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []
        for idx, event in enumerate(events):
            for err in self.validator.iter_errors(event):
                errors.append(
                    {
                        "index": idx,
                        "message": err.message,
                        "path": ".".join(str(p) for p in err.path),
                    }
                )
        return errors

    def assert_valid(self, events: JsonList) -> None:
        errs = self.validate(events)
        if errs:
            raise ValueError(f"Schema validation failed: {errs[0]}")
