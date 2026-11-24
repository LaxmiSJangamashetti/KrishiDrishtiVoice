# Crop and Disease Coverage Matrix

Audit basis: repository inspection on 2026-11-24. A name in a registration field or a rejected-question guard is not counted as agricultural support.

| Crop | Kannada name | LU support | Knowledge coverage | Disease coverage | Pest coverage | Image support | Tests | Readiness |
|---|---|---|---|---|---|---|---|---|
| Tomato | ಟೊಮೆಟೋ | Yes; only crop alias | 10 curated records | 4 disease categories listed as references, not diagnoses | 5 pest categories listed; 3 observation records | Experimental 10-class PlantVillage classifier; not field validated | Extensive English/Kannada/retrieval/safety tests plus image tests | Text guidance plus experimental image candidate only |
| Rice | ಅಕ್ಕಿ / ಭತ್ತ | No | None | None | None | None | Unsupported-crop tests only | Not supported |
| Wheat | ಗೋಧಿ | No | None | None | None | None | Unsupported-crop tests only | Not supported |
| Maize | ಮೆಕ್ಕೆಜೋಳ | No | None | None | None | None | Unsupported-crop guard only | Not supported |
| Ragi | ರಾಗಿ | No | None | None | None | None | None | Not supported |
| Jowar | ಜೋಳ | No | None | None | None | None | None | Not supported |
| Chilli | ಮೆಣಸಿನಕಾಯಿ | No | None | None | None | None | Unsupported-crop guard only | Not supported |
| Potato | ಆಲೂಗಡ್ಡೆ | No | None | None | None | None | Unsupported-crop guard only | Not supported |
| Onion | ಈರುಳ್ಳಿ | No | None | None | None | None | None | Not supported |
| Brinjal | ಬದನೆಕಾಯಿ | No | None | None | None | None | None | Not supported |
| Okra | ಬೆಂಡೆಕಾಯಿ | No | None | None | None | None | None | Not supported |
| Sugarcane | ಕಬ್ಬು | No | None | None | None | None | None | Not supported |
| Cotton | ಹತ್ತಿ | No | None | None | None | None | None | Not supported |
| Groundnut | ನೆಲಗಡಲೆ | No | None | None | None | None | None | Not supported |
| Sunflower | ಸೂರ್ಯಕಾಂತಿ | No | None | None | None | None | None | Not supported |
| Pigeon pea | ತೊಗರಿ | No | None | None | None | None | None | Not supported |
| Chickpea | ಕಡಲೆ | No | None | None | None | None | None | Not supported |
| Green gram | ಹೆಸರುಕಾಳು | No | None | None | None | None | None | Not supported |
| Banana | ಬಾಳೆಹಣ್ಣು | No | None | None | None | None | None | Not supported |
| Mango | ಮಾವು | No | None | None | None | None | None | Not supported |

## Exact counts

- Crops with LU crop aliases: **1** (tomato).
- Crops with knowledge records: **1** (tomato).
- Crops with evidence-backed text guidance: **1**, limited to curated tomato observations and triage.
- Crops with tested disease/pest observation coverage: **1** (tomato).
- Crops with production-ready image inference: **0**; tomato has an experimental controlled-dataset classifier only.
- Measurable disease categories in the tomato reference record: **4** (early blight, late blight, bacterial wilt, leaf curl virus); not diagnostic.
- Measurable pest categories in the tomato reference record: **5** (fruit borer, whitefly, aphids, thrips, leaf miner); not a treatment recommendation.

The crop registration form accepts free text. That is storage capability, not support evidence.

Task 11.9 update: tomato image inference is now available experimentally through the ONNX runtime in the application environment. The controlled PlantVillage classifier is not production-ready and does not authorize disease-specific treatment or diagnosis. Unknown-crop rejection remains provisional.

Task 11.9 + 12 update: rice is now recognized and has two local, source-attributed guidance records for crop context and conservative leaf-yellowing triage. Rice has text knowledge and guidance support, but no image model, Kannada expert review, or regional agronomic approval yet.

## Task 12.2/12.3 multi-crop update

Text capabilities now cover five recognized crops: tomato, rice/paddy, potato, maize/corn and chilli. All five have limited source-attributed observation guidance; this does not mean all diseases or treatments are supported.

PlantVillage archive audit found: tomato 18,160 images / 10 classes; potato 2,152 images / 3 classes; maize 3,852 images / 4 classes; bell pepper 2,475 images / 2 classes; rice 0 images; chilli 0 images. Bell pepper is not treated as chilli. Only tomato has a trained/exported image model in this project. Potato and maize image models were not promoted without a completed training and independent evaluation run.

## Task 12.5 image capability update

Experimental trained image models now exist for tomato, potato and maize, with crop-specific registry selection. Rice and chilli remain text-only because no eligible image dataset was acquired for this project. All three image models remain experimental; independent calibration, wrong-crop/unknown rejection, field validation and expert review are still required.
