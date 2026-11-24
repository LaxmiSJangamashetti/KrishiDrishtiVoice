"""Export the selected tomato classifier without changing its learned weights."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--artifact-name", default="mobilenet_v3_small.onnx")
    args = parser.parse_args()

    import torch
    from torchvision import models
    import onnx

    weights = Path(args.weights)
    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    classes = [metadata["class_mapping"][str(i)] for i in range(len(metadata["class_mapping"]))]
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(classes))
    model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
    model.eval()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = output_dir / args.artifact_name
    sample = torch.zeros(1, 3, int(metadata["input_size"][0]), int(metadata["input_size"][1]))
    torch.onnx.export(
        model,
        sample,
        onnx_path,
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
    onnx.checker.check_model(onnx.load(onnx_path))
    digest = hashlib.sha256(onnx_path.read_bytes()).hexdigest()
    export_metadata = {
        **metadata,
        "runtime_format": "onnx",
        "onnx_opset": 17,
        "onnx_model_path": str(onnx_path),
        "onnx_sha256": digest,
        "export_source_weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
        "export_source_model_version": metadata["model_version"],
        "export_status": "experimental",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(export_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"onnx": str(onnx_path), "sha256": digest, "bytes": onnx_path.stat().st_size}))


if __name__ == "__main__":
    main()
