# Image Inference Implementation Report

## Status

- Image decoding and quality validation: **IMPLEMENTED and TESTED**.
- Model metadata and missing-weight checks: **IMPLEMENTED and TESTED**.
- Missing-model inference behavior: **IMPLEMENTED and TESTED_WITH_MOCKS**; returns abstention through `ImageResult`.
- Real model inference: **IMPLEMENTED and TESTED_WITH_REAL_CHECKPOINT**.
- Disease diagnosis: **NOT OPERATIONAL**.

`image_processing/inference_engine.py` refuses missing or incomplete model artifacts and never fabricates a prediction.

Selected checkpoint: `D:\KrishiDrishtiML\models\tomato_full_exp2\mobilenet_v3_small_tomato.pt`; SHA-256 `88F10DA56D69FC6F45954BAB22D0FAF003FC4F2EC8291563D2D9ACAD2B56D2F6`. Provisional threshold: 0.60. Cold-load plus single-image inference: 3.124 seconds. A real held-out image produced a candidate label with confidence 0.9738; the UI labels it experimental and not diagnostic.

## Task 11.9 update

The normal application environment now uses the ONNX export at `D:\KrishiDrishtiML\models\tomato_full_exp2\export\mobilenet_v3_small_tomato.onnx` through `onnxruntime 1.23.2` and CPU execution. The export SHA-256 is `5a6f7917825f3918871eb5241f8a23077805b2213b57d639ce500442cb409564`. Application-side inference was executed with the exact Streamlit interpreter on a held-out image and returned a real experimental candidate. Calibrated confidence is stored in the export metadata, but unknown rejection remains provisional because the development unknown false-acceptance rate was 0.5361.

## Task 12.5 update

Crop-specific ONNX artifacts are now named `mobilenet_v3_small_potato.onnx` and `mobilenet_v3_small_maize.onnx`; registry and metadata references were corrected. Real application-side inference was rerun for potato and maize after correction and returned experimental candidates. This does not establish diagnosis, field validity, independent calibration, or reliable wrong-crop rejection.
