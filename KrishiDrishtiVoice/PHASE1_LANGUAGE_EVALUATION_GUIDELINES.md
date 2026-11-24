# Phase 1 Evaluation Guidelines

## Baseline method

Run each JSONL sentence through the current deterministic interfaces (`normalize_text`, `parse_question`, `identify_crop`, `search`, `build_guidance`) without changing parser behavior. Save one machine-readable result per input with parser output, record IDs/scores, guidance fallback, errors, implementation revision, and elapsed time. Missing parser fields are **unavailable**, not incorrect values fabricated for a metric.

Compare current fields only where an approved gold label maps to them: crop, one legacy symptom label, retrieval ID, safety abstention, and fallback/clarification. The future structured fields cannot be scored until an implementation produces them.

## Metrics

| Metric | Calculation | Notes |
|---|---|---|
| Intent exact accuracy | correct intent records / scored records | Unavailable for current parser. |
| Crop exact accuracy | exact crop matches / crop-scored records | Report omitted-crop cases separately. |
| Entity precision/recall/F1 | exact normalized entity spans or values vs gold | Compute by entity type and language. |
| Symptom precision/recall/F1 | set overlap of independently labeled symptoms | Do not reduce multi-symptom cases to first label. |
| Polarity accuracy | correct present/absent/uncertain labels / polarity-scored symptoms | Report false-positive negations separately. |
| Multi-symptom completeness | correctly recovered gold symptoms / total gold symptoms | A missing symptom is distinct from a wrong symptom. |
| Context retention accuracy | correct contextual values / context-scored values | Requires multi-turn harness. |
| Ambiguity detection | correctly flagged ambiguous cases / ambiguous gold cases | Also report unjustified ambiguity on clear inputs. |
| Follow-up appropriateness | human/adjudicator rating plus field coverage | A follow-up must target an unresolved field and avoid repeats. |
| Code-mix/STT robustness | each metric stratified by characteristic | Never merge into Kannada-only score. |
| False entity rate | unsupported extracted entities / all extracted entities | Safety-relevant. |

## Safety-critical reporting

Always separately count: a negated symptom extracted as present; invented crop/pest/disease; unsupported treatment/dose content; crop-specific retrieval with no crop evidence; and failure to abstain on unsafe quantity/mixing requests. These are release-blocking categories, not errors to hide in macro averages.

## Reproducibility and review workflow

1. Validate JSONL before a run.
2. Record Python version, source revision/hash if available, corpus version, command, timestamp, and no-network status.
3. Save per-record outputs and a summary without overwriting prior baselines.
4. Review failures by Kannada-language reviewer, agricultural reviewer where interpretation could imply crop facts, and safety reviewer for critical errors.
5. Correct gold annotations separately from parser changes; rerun both old and new versions for comparison.

## Regression gates

No parser change may lower approved-set safety performance, silently remove evidence, turn a negated symptom positive, or replace an abstention with unsupported guidance. Improvements must be reported by language, code-mix, difficulty, and review status.
