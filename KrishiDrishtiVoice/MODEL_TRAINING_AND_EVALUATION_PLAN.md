# Model Training and Evaluation Plan

No model is trained or evaluated. No weights were downloaded.

The first model gate is tomato-only and must use classes supported by both a verified dataset and reviewed agricultural knowledge. Candidate architectures such as MobileNetV3 and EfficientNet-Lite require a controlled comparison for macro F1, per-class precision/recall, calibration, unknown-class rejection, CPU latency, RAM, model size, and battery impact on representative budget Android devices.

Python 3.13 compatibility for a future training stack must be verified in an isolated environment; the application environment must not be changed for training.

Required evaluation splits are plant/farm/collection-group separated. Laboratory images and independent field images must be reported separately. A high softmax score is not sufficient evidence of calibration or diagnosis.
