"""Offline import and persistence for versioned behavior profiles."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import (
    AuthorizationOutcome,
    BehaviorObservation,
    BehaviorProfile,
    ImportedObservationSet,
    OutcomeClassifier,
    ResponseEvidence,
)


def import_observations(
    data: dict[str, Any] | list[dict[str, Any]],
    *,
    classifier: OutcomeClassifier | None = None,
) -> BehaviorProfile:
    """Create a profile from caller-supplied JSON-compatible observations.

    No network access or credential handling occurs in this importer.
    """
    if isinstance(data, list):
        if not data:
            raise ValueError("observation list is empty")
        first = data[0]
        application_id = first.get("application_id")
        version_id = first.get("version_id")
        envelope: dict[str, Any] = {
            "application_id": application_id,
            "version_id": version_id,
            "observations": data,
        }
    elif isinstance(data, dict):
        envelope = data
    else:
        raise ValueError("expected an observation object or list")

    try:
        imported = ImportedObservationSet.model_validate(envelope)
    except ValidationError as exc:
        raise ValueError(f"invalid observation set: {exc}") from exc
    application_id, version_id = imported.application_id, imported.version_id
    raw_observations = imported.observations
    if not isinstance(raw_observations, list) or not raw_observations:
        raise ValueError("observations must be a non-empty list")

    parsed: list[BehaviorObservation] = []
    for index, raw in enumerate(raw_observations):
        if not isinstance(raw, dict):
            raise ValueError(f"observation {index} must be an object")
        item = dict(raw)
        item.setdefault("application_id", application_id)
        item.setdefault("version_id", version_id)
        try:
            response = ResponseEvidence.model_validate(item.get("response") or {})
        except ValidationError as exc:
            raise ValueError(f"invalid response evidence in observation {index}: {exc}") from exc
        item["response"] = response
        if "observed" not in item or item["observed"] in (None, ""):
            item["observed"] = (classifier or OutcomeClassifier()).classify(response).value
        try:
            parsed.append(BehaviorObservation.model_validate(item))
        except Exception as exc:
            raise ValueError(f"invalid observation {index}: {exc}") from exc

    return BehaviorProfile.from_observations(
        application_id,
        version_id,
        parsed,
        source_version=imported.source_version,
        source_ref=imported.source_ref,
    )


def load_profile(path: str | Path) -> BehaviorProfile:
    return BehaviorProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_profile(profile: BehaviorProfile, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(profile.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_observations(path: str | Path, *, classifier: OutcomeClassifier | None = None) -> BehaviorProfile:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read observation JSON: {exc}") from exc
    return import_observations(data, classifier=classifier)
