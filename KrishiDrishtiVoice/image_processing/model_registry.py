from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any


class ModelUnavailable(RuntimeError):
    pass


MODEL_CONFIGS = {
    "tomato": {
        "status": "experimental",
        "weights": Path(r"D:\KrishiDrishtiML\models\tomato_full_exp2\mobilenet_v3_small_tomato.pt"),
        "metadata": Path(r"D:\KrishiDrishtiML\models\tomato_full_exp2\export\metadata.json"),
    },
    "potato": {
        "status": "experimental",
        "weights": Path(r"D:\KrishiDrishtiML\models\potato_exp1\mobilenet_v3_small_potato.pt"),
        "metadata": Path(r"D:\KrishiDrishtiML\models\potato_exp1\export\metadata.json"),
    },
    "maize": {
        "status": "experimental",
        "weights": Path(r"D:\KrishiDrishtiML\models\maize_exp1\mobilenet_v3_small_maize.pt"),
        "metadata": Path(r"D:\KrishiDrishtiML\models\maize_exp1\export\metadata.json"),
    },
}


def get_model_config(crop: str) -> dict[str, Any] | None:
    config = MODEL_CONFIGS.get(str(crop).strip().lower())
    return dict(config) if config else None


def load_model_metadata(path: str | Path) -> dict[str, Any]:
    metadata_path = Path(path)
    if not metadata_path.exists():
        raise ModelUnavailable("No approved image model metadata is installed.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelUnavailable("Image model metadata is missing or corrupted.") from exc
    required = {"model_version", "class_mapping", "input_size", "preprocessing"}
    missing = sorted(required - set(metadata))
    if missing:
        raise ModelUnavailable("Image model metadata is incomplete: " + ", ".join(missing))
    if not isinstance(metadata["class_mapping"], dict) or not metadata["class_mapping"]:
        raise ModelUnavailable("Image model class_mapping is invalid.")
    return metadata


def require_weight_file(path: str | Path) -> Path:
    weight_path = Path(path)
    if not weight_path.exists() or weight_path.stat().st_size == 0:
        raise ModelUnavailable("Approved image model weights are not installed.")
    return weight_path


def verify_weight_checksum(path: str | Path, metadata: dict[str, Any]) -> None:
    expected = metadata.get("weights_sha256")
    if not expected:
        raise ModelUnavailable("Image model metadata has no weight checksum.")
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest.lower() != str(expected).lower():
        raise ModelUnavailable("Image model checksum does not match its metadata.")
