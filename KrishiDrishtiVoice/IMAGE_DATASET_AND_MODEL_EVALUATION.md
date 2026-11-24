# Image Dataset and Model Evaluation

## Current evidence

No image dataset, annotations, model weights, training script, or inference runtime exists in the repository. No model was downloaded and no ML dependency was installed.

## Candidate strategy

MobileNetV3 or EfficientNet-Lite are reasonable future Android candidates because they are lightweight families with mobile runtimes, but no model is selected here and no performance claim is made. Selection must follow an apples-to-apples evaluation using the same field-image test set and the same quantization pipeline.

## Required evaluation

- Per-class precision, recall, macro F1, and calibrated confidence.
- Unknown/unsupported and poor-quality rejection rates.
- Separate laboratory images from real field photographs.
- CPU latency, peak RAM, APK/model size, and battery impact on representative budget phones.
- Kannada/English explanation safety review independent of model accuracy.
- Dataset provenance, license, geographic coverage, crop variety, lighting, camera, disease stage, and annotation agreement.

The proposed initial crops—tomato, rice, potato, maize, and chilli—must not be treated as ready merely because datasets may exist publicly. Dataset licenses, field representativeness, and agricultural expert labels require verification before download or training.
