# Phase 0 Baseline Report

Status: Draft benchmark preparation. The 300 questions are generated evaluation examples and are not expert-validated. No model was downloaded and no Gnani request was made.

## Composition

- 300 total: 120 Kannada-script, 90 English, 90 Kannada-English code-mixed.
- Exactly 20 safety/adversarial questions within the total.
- Ten existing tomato observation topics plus ambiguity, crop omission, spelling/transcription variation and unsupported crops.

## Methodology

run_baseline.py imports parse_question, identify_crop, search and build_guidance from the existing agriculture_engine.py. It records expected labels, observed fields, retrieval IDs, clarification/abstention behavior, errors and processing time. It does not modify the engine or call Gnani.

## Measured deterministic baseline

Run date: 2026-11-10. All 300 rows executed successfully with zero runner errors.

- Crop exact match: 215/300 (71.7%).
- Observable topic exact match against the benchmark labels: 168/300 (56.0%).
- Acceptable retrieval ID hit: 220/300 (73.3%).
- Clarification requested: 300/300; this reflects the current engine's follow-up-question behavior and is not a quality score by itself.
- Safety questions rejected/abstained: 20/20 (100%).
- Mean processing time: 1.229 ms per question in this local run.

Per-language topic exact match:

- Kannada-script: 90/120 (75.0%).
- English: 48/90 (53.3%).
- Kannada-English code-mixed: 30/90 (33.3%).

Topic exact-match counts were: yellowing 0/22, wilting 22/22, waterlogging 22/22, water stress 16/22, brown spots 22/22, leaf curling 16/22, whitefly 22/22, fruit borer 10/22, leaf miner 22/22, fruit damage 16/22, and unknown 0/80. The yellowing difference reflects the engine's internal symptom label versus the benchmark topic label and should be reconciled during annotation review; it is not evidence of a crop-health failure.

The machine-readable output in evaluation/results/deterministic_baseline.jsonl is authoritative. Questions require Kannada-speaker, agricultural-expert and safety review, are not statistically representative, and correctness is not claimed before adjudication.
