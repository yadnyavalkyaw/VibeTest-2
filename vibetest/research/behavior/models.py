"""Schemas for imported authorization observations (no target requests)."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AuthorizationOutcome(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    UNKNOWN = "unknown"


class ResponseEvidence(BaseModel):
    """Small, caller-supplied response facts; never populated from live traffic here."""

    status_code: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    redirect_to: str | None = None
    body_excerpt: str | None = Field(default=None, max_length=4096)
    body_sha256: str | None = None
    indicators: list[str] = Field(default_factory=list)
    evidence_ref: str | None = None


class OutcomeRule(BaseModel):
    """A deterministic conjunctive response classifier rule."""

    outcome: AuthorizationOutcome
    status_codes: set[int] = Field(default_factory=set)
    body_contains: list[str] = Field(default_factory=list)
    redirect_contains: list[str] = Field(default_factory=list)
    indicator_contains: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_matcher(self) -> "OutcomeRule":
        if not (self.status_codes or self.body_contains or self.redirect_contains or self.indicator_contains):
            raise ValueError("an outcome rule must define at least one matcher")
        return self


class OutcomeClassifier(BaseModel):
    """Classifies imported response data; ambiguous/no-match results stay unknown."""

    rules: list[OutcomeRule] = Field(default_factory=list)

    def classify(self, response: ResponseEvidence) -> AuthorizationOutcome:
        matches: set[AuthorizationOutcome] = set()
        body = (response.body_excerpt or "").casefold()
        redirect = (response.redirect_to or "").casefold()
        indicators = [value.casefold() for value in response.indicators]
        for rule in self.rules:
            checks: list[bool] = []
            if rule.status_codes:
                checks.append(response.status_code in rule.status_codes)
            if rule.body_contains:
                checks.append(any(term.casefold() in body for term in rule.body_contains))
            if rule.redirect_contains:
                checks.append(any(term.casefold() in redirect for term in rule.redirect_contains))
            if rule.indicator_contains:
                checks.append(any(any(term.casefold() in value for value in indicators) for term in rule.indicator_contains))
            if checks and all(checks):
                matches.add(rule.outcome)
        if len(matches) == 1:
            return next(iter(matches))
        return AuthorizationOutcome.UNKNOWN


class BehaviorObservation(BaseModel):
    """One labeled, imported behavior observation for an application version."""

    case_id: str = Field(min_length=1)
    application_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    principal_label: str | None = None
    role: str | None = None
    action: str = Field(min_length=1)
    resource: str = Field(min_length=1)
    resource_owner_id: str | None = None
    endpoint: str = Field(min_length=1)
    method: str = Field(min_length=1)
    application_state: str = "default"
    authorization_condition: str | None = None
    policy_source: str | None = None
    expected: AuthorizationOutcome = AuthorizationOutcome.UNKNOWN
    observed: AuthorizationOutcome = AuthorizationOutcome.UNKNOWN
    response: ResponseEvidence = Field(default_factory=ResponseEvidence)
    source: str = "imported"
    source_version: str | None = None
    source_ref: str | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def comparison_key(self) -> str:
        """Stable scenario identity shared across application versions."""
        return self.case_id


class BehaviorProfile(BaseModel):
    """Immutable-by-convention version profile persisted as JSON."""

    schema_version: str = "1"
    profile_id: str
    application_id: str
    version_id: str
    source_version: str | None = None
    source_ref: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observations: list[BehaviorObservation]

    @classmethod
    def from_observations(
        cls,
        application_id: str,
        version_id: str,
        observations: list[BehaviorObservation],
        *,
        source_version: str | None = None,
        source_ref: str | None = None,
    ) -> "BehaviorProfile":
        if not observations:
            raise ValueError("cannot create a behavior profile without observations")
        for observation in observations:
            if observation.application_id != application_id or observation.version_id != version_id:
                raise ValueError("all observations must match the profile application and version")
        keys = [observation.case_id for observation in observations]
        if len(set(keys)) != len(keys):
            raise ValueError("case_id values must be unique within a profile")
        canonical = {
            "application_id": application_id,
            "version_id": version_id,
            "source_version": source_version,
            "source_ref": source_ref,
            "observations": [o.model_dump(mode="json", exclude={"observed_at"}) for o in sorted(observations, key=lambda x: x.case_id)],
        }
        digest = sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:24]
        return cls(
            profile_id=f"profile-{digest}",
            application_id=application_id,
            version_id=version_id,
            source_version=source_version,
            source_ref=source_ref,
            observations=observations,
        )


class ImportedObservationSet(BaseModel):
    """Envelope accepted by the offline importer."""

    application_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    source_version: str | None = None
    source_ref: str | None = None
    observations: list[dict[str, Any]]


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    NOT_REPRODUCED = "not_reproduced"
    INCONCLUSIVE = "inconclusive"


class VerificationRecord(BaseModel):
    case_id: str
    status: VerificationStatus
    baseline_outcome: AuthorizationOutcome
    candidate_outcome: AuthorizationOutcome
    verification_outcome: AuthorizationOutcome
    evidence_ref: str | None = None
    note: str
