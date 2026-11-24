from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError


ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_PIXELS = 25_000_000


def load_image_bytes(data: bytes, *, max_bytes: int = DEFAULT_MAX_BYTES,
                     max_pixels: int = DEFAULT_MAX_PIXELS) -> Image.Image:
    if not data:
        raise ValueError("No image data was provided.")
    if len(data) > max_bytes:
        raise ValueError("Image file is too large. Please choose an image under 10 MB.")
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValueError("Unsupported image format. Use JPEG, PNG, or WebP.")
            if image.width * image.height > max_pixels:
                raise ValueError("Image dimensions are too large. Please choose a smaller image.")
            # EXIF orientation is applied, then the image is converted to a safe RGB surface.
            return image.convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("The file is not a valid image or is corrupted.") from exc
