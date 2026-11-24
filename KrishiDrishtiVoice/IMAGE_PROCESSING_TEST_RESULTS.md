# Image Processing Test Results

- Full regression suite: **97/97 passed**.
- New image processing tests: **4 passed**.
- Image contract tests: **3 passed**.
- Python compilation: passed.
- Dataset dry-run helper: no downloads performed.
- Streamlit AppTest image route: passed.
- Model registry and missing-weight tests: 2 passed.
- Real checkpoint inference smoke test: executed; low-confidence result abstained safely.
- Full-dataset epoch-4 checkpoint evaluation: executed on 2,724 held-out images.
- Unknown-class rejection and calibration: not run.

Task 11.9: 99/99 full regression tests passed. ONNX export was checked; representative parity was 300/300 top-1 agreement. Application-runtime inference passed with the exact application interpreter. Provisional calibration and unknown-image metrics are stored in `D:\KrishiDrishtiML\evaluation\task11_9_metrics.json`. Unknown rejection remains development-only; no browser interaction was verified.
