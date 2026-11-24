# Model Training Report

## Status: EXPERIMENTAL FULL-DATASET TRAINING EXECUTED

Isolated environment: `D:\KrishiDrishtiML\venv` (Python 3.13.9). CPU-only; CUDA was unavailable. Installed versions: torch 2.15.0+cpu, torchvision 0.29.2+cpu, NumPy 2.5.4, Pillow 13.0.0, scikit-learn 1.9.1, psutil 7.2.2.

PlantVillage was acquired from the authorized source and its SHA-256 verified as `FBA30C6A7965E49BE94B47A62F8AFF6CFB1C35C27F475F22092B56DB41745E84`. Only the RGB tomato subset was extracted: 18,160 images across 10 classes. The experiment used 100 images per class: 700 train, 150 validation, 150 test.

Training command:

```powershell
& "D:\KrishiDrishtiML\venv\Scripts\python.exe" evaluation\train_tomato_model.py --dataset "D:\KrishiDrishtiML\datasets\plantvillage_tomato_color" --output "D:\KrishiDrishtiML\models\tomato_exp1" --epochs 2 --limit-per-class 100 --batch-size 32 --pretrained --device cpu
```

The full-dataset run completed 4 epochs and saved checkpoints for epochs 1–4. The wrapper ended before the configured fifth-epoch metadata write; epoch 4 is the completed artifact. Full split counts are 12,712 train, 2,724 validation, and 2,724 test. This remains controlled PlantVillage evaluation, not field validation.

The executable entry point is:

```powershell
& "D:\AI-Projects\Python-Environments\KrishiDrishtiVoice\Scripts\python.exe" evaluation\train_tomato_model.py --dataset <approved-dataset> --output <D:-output-dir>
```

The script remains configurable for a larger approved experiment.

## Task 12.4 multi-crop experiments

Potato and maize were trained from the existing PlantVillage archive using the same MobileNetV3-Small transfer-learning script, pretrained weights cached under `D:\KrishiDrishtiML`, CPU execution, three epochs and batch size 32. No tomato checkpoint was overwritten.

Potato: 1,152 images across 3 classes; train 806, validation 161, test 323. Best validation accuracy was 94.43%. Model: `D:\KrishiDrishtiML\models\potato_exp1\mobilenet_v3_small_tomato.pt`.

Maize: 3,852 images across 4 classes; train 2,696, validation 578, test 578. Best validation accuracy was 95.50% at epoch 2; epoch 3 completed. Model: `D:\KrishiDrishtiML\models\maize_exp1\mobilenet_v3_small_tomato.pt`.

These are controlled PlantVillage experiments, not field performance.

## Task 12.5 artifact audit

The potato archive contains 2,152 images and its split manifest accounts for all of them: 1,506 train, 323 validation, and 323 test. The previously reported 806/161/323 counts describe an earlier sampled experiment, not the current full split manifest; the remaining 862 images were subsequently included in the current training split. No duplicate-removal or class-balance exclusion was found in the current manifest.

The deployed non-tomato artifacts were renamed to `mobilenet_v3_small_potato.pt/.onnx` and `mobilenet_v3_small_maize.pt/.onnx`. Metadata now points to the crop-specific ONNX names and crop-specific source model versions. No model was retrained or overwritten.

No rice or chilli dataset was acquired in this task. Candidate licensed sources remain subject to permission/provenance review before acquisition.

## Task 12.6 status

Rice and chilli archives were not acquired: the ML environment could not resolve `api.mendeley.com`, and no local archive was present. Therefore no rice/chilli training, leakage-safe split, calibration, ONNX export, or metrics are claimed. The chilli source also has a licence-scope inconsistency requiring clarification before commercial use.
