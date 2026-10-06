"""Typed in-memory graph models for behavior profiles."""
from __future__ import annotations

from hashlib import sha256

from pydantic import BaseModel, Field


def stable_id(kind: str, key: str) -> str:
    digest = sha256(f"{kind}\0{key}".encode("utf-8")).hexdigest()[:20]
    return f"{kind}:{digest}"


class GraphNode(BaseModel):
    id: str
    kind: str
    key: str
    label: str
    attributes: dict[str, str] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    predicate: str
    target: str
    attributes: dict[str, str] = Field(default_factory=dict)


class BehaviorGraph(BaseModel):
    schema_version: str = "1"
    application_id: str
    version_id: str
    profile_id: str
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class GraphDelta(BaseModel):
    application_id: str
    baseline_version: str
    current_version: str
    added_edges: list[GraphEdge] = Field(default_factory=list)
    removed_edges: list[GraphEdge] = Field(default_factory=list)
    added_nodes: list[GraphNode] = Field(default_factory=list)
    removed_nodes: list[GraphNode] = Field(default_factory=list)
