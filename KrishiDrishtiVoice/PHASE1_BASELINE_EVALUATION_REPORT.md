# Phase 1 Provisional Baseline Evaluation

**These results are provisional measurements against an unapproved draft corpus. They do not establish real-world Kannada language-understanding accuracy or agricultural diagnostic accuracy.**

## Execution
- Corpus: `PHASE1_LANGUAGE_EVALUATION_CANDIDATE_V2.jsonl`; records: 130.
- Entry point: `agriculture_engine.parse_question(question)`. It returns only `crop`, one `symptom`, and `normalized_text`; it is local and does not call network, retrieval, or guidance.
- Unsupported contract fields: intents, polarity, evidence spans, plant parts, context, correction state, multi-symptom output, follow-up state, confidence.

## PROVISIONAL DRAFT-DATA metrics
- Crop exact match: 44/45 (97.8%).
- Single supported symptom hit: 31/61 (50.8%).
- Concrete incorrect symptom activations: 11.
- Parser exceptions: 0.
- Exclusions: {'UNCLASSIFIED_EMPTY_OBSERVATIONS': 52, 'unsupported_vocabulary': 2, 'insufficient_evidence': 7, 'legitimate_intent_only': 1}.

## Limitations and failures
The parser cannot express negation, multiple symptoms, evidence, context, correction, or intent. Consequently these capabilities are NOT_MEASURABLE, not scored as failures. Concrete lexical misclassification remains an error where a present expected symptom is comparable. Empty/unclassified draft annotations are excluded from observation scoring. Case-level outputs are in `evaluation/phase1_baseline_results.jsonl`.

## Priorities
Improve reviewed corpus labels before interpreting scores; then add deterministic polarity, multi-observation, crop alias, and context support. Production code was not modified.
