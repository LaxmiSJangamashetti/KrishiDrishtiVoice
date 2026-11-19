# Phase 1 Task 2 Report

## Finalized artifacts

- `PHASE1_LANGUAGE_UNDERSTANDING_CONTRACT.md`: model/vendor-independent LU boundary, fields, evidence, uncertainty, follow-up, safety, and integration rules.
- `PHASE1_LANGUAGE_EVALUATION_DATASET_SCHEMA.md`: JSONL field and annotation specification.
- `PHASE1_LANGUAGE_EVALUATION_SEED.jsonl`: 100 draft, Kannada-first evaluation records.
- `PHASE1_LANGUAGE_EVALUATION_GUIDELINES.md`: baseline, metric, safety-error, review, and regression guidance.
- `evaluation/validate_phase1_seed.py`: isolated JSONL validator; it imports no production code.

## Decisions

1. Language understanding records observations and evidence; it never diagnoses or recommends treatment.
2. Unknown, absent, ambiguous, contextual, and contradicted values are first-class states.
3. Symptoms are arrays with independently labeled polarity/evidence, preventing forced single-symptom interpretation.
4. Conversation context must be explicit and distinguish current-message facts from carried facts.
5. Metrics must stratify language, code mixing, and safety-critical negation errors; unavailable parser fields are not fabricated.

## Contract and validation result

The approved LU contract version is `1.0.0`. The corpus validator completed successfully: 100 records, 100 unique IDs, and 22 primary categories. It checks JSONL syntax, required legacy/contract fields, review status, polarity, observation validity, evidence message IDs/phrases, contract version, follow-up state, and same-record observation references. Structural validity does not establish semantic or agricultural correctness.

## Corpus limitations and human review

All records are `draft`. They have not received farmer, Kannada-speaker, agricultural-expert, or safety-review approval. Code-mixed, regional/colloquial, correction, contradiction, disease/pest mention, and unsafe-request records especially require Kannada-speaker and safety review; symptom/context interpretations require agricultural review. They are not a production benchmark and not agricultural advice.

## Recommendation for Task 3

First complete human review and expand the seed corpus to the agreed target across code-mix, negation, multi-symptom, context, and STT-like categories. Then build a non-production baseline runner that maps existing parser output only to fields it currently produces and explicitly marks all other metrics unavailable. Do not modify the parser before this review gate.

## Readiness and files changed

The corpus is structurally ready for a future baseline runner, but not trustworthy for semantic comparison until the draft labels receive independent review. Known ambiguity remains in colloquial wording, STT-like variants, crop omission, and whether a mention supports a controlled observation label.

Changed in Task 2B: `PHASE1_LANGUAGE_UNDERSTANDING_CONTRACT.md`, `PHASE1_LANGUAGE_EVALUATION_DATASET_SCHEMA.md`, `PHASE1_LANGUAGE_EVALUATION_SEED.jsonl`, `evaluation/validate_phase1_seed.py`, and this report.

## Production integrity

No production Python modules, frontend, knowledge base, API configuration, credentials, or existing tests were modified by Task 2.
