# Website Knowledge Integration Report

## Status

The specified tomato pages were inspected on 2026-11-24. Their public content includes useful topic headings and chemical instructions, but no verified reuse licence was found during this review. The application therefore does not copy page text or images and does not activate the website's chemical recommendations.

The tomato pages contain category-level material for crop production, diseases, pests and varieties. The whitefly section visibly repeats leaf-miner wording, so it is not treated as verified whitefly symptom evidence.

## Implemented records

Two rice records were added to the local knowledge base:

- `rice-crop-profile-001`: crop-stage, water, spread and fertilizer-history context.
- `rice-leaf-yellowing-001`: conservative yellowing triage using KAU and TNAU nutrient-context sources.

Rice is now recognized from English, paddy and Kannada `ಭತ್ತ` forms. Yellowing is preserved as an observation; nitrogen deficiency is not asserted. No dosage, spray schedule or chemical mixing instruction is returned.

## Source and review status

Source metadata is stored in `AGRICULTURAL_SOURCE_REGISTER.json`. Rice summaries are attributed to the inspected institutional pages, but remain pending Karnataka-specific agricultural review and Kannada native-speaker review. Tomato website content remains reference-only pending publisher/rights verification and expert review.

## Vision boundary

The existing ONNX runtime and experimental tomato classifier are preserved. Website photographs were not downloaded or used for training because reuse/training permission was not verified. The model remains a controlled PlantVillage experiment and cannot cover fruit, root or seedling disorders reliably from leaf classification alone.
