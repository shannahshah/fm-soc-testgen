from __future__ import annotations

from typing import Any, Callable, Dict, List, Sequence

JsonDict = Dict[str, Any]
JsonList = List[JsonDict]

PromptFn = Callable[[Sequence[JsonDict], int], JsonList]


class FmGenerator:
    """Foundation model based event generator."""

    def __init__(self, model: str, prompt_fn: PromptFn) -> None:
        self.model = model
        self.prompt_fn = prompt_fn

    def generate_from_seeds(self, seeds: Sequence[JsonDict], num: int) -> JsonList:
        if num <= 0:
            return []
        events = self.prompt_fn(seeds, num)
        return [ev for ev in events if isinstance(ev, dict)]


def echo_prompt_fn(seeds: Sequence[JsonDict], num: int) -> JsonList:
    """Placeholder FM — repeats seeds until num is reached."""
    if not seeds or num <= 0:
        return []
    out: JsonList = []
    i = 0
    while len(out) < num:
        out.append(dict(seeds[i % len(seeds)]))
        i += 1
    return out
