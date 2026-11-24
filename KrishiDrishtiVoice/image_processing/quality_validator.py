from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO

import numpy as np
from PIL import Image, ImageFilter, UnidentifiedImageError

from .image_loader import load_image_bytes


@dataclass(frozen=True)
class ImageQualityReport:
    accepted: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    width: int | None = None
    height: int | None = None
    format: str | None = None
    brightness: float | None = None
    blur_score: float | None = None


def validate_image(data: bytes, *, max_bytes: int = 10 * 1024 * 1024,
                   max_pixels: int = 25_000_000) -> ImageQualityReport:
    try:
        image = load_image_bytes(data, max_bytes=max_bytes, max_pixels=max_pixels)
    except ValueError as exc:
        return ImageQualityReport(False, "rejected", [str(exc)])

    gray = np.asarray(image.convert("L"), dtype=np.float32)
    brightness = float(gray.mean())
    edges = np.asarray(image.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    blur_score = float(edges.var())
    reasons: list[str] = []
    # These are provisional retake heuristics, not crop or disease classifiers.
    if brightness < 20:
        reasons.append("Image is too dark. Retake it in even natural light.")
    elif brightness > 240:
        reasons.append("Image is overexposed. Avoid direct glare and retake it.")
    if blur_score < 12:
        reasons.append("Image may be blurry. Hold the camera steady and retake it.")
    return ImageQualityReport(
        not reasons, "accepted" if not reasons else "uncertain", reasons,
        image.width, image.height, "RGB", brightness, blur_score,
    )
