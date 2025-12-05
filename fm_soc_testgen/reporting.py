from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

JsonDict = Dict[str, Any]
JsonList = List[JsonDict]


def basic_report(events: JsonList, timestamp_field="@timestamp", id_field="event_id") -> Dict[str, Any]:
    num = len(events)
    missing_ts = sum(1 for e in events if timestamp_field not in e)
    event_ids = Counter(str(e.get(id_field)) for e in events if e.get(id_field) is not None)

    sample = events[:3]

    return {
        "num_events": num,
        "missing_timestamps": missing_ts,
        "unique_event_ids": len(event_ids),
        "top_event_ids": event_ids.most_common(5),
        "sample_events": sample,
    }
