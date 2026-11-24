# Image Processing Implementation Report

## Implemented and tested

- Actual image bytes are decoded with Pillow.
- JPEG, PNG and WebP are accepted after content verification.
- Corrupt content, unsupported formats, excessive file size and excessive pixel count are rejected.
- Images are converted to RGB after decoding.
- Provisional brightness and edge-variance blur heuristics return retake feedback.
- Quality checks explicitly do not determine crop identity or disease.

## Not implemented

- Model loading, inference, crop classification, disease classification, calibration, or Android export.
- No image prediction is shown in the UI; the UI reports model unavailable.
