# Image Processing Architecture

## Repository audit

No image-processing module, model weights, image dataset, annotation set, upload-to-inference path, evaluation report, or mobile inference implementation was found. The current application has no operational image inference.

## Future boundary

`image upload/camera → quality validation → preprocessing → local or service inference → ImageResult → Conversation Manager → clarification → safety validation → retrieval → guidance → optional TTS`

The vision component must emit structured observations only. It must not emit pesticide dosages, chemical mixtures, or confirmed diagnoses.

## Implemented contract

`image_processing_contract.py` defines and validates the schema boundary. It performs no inference and defaults to abstention. `ImageResult` includes image ID, quality status, candidate crop, visible symptoms, candidate disease/pest, optional calibrated confidence, model version, supported-class status, uncertainty reason, clarification question, and abstention status.

## Future quality gates

- Reject blurred, dark, obstructed, or unsupported images.
- Include an explicit unknown/unsupported class.
- Calibrate confidence on field images, not only laboratory images.
- Keep model version and preprocessing version with every result.
- Preserve the original image reference without exposing it in logs.
