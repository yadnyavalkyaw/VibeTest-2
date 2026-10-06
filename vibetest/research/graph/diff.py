"""Compare graph facts across versions; version membership is metadata, not drift."""
from __future__ import annotations

from ..behavior.models import BehaviorProfile
from .builder import build_graph
from .models import GraphDelta


def _node_key(graph, identifier: str) -> tuple[str, str]:
    node = next(n for n in graph.nodes if n.id == identifier)
    return node.kind, node.key


def _semantic_edges(graph) -> dict[tuple, object]:
    facts = {}
    for edge in graph.edges:
        if edge.predicate in {"HAS_VERSION", "CONTAINS_CASE"}:
            continue
        key = (
            *_node_key(graph, edge.source),
            edge.predicate,
            *_node_key(graph, edge.target),
            tuple(sorted(edge.attributes.items())),
        )
        facts[key] = edge
    return facts


def diff_profiles(baseline: BehaviorProfile, current: BehaviorProfile) -> GraphDelta:
    if baseline.application_id != current.application_id:
        raise ValueError("profiles must belong to the same application")
    old_graph, new_graph = build_graph(baseline), build_graph(current)
    old_facts, new_facts = _semantic_edges(old_graph), _semantic_edges(new_graph)
    old_nodes = {(n.kind, n.key): n for n in old_graph.nodes if n.kind not in {"version"}}
    new_nodes = {(n.kind, n.key): n for n in new_graph.nodes if n.kind not in {"version"}}
    return GraphDelta(
        application_id=baseline.application_id,
        baseline_version=baseline.version_id,
        current_version=current.version_id,
        added_edges=[new_facts[key] for key in sorted(new_facts.keys() - old_facts.keys())],
        removed_edges=[old_facts[key] for key in sorted(old_facts.keys() - new_facts.keys())],
        added_nodes=[new_nodes[key] for key in sorted(new_nodes.keys() - old_nodes.keys())],
        removed_nodes=[old_nodes[key] for key in sorted(old_nodes.keys() - new_nodes.keys())],
    )
