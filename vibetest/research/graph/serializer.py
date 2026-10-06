"""JSON serialization and loading for behavior graphs."""
from __future__ import annotations

from pathlib import Path

from .models import BehaviorGraph


def save_graph(graph: BehaviorGraph, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(graph.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_graph(path: str | Path) -> BehaviorGraph:
    return BehaviorGraph.model_validate_json(Path(path).read_text(encoding="utf-8"))
