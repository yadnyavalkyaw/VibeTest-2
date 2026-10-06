"""Build a purposeful JSON graph from imported behavior observations."""
from __future__ import annotations

import json
from hashlib import sha256

from .models import BehaviorGraph, GraphEdge, GraphNode, stable_id
from ..behavior.models import BehaviorProfile


def build_graph(profile: BehaviorProfile) -> BehaviorGraph:
    nodes: dict[str, GraphNode] = {}
    edges: dict[str, GraphEdge] = {}

    def node(kind: str, key: str, label: str, **attributes: str) -> str:
        identifier = stable_id(kind, key)
        nodes.setdefault(identifier, GraphNode(id=identifier, kind=kind, key=key, label=label, attributes=attributes))
        return identifier

    def edge(source: str, predicate: str, target: str, **attributes: str) -> None:
        key = f"{source}\0{predicate}\0{target}"
        identifier = stable_id("edge", key)
        edges.setdefault(identifier, GraphEdge(id=identifier, source=source, predicate=predicate, target=target, attributes=attributes))

    app = node("application", profile.application_id, profile.application_id)
    version = node("version", f"{profile.application_id}@{profile.version_id}", profile.version_id,
                   source_version=profile.source_version or "", source_ref=profile.source_ref or "")
    edge(app, "HAS_VERSION", version)

    for obs in profile.observations:
        case = node("case", obs.case_id, obs.case_id, application_state=obs.application_state)
        edge(version, "CONTAINS_CASE", case)
        principal = node("principal", obs.principal_id, obs.principal_label or obs.principal_id)
        action = node("action", obs.action.casefold(), obs.action)
        resource = node("resource", obs.resource, obs.resource)
        endpoint = node("endpoint", f"{obs.method.upper()} {obs.endpoint}", f"{obs.method.upper()} {obs.endpoint}")
        role = node("role", obs.role, obs.role) if obs.role else None
        expected = node("outcome", obs.expected.value, obs.expected.value)
        observed = node("outcome", obs.observed.value, obs.observed.value)
        edge(case, "PRINCIPAL", principal)
        if role:
            edge(principal, "HAS_ROLE", role)
        edge(case, "ACTION", action)
        edge(action, "ON_RESOURCE", resource)
        edge(resource, "AT_ENDPOINT", endpoint)
        edge(case, "EXPECTED", expected)
        edge(case, "OBSERVED", observed, status_code=str(obs.response.status_code or ""))
        if obs.authorization_condition:
            condition = node("authorization_condition", obs.authorization_condition, obs.authorization_condition,
                             policy_source=obs.policy_source or "unspecified")
            edge(case, "REQUIRES_CONDITION", condition)
        if obs.resource_owner_id:
            owner = node("principal", obs.resource_owner_id, obs.resource_owner_id)
            edge(resource, "OWNED_BY", owner)
        state = node("state", obs.application_state, obs.application_state)
        edge(case, "IN_STATE", state)
        evidence_facts = {
            "status_code": str(obs.response.status_code or ""),
            "redirect_to": obs.response.redirect_to or "",
            "body_sha256": obs.response.body_sha256 or "",
            "indicators": ",".join(obs.response.indicators),
            "evidence_ref": obs.response.evidence_ref or "",
        }
        if any(evidence_facts.values()):
            evidence_key = obs.response.evidence_ref or sha256(
                json.dumps(evidence_facts, sort_keys=True).encode("utf-8")
            ).hexdigest()
            evidence = node("evidence", evidence_key, "response evidence", **evidence_facts)
            edge(case, "SUPPORTED_BY", evidence)

    return BehaviorGraph(
        application_id=profile.application_id,
        version_id=profile.version_id,
        profile_id=profile.profile_id,
        nodes=sorted(nodes.values(), key=lambda item: item.id),
        edges=sorted(edges.values(), key=lambda item: item.id),
    )
