# Model Evaluation Report

## Status: EXPERIMENTAL FULL-DATASET HELD-OUT EVALUATION

The 2,724-image held-out test split was evaluated using the epoch-4 checkpoint. Results: accuracy **0.9413**, balanced accuracy **0.9219**, macro precision **0.9282**, macro recall **0.9219**, macro F1 **0.9237**. CPU batch inference time was 9.4553 seconds for the evaluated test batches. Checkpoint size is 6,247,403 bytes.

Late blight recall was **0.9371** and leaf mold recall was **0.9441**, improving substantially over the earlier 0.0 recalls. The model remains experimental; field-image evaluation, unknown-crop rejection and calibration were not completed.

The executable evaluation entry point is:

```powershell
& "D:\AI-Projects\Python-Environments\KrishiDrishtiVoice\Scripts\python.exe" evaluation\evaluate_tomato_model.py --model <model-path> --test-data <independent-test-data>
```

## Task 11.9 deployment measurements

The selected checkpoint was exported to ONNX without changing weights. On a 300-image stratified sample (30 per class), PyTorch/ONNX top-1 agreement was **100.0%** and mean maximum-confidence difference was **0.00000058**. This is representative parity evidence, not a full independent field evaluation.

Provisional validation-grid temperature scaling selected **0.83**. On the 300-image development sample, ECE changed from **0.03469** to **0.01454**, NLL from **0.29242** to **0.28404**, and Brier score from **0.14050** to **0.13927**. The validation split was used during model development, so calibration is provisional. On the 300-image test sample, accuracy after calibration was **0.9000**, ECE **0.04030**, and coverage at threshold 0.60 was **0.9333**.

The development unknown protocol used 360 non-tomato PlantVillage RGB images from the already acquired archive: corn/maize, bell pepper, and potato. At threshold 0.60, false acceptance was **0.5361**. This is not reliable unknown-crop rejection; no PlantDoc or field-image data were acquired. The application therefore keeps predictions experimental and does not convert them into diagnosis or treatment.

Task 12.1 confirms application-runtime ONNX execution through the project interpreter. A held-out image returned an experimental candidate with confidence 0.9895. This is not field accuracy and does not activate diagnosis or treatment guidance.

## Task 12.4 evaluation

Potato held-out test: 323 images, accuracy **93.81%**, balanced accuracy **95.62%**, macro precision **84.90%**, macro recall **95.62%**, macro F1 **88.42%**, CPU batch time **0.917 s**. Recall: early blight **96.67%**, late blight **90.20%**, healthy **100.00%**; healthy precision was **58.82%**.

Maize held-out test: 578 images, accuracy **95.85%**, balanced accuracy **94.25%**, macro precision **94.11%**, macro recall **94.25%**, macro F1 **94.18%**, CPU batch time **1.591 s**. Recall: gray leaf spot **85.71%**, common rust **99.44%**, northern leaf blight **91.84%**, healthy **100.00%**.

ONNX parity on deterministic samples was 100% top-1 agreement: potato 90 samples with mean maximum-probability difference `1.87e-7`; maize 120 samples with difference `4.46e-7`. Unknown-image calibration for the new models remains incomplete; they stay experimental.

## Task 12.5 reliability status

Artifact paths and metadata were corrected without changing learned weights. Complete SHA-256 values were recomputed after the rename: potato checkpoint `e601ee43f7227ea1b52e6686ada9e595cbebaaae3299093db7bca2945776d2f0`, potato ONNX `55c5cd3b368528f5c0fc5e7321bba161de4f18331c68d21fbcef5ae262e086d9`, maize checkpoint `fc67019fc4957651169d906429f65835417373085ecfd5caeabf4941916273b`, maize ONNX `8aabecc7243ce2c0c1c05f1b853aedf1db64c273731ee4203716ae157cbe15eb`.

Independent calibration and unknown/wrong-crop rejection remain incomplete for potato and maize. The existing tomato development protocol had 0.5361 unknown false acceptance at threshold 0.60; this is not a production rejection result. No new threshold or calibration claim is made.

Rice research identified a CC BY 4.0 Mendeley rice-leaf dataset with 1,701 original images and eight labels, but it was not downloaded or trained. Chilli research identified a CC BY 4.0 Mendeley smartphone field dataset with 1,544 labelled images (anthracnose, Cercospora leaf spot, leaf curl, healthy), but it was not downloaded or trained. These are research leads, not project datasets.

## Task 12.6 status

No new rice or chilli evaluation exists because the authorized archives were not acquired. Existing tomato, potato and maize results remain controlled PlantVillage experiments only. Independent calibration and unknown/wrong-crop rejection remain open; no production diagnostic readiness is claimed.
