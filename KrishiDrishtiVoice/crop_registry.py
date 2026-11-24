"""Capability registry; status is explicit so names never imply support."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CropCapability:
    crop: str
    kannada_name: str
    registered: bool = True
    recognized: bool = False
    knowledge_supported: bool = False
    guidance_supported: bool = False
    image_supported: bool = False
    expert_reviewed: bool = False


CROP_REGISTRY = {
    "tomato": CropCapability(
        crop="tomato", kannada_name="ಟೊಮೆಟೋ", recognized=True,
        knowledge_supported=True, guidance_supported=True, image_supported=True,
    ),
    "rice": CropCapability(crop="rice", kannada_name="ಅಕ್ಕಿ / ಭತ್ತ", recognized=True, knowledge_supported=True, guidance_supported=True),
    "potato": CropCapability(crop="potato", kannada_name="ಆಲೂಗಡ್ಡೆ", recognized=True, knowledge_supported=True, guidance_supported=True),
    "maize": CropCapability(crop="maize", kannada_name="ಮೆಕ್ಕೆಜೋಳ", recognized=True, knowledge_supported=True, guidance_supported=True),
    "chilli": CropCapability(crop="chilli", kannada_name="ಮೆಣಸಿನಕಾಯಿ", recognized=True, knowledge_supported=True, guidance_supported=True),
}


def get_crop_capability(crop: str) -> dict[str, object] | None:
    capability = CROP_REGISTRY.get(crop.strip().lower())
    return asdict(capability) if capability else None


def supported_crop_names() -> list[str]:
    return [name for name, capability in CROP_REGISTRY.items() if capability.guidance_supported]
