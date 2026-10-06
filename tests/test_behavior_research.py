"""Offline behavior research tests; none of these tests contacts a target."""
from pathlib import Path

import pytest

from vibetest.research.behavior.baseline import import_observations, load_observations
from vibetest.research.behavior.comparator import DriftKind, compare_profiles, verify_candidates
from vibetest.research.behavior.models import (
    AuthorizationOutcome,
    OutcomeClassifier,
    OutcomeRule,
    ResponseEvidence,
    VerificationStatus,
)
from vibetest.research.experiment import run_imported_experiment
from vibetest.research.graph.builder import build_graph
from vibetest.research.graph.diff import diff_profiles

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "eval" / "behavior"


def _profiles():
    return (
        load_observations(FIXTURES / "minishop_v0.json"),
        load_observations(FIXTURES / "minishop_v1.json"),
        load_observations(FIXTURES / "minishop_verification.json"),
    )


def test_baseline_import_is_versioned_and_round_trips():
    profile = load_observations(FIXTURES / "minishop_v0.json")
    restored = type(profile).model_validate_json(profile.model_dump_json())
    assert restored.profile_id == profile.profile_id
    assert restored.version_id == "v0"
    assert len(restored.observations) == 8
    assert profile.profile_id.startswith("profile-")


def test_response_classifier_uses_configured_rules_and_ambiguous_is_unknown():
    classifier = OutcomeClassifier(rules=[
        OutcomeRule(outcome="denied", status_codes={302}, redirect_contains=["/login"]),
        OutcomeRule(outcome="allowed", status_codes={200}, indicator_contains=["private-data"]),
    ])
    assert classifier.classify(ResponseEvidence(status_code=302, redirect_to="/login")) is AuthorizationOutcome.DENIED
    assert classifier.classify(ResponseEvidence(status_code=200, indicators=["private-data-present"])) is AuthorizationOutcome.ALLOWED
    assert classifier.classify(ResponseEvidence(status_code=200)) is AuthorizationOutcome.UNKNOWN


def test_malformed_and_duplicate_observations_are_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        import_observations({"application_id": "app", "version_id": "v0", "observations": []})
    base = {"case_id": "same", "principal_id": "a", "action": "read", "resource": "r", "endpoint": "/r", "method": "GET"}
    data = {"application_id": "app", "version_id": "v0", "observations": [base, base]}
    with pytest.raises(ValueError, match="unique"):
        import_observations(data)


def test_comparison_identifies_owner_and_role_regression_candidates():
    before, after, _ = _profiles()
    result = compare_profiles(before, after)
    candidates = {item.case_id: item for item in result.regression_candidates}
    assert set(candidates) == {"read-other-order", "delete-as-user", "removed-owner-check", "weakened-role-check"}
    assert candidates["read-other-order"].kind is DriftKind.DENIED_TO_ALLOWED
    assert candidates["delete-as-user"].current.role == "user"
    assert next(c for c in result.changes if c.case_id == "read-own-order").kind is DriftKind.UNCHANGED


def test_separate_imported_observations_verify_candidates():
    before, after, verification = _profiles()
    result = verify_candidates(compare_profiles(before, after), verification)
    assert all(item.verification.status is VerificationStatus.VERIFIED for item in result.regression_candidates)
    assert all("not attested" in item.classification for item in result.regression_candidates)


def test_verification_rejects_current_profile_and_mismatched_scenario():
    before, after, verification = _profiles()
    comparison = compare_profiles(before, after)
    with pytest.raises(ValueError, match="separately imported"):
        verify_candidates(comparison, after)
    malformed = verification.model_copy(deep=True)
    row = next(item for item in malformed.observations if item.case_id == "read-other-order")
    row.resource = "unrelated-resource"
    result = verify_candidates(comparison, malformed)
    status = next(item.verification.status for item in result.regression_candidates if item.case_id == "read-other-order")
    assert status is VerificationStatus.INCONCLUSIVE


def test_graph_build_and_diff_carry_observed_authorization_facts():
    before, after, _ = _profiles()
    graph = build_graph(before)
    delta = diff_profiles(before, after)
    assert any(node.kind == "principal" and node.key == "user-a" for node in graph.nodes)
    assert any(edge.predicate == "OWNED_BY" for edge in graph.edges)
    changed_cases = {edge.source for edge in delta.added_edges + delta.removed_edges
                     if edge.predicate == "OBSERVED"}
    assert changed_cases


def test_experiment_result_has_no_requests_and_ground_truth_metrics():
    before, after, verification = _profiles()
    truth = {"read-own-order": False, "read-other-order": True, "delete-as-user": True, "delete-as-admin": False}
    result = run_imported_experiment(before, after, verification, ground_truth=truth)
    assert result.request_count == 0
    assert result.drift_candidates == result.verified_regressions == 4
    assert result.false_positives == result.false_negatives == 0


def test_profiles_from_different_applications_cannot_be_compared():
    before, after, _ = _profiles()
    other = after.model_copy(update={"application_id": "different-app"})
    with pytest.raises(ValueError, match="same application"):
        compare_profiles(before, other)
