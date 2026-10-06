"""Deterministic, evidence-preserving comparison of imported profiles."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .models import AuthorizationOutcome, BehaviorObservation, BehaviorProfile, VerificationRecord, VerificationStatus


class DriftKind(str, Enum):
    DENIED_TO_ALLOWED = "denied_to_allowed"
    ALLOWED_TO_DENIED = "allowed_to_denied"
    EXPECTATION_CHANGED = "expectation_changed"
    NEWLY_ACCESSIBLE = "newly_accessible"
    OBSERVATION_REMOVED = "observation_removed"
    OUTCOME_CHANGED = "outcome_changed"
    UNCHANGED = "unchanged"


class DriftChange(BaseModel):
    case_id: str
    kind: DriftKind
    classification: str
    is_regression_candidate: bool = False
    baseline: BehaviorObservation | None = None
    current: BehaviorObservation | None = None
    verification: VerificationRecord | None = None


class BehaviorComparison(BaseModel):
    application_id: str
    baseline_profile_id: str
    current_profile_id: str
    baseline_version: str
    current_version: str
    changes: list[DriftChange] = Field(default_factory=list)

    @property
    def regression_candidates(self) -> list[DriftChange]:
        return [change for change in self.changes if change.is_regression_candidate]


def compare_profiles(baseline: BehaviorProfile, current: BehaviorProfile) -> BehaviorComparison:
    if baseline.application_id != current.application_id:
        raise ValueError("profiles must belong to the same application")
    if baseline.version_id == current.version_id:
        raise ValueError("profiles must represent different versions")

    old = {observation.case_id: observation for observation in baseline.observations}
    new = {observation.case_id: observation for observation in current.observations}
    changes: list[DriftChange] = []

    for case_id in sorted(old.keys() | new.keys()):
        before, after = old.get(case_id), new.get(case_id)
        if before is None and after is not None:
            candidate = after.observed is AuthorizationOutcome.ALLOWED and after.expected is AuthorizationOutcome.DENIED
            changes.append(DriftChange(
                case_id=case_id,
                kind=DriftKind.NEWLY_ACCESSIBLE if candidate else DriftKind.OUTCOME_CHANGED,
                classification="newly observed access; requires review" if candidate else "new observation; no prior baseline case",
                is_regression_candidate=candidate,
                current=after,
            ))
            continue
        if after is None and before is not None:
            changes.append(DriftChange(case_id=case_id, kind=DriftKind.OBSERVATION_REMOVED,
                                       classification="baseline observation missing in current profile", baseline=before))
            continue
        assert before is not None and after is not None
        if before.expected is not after.expected:
            candidate = before.observed is AuthorizationOutcome.DENIED and after.observed is AuthorizationOutcome.ALLOWED
            changes.append(DriftChange(case_id=case_id, kind=DriftKind.EXPECTATION_CHANGED,
                                       classification="expected authorization condition changed; review policy/source",
                                       is_regression_candidate=candidate, baseline=before, current=after))
        elif before.observed is after.observed:
            changes.append(DriftChange(case_id=case_id, kind=DriftKind.UNCHANGED,
                                       classification="no observed authorization behavior change", baseline=before, current=after))
        elif before.observed is AuthorizationOutcome.DENIED and after.observed is AuthorizationOutcome.ALLOWED:
            changes.append(DriftChange(case_id=case_id, kind=DriftKind.DENIED_TO_ALLOWED,
                                       classification="security drift candidate: denied access became allowed",
                                       is_regression_candidate=True, baseline=before, current=after))
        elif before.observed is AuthorizationOutcome.ALLOWED and after.observed is AuthorizationOutcome.DENIED:
            changes.append(DriftChange(case_id=case_id, kind=DriftKind.ALLOWED_TO_DENIED,
                                       classification="behavior changed to deny; possible functionality regression",
                                       baseline=before, current=after))
        else:
            candidate = after.expected is AuthorizationOutcome.DENIED and after.observed is AuthorizationOutcome.ALLOWED
            changes.append(DriftChange(case_id=case_id, kind=DriftKind.OUTCOME_CHANGED,
                                       classification="observed outcome changed or became inconclusive",
                                       is_regression_candidate=candidate, baseline=before, current=after))

    return BehaviorComparison(
        application_id=baseline.application_id,
        baseline_profile_id=baseline.profile_id,
        current_profile_id=current.profile_id,
        baseline_version=baseline.version_id,
        current_version=current.version_id,
        changes=changes,
    )


def verify_candidates(
    comparison: BehaviorComparison,
    verification_profile: BehaviorProfile,
) -> BehaviorComparison:
    """Match candidates against a separately imported verification profile.

    VERIFIED means the supplied independent observation reproduces the denied→allowed
    transition. This module does not generate a request or prove how evidence was collected.
    """
    if verification_profile.application_id != comparison.application_id:
        raise ValueError("verification profile belongs to a different application")
    if verification_profile.profile_id in {comparison.baseline_profile_id, comparison.current_profile_id}:
        raise ValueError("verification must use a separately imported profile")
    supplied = {observation.case_id: observation for observation in verification_profile.observations}
    for change in comparison.changes:
        if not change.is_regression_candidate:
            continue
        check = supplied.get(change.case_id)
        baseline_outcome = change.baseline.observed if change.baseline else AuthorizationOutcome.UNKNOWN
        candidate_outcome = change.current.observed if change.current else AuthorizationOutcome.UNKNOWN
        if check is None:
            status = VerificationStatus.INCONCLUSIVE
            outcome = AuthorizationOutcome.UNKNOWN
            note = "no separately supplied observation for this candidate"
            evidence_ref = None
        else:
            outcome = check.observed
            evidence_ref = check.response.evidence_ref or check.source_ref
            reference = change.current or change.baseline
            fields = ("principal_id", "role", "action", "resource", "resource_owner_id", "endpoint", "method", "application_state")
            same_scenario = reference is not None and all(getattr(reference, field) == getattr(check, field) for field in fields)
            if not same_scenario:
                status = VerificationStatus.INCONCLUSIVE
                note = "supplied verification record does not match the candidate scenario fields"
            elif candidate_outcome is AuthorizationOutcome.ALLOWED and outcome is AuthorizationOutcome.ALLOWED and baseline_outcome in {AuthorizationOutcome.DENIED, AuthorizationOutcome.UNKNOWN}:
                status = VerificationStatus.VERIFIED
                note = (
                    "separately supplied observation reproduces denied-to-allowed behavior"
                    if baseline_outcome is AuthorizationOutcome.DENIED
                    else "separately supplied observation confirms access for a new denied-expected case"
                )
            elif outcome is AuthorizationOutcome.DENIED:
                status = VerificationStatus.NOT_REPRODUCED
                note = "separately supplied observation did not reproduce allowed access"
            else:
                status = VerificationStatus.INCONCLUSIVE
                note = "supplied verification observation is inconclusive"
        change.verification = VerificationRecord(
            case_id=change.case_id,
            status=status,
            baseline_outcome=baseline_outcome,
            candidate_outcome=candidate_outcome,
            verification_outcome=outcome,
            evidence_ref=evidence_ref,
            note=note,
        )
        if status is VerificationStatus.VERIFIED:
            change.classification = "verified within separately supplied observations; collection method is not attested"
    return comparison
