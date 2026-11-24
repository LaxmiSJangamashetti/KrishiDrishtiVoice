"""Schema-only contract for future image observations.

This module deliberately performs no image inference. It validates the boundary
between a future vision component and the existing conversation/safety pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_QUALITY = {"accepted", "rejected", "uncertain", "not_evaluated"}
ALLOWED_SUPPORTED_CLASS = {"supported", "unsupported", "unknown"}


@dataclass
class ImageResult:
    image_id: str
    quality_status: str = "not_evaluated"
    candidate_crop: str | None = None
    visible_symptoms: list[dict[str, Any]] = field(default_factory=list)
    candidate_disease_or_pest: str | None = None
    model_confidence: float | None = None
    model_version: str | None = None
    supported_class_status: str = "unknown"
    uncertainty_reason: str | None = None
    clarification_question: str | None = None
    abstained: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.image_id.strip():
            errors.append("image_id is required")
        if self.quality_status not in ALLOWED_QUALITY:
            errors.append("invalid quality_status")
        if self.supported_class_status not in ALLOWED_SUPPORTED_CLASS:
            errors.append("invalid supported_class_status")
        if self.model_confidence is not None and not 0 <= self.model_confidence <= 1:
            errors.append("model_confidence must be between 0 and 1")
        if not isinstance(self.visible_symptoms, list):
            errors.append("visible_symptoms must be a list")
        if not self.abstained and not self.uncertainty_reason:
            errors.append("non-abstained results require an uncertainty_reason")
        return errors

    def to_dict(self) -> dict[str, Any]:
        errors = self.validate()
        if errors:
            raise ValueError("Invalid image result: " + "; ".join(errors))
        return asdict(self)
