from __future__ import annotations

import io
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

from image_processing_contract import ImageResult
from .model_registry import ModelUnavailable, load_model_metadata, require_weight_file, verify_weight_checksum


@lru_cache(maxsize=2)
def _load_onnx_session(path: str):
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise ModelUnavailable("ONNX Runtime is not installed in this application environment.") from exc
    return ort.InferenceSession(path, providers=["CPUExecutionProvider"])


def _preprocess(image_bytes: bytes, metadata: dict) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    height, width = (int(v) for v in metadata["input_size"])
    image = image.resize((width, height), Image.Resampling.BILINEAR)
    values = np.asarray(image, dtype=np.float32) / 255.0
    mean = np.asarray(metadata["preprocessing"]["mean"], dtype=np.float32)
    std = np.asarray(metadata["preprocessing"]["std"], dtype=np.float32)
    return ((values - mean) / std).transpose(2, 0, 1)[None, ...].astype(np.float32)


def _result_from_logits(image_id: str, metadata: dict, logits: np.ndarray) -> ImageResult:
    logits = np.asarray(logits, dtype=np.float64)[0]
    temperature = float(metadata.get("calibration", {}).get("temperature", 1.0))
    probabilities = np.exp((logits - logits.max()) / max(temperature, 1e-6))
    probabilities /= probabilities.sum()
    index = int(probabilities.argmax())
    confidence = float(probabilities[index])
    classes = [metadata["class_mapping"][str(i)] for i in range(len(metadata["class_mapping"]))]
    crop_label = classes[0].split("___", 1)[0] if classes else "unknown"
    crop = {"Corn_(maize)": "maize", "Potato": "potato", "Tomato": "tomato"}.get(crop_label, crop_label.casefold())
    threshold = float(metadata.get("rejection", {}).get("confidence_threshold", metadata.get("abstention_threshold", 0.60)))
    if confidence < threshold:
        return ImageResult(image_id=image_id, quality_status="accepted", model_version=metadata["model_version"], model_confidence=confidence, supported_class_status="unknown", uncertainty_reason="The calibrated confidence is below the provisional rejection threshold.", clarification_question="Can you describe what you observe on the plant?", abstained=True)
    return ImageResult(image_id=image_id, quality_status="accepted", candidate_crop=crop, candidate_disease_or_pest=classes[index], model_version=metadata["model_version"], model_confidence=confidence, supported_class_status="supported", uncertainty_reason="Experimental visual candidate only; this is not a confirmed diagnosis.", clarification_question="Does this candidate match what you observe in the field?", abstained=False)


def infer_image(*, image_id: str, image_bytes: bytes, weights_path: str | Path, metadata_path: str | Path) -> ImageResult:
    """Run local ONNX inference, with conservative abstention on any failure."""
    try:
        metadata = load_model_metadata(metadata_path)
        if metadata.get("runtime_format", "torch") == "onnx":
            model_path = Path(metadata.get("onnx_model_path", weights_path))
            require_weight_file(model_path)
            verify_weight_checksum(model_path, {"weights_sha256": metadata["onnx_sha256"]})
            session = _load_onnx_session(str(model_path))
            logits = session.run(None, {session.get_inputs()[0].name: _preprocess(image_bytes, metadata)})[0]
            return _result_from_logits(image_id, metadata, logits)
        require_weight_file(weights_path)
        verify_weight_checksum(weights_path, metadata)
        import torch
        from torchvision import models, transforms
        model = models.mobilenet_v3_small(weights=None)
        model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(metadata["class_mapping"]))
        model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True)); model.eval()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        transform = transforms.Compose([transforms.Resize(tuple(metadata["input_size"])), transforms.ToTensor(), transforms.Normalize(metadata["preprocessing"]["mean"], metadata["preprocessing"]["std"])])
        with torch.no_grad():
            logits = model(transform(image).unsqueeze(0)).numpy()
        return _result_from_logits(image_id, metadata, logits)
    except (ModelUnavailable, ImportError, OSError, RuntimeError, ValueError) as exc:
        return ImageResult(image_id=image_id, quality_status="not_evaluated", supported_class_status="unknown", uncertainty_reason=str(exc), clarification_question="Please continue with a text or voice description.", abstained=True)
