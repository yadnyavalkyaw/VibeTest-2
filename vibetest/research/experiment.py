"""Reproducible summary for an offline imported-observation experiment."""
from __future__ import annotations

from time import perf_counter

from pydantic import BaseModel, Field

from .behavior.comparator import BehaviorComparison, compare_profiles, verify_candidates
from .behavior.models import BehaviorProfile, VerificationStatus
from .graph.diff import diff_profiles
from .graph.models import GraphDelta
from .graph.builder import build_graph


class ExperimentResult(BaseModel):
    schema_version: str = "1"
    application_id: str
    baseline_version: str
    compared_version: str
    baseline_observations: int
    compared_observations: int
    graph_nodes: int
    graph_edges: int
    changed_authorization_relationships: int
    drift_candidates: int
    verified_regressions: int
    false_positives: int | None = None
    false_negatives: int | None = None
    execution_time_seconds: float
    request_count: int = 0
    comparison: BehaviorComparison
    graph_delta: GraphDelta
    notes: list[str] = Field(default_factory=lambda: [
        "Observations were imported; VibeTest made zero requests and used no credentials.",
        "Verification status reflects supplied observations and does not attest collection independence.",
    ])


def run_imported_experiment(
    baseline: BehaviorProfile,
    current: BehaviorProfile,
    verification: BehaviorProfile | None = None,
    *,
    ground_truth: dict[str, bool] | None = None,
) -> ExperimentResult:
    started = perf_counter()
    comparison = compare_profiles(baseline, current)
    if verification is not None:
        comparison = verify_candidates(comparison, verification)
    delta = diff_profiles(baseline, current)
    graph = build_graph(current)
    true_positive = false_positive = false_negative = None
    if ground_truth is not None:
        if any(type(value) is not bool for value in ground_truth.values()):
            raise ValueError("ground truth values must be booleans")
        predicted = {
            change.case_id
            for change in comparison.regression_candidates
            if change.verification is not None and change.verification.status is VerificationStatus.VERIFIED
        }
        expected = {case_id for case_id, is_regression in ground_truth.items() if is_regression}
        true_positive = len(predicted & expected)
        false_positive = len(predicted - expected)
        false_negative = len(expected - predicted)
    return ExperimentResult(
        application_id=baseline.application_id,
        baseline_version=baseline.version_id,
        compared_version=current.version_id,
        baseline_observations=len(baseline.observations),
        compared_observations=len(current.observations),
        graph_nodes=len(graph.nodes),
        graph_edges=len(graph.edges),
        changed_authorization_relationships=sum(
            1 for edge in delta.added_edges + delta.removed_edges
            if edge.predicate in {
                "HAS_ROLE", "ACTION", "ON_RESOURCE", "AT_ENDPOINT", "EXPECTED",
                "OBSERVED", "OWNED_BY", "REQUIRES_CONDITION", "IN_STATE",
            }
        ),
        drift_candidates=len(comparison.regression_candidates),
        verified_regressions=sum(
            1 for change in comparison.regression_candidates
            if change.verification is not None and change.verification.status is VerificationStatus.VERIFIED
        ),
        false_positives=false_positive,
        false_negatives=false_negative,
        execution_time_seconds=round(perf_counter() - started, 6),
        request_count=0,
        comparison=comparison,
        graph_delta=delta,
    )
