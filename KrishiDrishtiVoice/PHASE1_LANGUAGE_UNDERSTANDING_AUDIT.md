# KrishiDrishti AI — Phase 1, Task 1: Language Understanding Audit

**Status:** Audit only — no production logic, knowledge records, tests, API configuration, or credentials were changed.  
**Audit date:** 2026-11-19  
**Evidence labels:** **Observed** = executed against the current code; **Code inspection** = established by reading source; **Inference** = reasoned from observed code/results; **Recommendation** = future work, not implemented.

## 1. Executive summary

The current system is a small, local, deterministic tomato triage engine. It has important strengths worth retaining: Unicode-safe loading, a deliberately limited crop scope, conservative disease language, source-backed retrieval, explicit safety refusal patterns, and focused Kannada patterns for several high-value observations. It is not a general Kannada language-understanding system.

**Observed:** all 36 existing automated tests pass. The supplied 20 Kannada inputs were executed. Only one received a complete tomato-specific retrieval response; most unrecognized Kannada inputs conservatively received the generic Kannada clarification. This is safer than fabricated guidance, but it does not amount to robust farmer-language understanding.

The principal technical gap is structural: `parse_question()` returns exactly one crop and one symptom. There is no language identification, tokenization, intent classifier, negation/polarity representation, multi-symptom representation, duration/severity/context extraction, dialogue state, or calibrated confidence. Retrieval is lexical substring scoring, not semantic retrieval.

**Verdict:** retain the deterministic safety boundary, knowledge retrieval, transparent fallback, and curated phrase patterns. Improve deterministic normalization, aliases, polarity, multi-observation extraction, and context first. An SLM is justified only after those controls and an adjudicated benchmark are in place, principally for flexible Kannada phrasing, code-switching, STT variation, and context-sensitive interpretation—not for agricultural recommendations.

## 2. Scope and method

- Read: `app.py`, `agriculture_engine.py`, `gnani_service.py`, `knowledge.json`, all six test modules, `evaluation/reports/PHASE0_BASELINE_REPORT.md`, `evaluation/schemas/question_interpretation.schema.json`, and `SLM_FEASIBILITY_STUDY.md`.
- Executed locally, without network calls: the 20 supplied Kannada inputs; eight targeted negation/multi-symptom/code-switch/STT-like inputs; and `python -m unittest discover -s tests -q`.
- Existing baseline report was read, not rerun: it records 300 draft examples run on 2026-11-10, with 56.0% topic exact match overall and 33.3% for Kannada-English code mix. Its labels require human agricultural and Kannada-speaker review.

## 3. Current architecture

```text
Audio upload/recording or manual text
  -> app.py: transcribe_audio() for selected supported STT language, or process_text()
  -> original transcript stored in Streamlit session state
  -> agriculture_engine.parse_question()
  -> agriculture_engine.search() local JSON lexical ranking
  -> agriculture_engine.build_guidance() safety gate, fallback or source-backed guidance
  -> Streamlit transcript / parser / retrieval / guidance display
  -> optional TTS only from existing validated guidance
```

### Implementation inventory

| Component | Status | Evidence |
|---|---|---|
| Voice STT transport | Implemented | `gnani_service.transcribe_audio`; not evaluated for linguistic accuracy here. |
| Transcript preservation | Implemented | `app.process_text` stores original text in `st.session_state["transcript"]`. |
| Normalization | Partially implemented | `agriculture_engine.normalize_text`: NFC, `casefold`, trim, whitespace collapse. |
| Kannada phrase processing | Partially implemented | `_parse_kannada_symptom` uses ordered regular-expression patterns. |
| English phrase processing | Partially implemented | `SYMPTOM_PATTERNS` uses ordered substring phrases. |
| Tokenization / morphology | Not implemented | No token stream, lemmatizer, stemmer, transliteration, or spell correction. |
| Language identification | Not implemented | Kannada-script detection is only a Unicode-range test in `build_guidance`. |
| Intent extraction | Not implemented | No intent field/function. Safety categories are not farmer intents. |
| Crop extraction | Partially implemented | Tomato aliases only, by substring in `parse_question`; `identify_crop` searches `knowledge["crops"]`, but current JSON has no `crops` key. |
| Plant part extraction | Not implemented as structured data | Plant-part words occur only inside selected patterns/keywords. |
| Symptom extraction | Partially implemented | Exactly one ordered symptom label is returned. |
| Context/duration/severity extraction | Not implemented | No fields/functions. |
| Retrieval | Implemented, lexical only | `search`: crop + keyword substring scores, then preferred record bonus. |
| Ambiguity handling | Partially implemented | Unknown Kannada gets a fixed Kannada clarification; otherwise generic fallback. |
| Follow-up selection | Partially implemented | `_questions` de-duplicates questions from top records; no state. |
| Safety validation | Implemented, phrase-based | `validate_safety` checks hard-coded English/Kannada phrases before retrieval. |
| Confidence | Not implemented | `Match.score` is retrieval rank evidence, not calibrated understanding confidence. |

## 4. Actual language-understanding pipeline

| Stage | Implementation and input/output | Status, limitations, tests |
|---|---|---|
| Input | `app.process_text(text, language)` receives manual text or verified STT transcript. | Implemented. App does not independently detect language. |
| Normalize | `normalize_text(str) -> str`: NFC, casefold, collapse whitespace. | Partial. It preserves Kannada but does not normalize colloquial spellings, endings, phonetic forms, Romanization, fillers, or negation. Unicode normalization test exists. |
| Crop + symptom parse | `parse_question(question) -> {crop, symptom, normalized_text}`. Tomato is substring aliases; symptom is first Kannada regex hit, otherwise first matching English/substrings. | Partial. Single-valued output, ordered matching, not a semantic parse. Parser tests cover predefined wording. |
| Safety | `validate_safety(question) -> category | None`. | Implemented for listed dosage/mixing/guarantee/treatment phrases. Safety tests cover exact-ish examples. |
| Retrieval | `search(question) -> list[Match]`, local `knowledge.json` entries. Score = matching crop + explicit keyword phrases + optional preferred-ID bonus. | Implemented but lexically brittle. No semantic similarity threshold or contradiction check. |
| Guidance | `build_guidance(question, language) -> dict`. Safety refusals precede parser. Unknown Kannada gets a fixed Kannada fallback; unmatched/non-tomato gets English fallback. | Partial. It does not expose parser ambiguity or scores; it may return an English fallback for Kannada that had a symptom but lacked crop. |
| UI | `app.py` displays parser crop/symptom, match score, sources, follow-ups. | Implemented. It does not display intent, plant part, polarity, multiple symptoms, confidence, or dialogue state. |

## 5. Kannada assessment

### What currently works

**Observed/code inspection:** conservative patterns cover examples of tomato spelling aliases (`ಟೊಮೆಟೋ`, `ಟೊಮಾಟೊ`, `ಟಮೋಟೊ`), leaf yellowing, wet/dry soil, white insects under leaves, fruit holes, leaf-miner-like trails, brown spots, leaf curling, and some wilting forms. The existing dedicated Kannada tests cover 18 supported phrase variations and check that retrieval does not claim a diagnosis.

**Observed:** supplied input 1 (`... ಎಲೆ ಹಳದಿ ಆಗ್ತಿದೆ`) parsed tomato + `leaf_yellowing`, selected `tomato-leaf-yellowing-001`, and generated retrieval-backed guidance. The code therefore recognizes some colloquial `ಆಗ್ತಿದೆ` phrasing when the crop alias is supported.

### What does not currently generalize

- **Crop omission:** inputs 2–10 and 12–20 largely have no explicit tomato token. `build_guidance` requires a crop before source-backed advice, even where a symptom was recognized. This is conservative but loses conversational context because no prior crop state is used.
- **Alias gap:** `ಟೊಮೇಟೊ` in input 11 is not one of the three recognized aliases, so crop is absent.
- **Colloquial inflection gap:** `ಬಾಡ್ತಾ`, `ಒಣಗ್ತಾ`, and `ಸೊರಗಿದೆ` did not match patterns expecting forms such as `ಬಾಡುತ್ತ`/`ಒಣಗುತ್ತ`.
- **Concept coverage gap:** flower drop, fruit set failure, burn-like leaves, pale/white leaf surface, black spots, stunting, leaf drop, pest observations without whitefly wording, and field-wide spread have no structured representation.
- **No dialect/phonetic/STT repair:** plausible near-form `ಟೊಮೆಟೊ` was not recognized as tomato. This is an observed spelling/transcription robustness failure, not a Gnani STT assessment.
- **No word segmentation or morphology:** patterns depend on specific grapheme sequences and adjacent wording; they are not Kannada lemma/morphology analysis.

## 6. Executed evaluation: supplied 20 Kannada inputs

Expected meanings below are human interpretations for audit purposes, not agricultural diagnoses. “Correct” assesses language interpretation/retrieval behavior, not diagnosis accuracy.

| ID | Input (abridged) | Style | Expected observation | Actual output | Status / failure reason |
|---:|---|---|---|---|---|
| 1 | ಟೊಮೆಟೋ…ಎಲೆ ಹಳದಿ ಆಗ್ತಿದೆ | Colloquial | tomato, leaf yellowing | tomato; `leaf_yellowing`; yellowing record | **CORRECT** |
| 2 | ಎಲೆಗಳು ಹಳದಿಯಾಗಿವೆ | Ambiguous | leaf yellowing; crop omitted | symptom recognized; no crop; English generic fallback | **AMBIGUOUS — HANDLED INCORRECTLY**: loses Kannada/context-aware clarification |
| 3 | ಗಿಡ ಸೊರಗಿದೆ | Colloquial, ambiguous | whole-plant decline/wilting-like | no symptom; Kannada fallback | **AMBIGUOUS — HANDLED CORRECTLY** |
| 4 | ಗಿಡ ಬಾಡ್ತಾ ಇದೆ | Colloquial | wilting-like | no symptom; Kannada fallback | **PARTIALLY CORRECT**: safe fallback, missed observation |
| 5 | ಗಿಡ ಒಣಗ್ತಾ ಇದೆ | Colloquial | drying/wilting-like | no symptom; Kannada fallback | **PARTIALLY CORRECT** |
| 6 | ಎಲೆ ಮೇಲೆ ಕಲೆ ಬಂದಿದೆ | Informal, ambiguous | leaf spots | no symptom; low lexical yellowing match; Kannada fallback | **AMBIGUOUS — HANDLED CORRECTLY** |
| 7 | ಎಲೆ ಸುಟ್ಟ ಹಾಗೆ | Informal | burn/scorch-like leaf symptom | no symptom; low lexical match; Kannada fallback | **NOT SUPPORTED** |
| 8 | ಕಾಯಿಗೆ ಹುಳು ಹಿಡಿದಿದೆ | Informal | fruit pest/damage | no symptom; Kannada fallback | **NOT SUPPORTED** |
| 9 | ಹೂ…ಕಾಯಿ ಆಗ್ತಿಲ್ಲ | Colloquial | poor fruit set | no symptom; Kannada fallback | **NOT SUPPORTED** |
| 10 | ಹೂಗಳು ಉದುರುತ್ತಿವೆ | Formal/incomplete | flower drop | no symptom; Kannada fallback | **NOT SUPPORTED** |
| 11 | ಟೊಮೇಟೊ ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತಿಲ್ಲ | Informal | tomato poor growth | no crop/symptom; Kannada fallback | **INCORRECT**: unsupported tomato spelling and no growth representation |
| 12 | ಗಿಡಕ್ಕೆ ಏನೋ ಸಮಸ್ಯೆ | Ambiguous | unspecified plant problem | no symptom; Kannada fallback | **AMBIGUOUS — HANDLED CORRECTLY** |
| 13 | ಎಲೆ ಕೆಳಗಡೆ ಮಡಚಿಕೊಳ್ಳುತ್ತಿದೆ | Colloquial | leaf curling/downward curl | no symptom; low lexical match; Kannada fallback | **PARTIALLY CORRECT**: no unsupported diagnosis, but missed phrase |
| 14 | ಎಲೆ ಮೇಲೆ ಬಿಳಿ ಬಿಳಿಯಾಗಿ | Ambiguous | white coating/discoloration | no symptom; Kannada fallback | **AMBIGUOUS — HANDLED CORRECTLY** |
| 15 | ಗಿಡದಲ್ಲಿ ಕಪ್ಪು ಕಲೆಗಳು | Informal | dark spots; plant part unclear | `brown_spots`; no crop; English fallback | **AMBIGUOUS — HANDLED INCORRECTLY**: color conflation + language-inappropriate fallback |
| 16 | ಬೆಳವಣಿಗೆ ನಿಂತ ಹಾಗೆ | Informal | stunting/growth arrest | no symptom; Kannada fallback | **NOT SUPPORTED** |
| 17 | ಎಲೆ ಒಣಗಿ ಕೆಳಗೆ ಬೀಳುತ್ತಿದೆ | Informal | leaf drying/drop | no symptom; Kannada fallback | **NOT SUPPORTED** |
| 18 | ನೀರು ಹಾಕಿದರೂ…ಚೇತರಿಸಿಕೊಳ್ಳುತ್ತಿಲ್ಲ | Contextual | non-response after irrigation | no symptom; lexical water-stress record, but no guidance due crop absent | **PARTIALLY CORRECT**: context not structured or acted upon |
| 19 | ಸಣ್ಣ ಸಣ್ಣ ಹುಳುಗಳಿವೆ | Informal | visible pest presence | no symptom; Kannada fallback | **NOT SUPPORTED** |
| 20 | ಎಲ್ಲಾ ಗಿಡಗಳಿಗೂ ಇದೇ ಸಮಸ್ಯೆ | Contextual/ambiguous | distribution/severity (field-wide) | no symptom; Kannada fallback | **PARTIALLY CORRECT**: safe clarification, distribution ignored |

**Executed summary:** 1/20 correct; 2/20 partially correct; 5/20 ambiguity handled conservatively; 8/20 not supported; 2/20 ambiguity handled incorrectly; 2/20 incorrect. These are an illustrative audit set, not a statistical language benchmark.

## 7. Failure analysis

### A. Normalization and spelling

**Observed:** normalization makes only Unicode/whitespace changes. It does not map `ಟೊಮೇಟೊ` to `ಟೊಮೆಟೋ`, `ಬಾಡ್ತಾ` to `ಬಾಡುತ್ತ`, or `ಒಣಗ್ತಾ` to `ಒಣಗುತ್ತ`. Repeated characters, transliteration, punctuation variants, fillers, and speech-recognition substitutions are unhandled.

### B. Semantics and context

**Code inspection:** `parse_question` selects the first matching symptom in an ordered tuple. It does not compare meanings or preserve evidence spans. Therefore different expressions must match predeclared strings/regexes; keyword matches are not semantic understanding.

**Observed:** `ಗಿಡದಲ್ಲಿ ಕಪ್ಪು ಕಲೆಗಳು` becomes `brown_spots` because the regex permits `...ಕಲೆ`; this conflates “black” with “brown” and does not know whether spots are on leaves, stems, or fruit.

### C. Negation

**Observed:** `ಕೀಟ ಇಲ್ಲ` is not modeled as negative; the yellowing case happened to retrieve yellowing because it was first. `ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ` still parsed `leaf_yellowing` and produced yellowing guidance. This is a material false-positive risk.

### D. Multiple symptoms

**Observed:** “yellow leaves, wilting, and flower drop” produced only `leaf_yellowing`; wilting and flower drop were discarded. The current return type cannot represent multiple symptoms.

### E. Code switching

**Observed:** `Tomato plant ಎಲೆ yellow ಆಗ್ತಿದೆ` worked through English crop/symptom substrings. Water-excess and spots mixed examples fell back because `water ಜಾಸ್ತಿ` and `spots` lack matching context patterns. `Tomato fruit ನಲ್ಲಿ insects ಇವೆ` retrieved general pest guidance. Support is accidental overlap, not deliberate code-switch processing.

### F. STT error tolerance

**Observed:** the near spelling `ಟೊಮೆಟೊ` was not recognized as tomato even though yellowing was detected. There is no post-STT correction/alias confidence system. This audit did not measure Gnani STT error rates.

## 8. Intent and entity extraction assessment

| Proposed capability | Current status | Evidence |
|---|---|---|
| REPORT_CROP_PROBLEM | Implicit only | Most input is treated as a problem statement; no intent output. |
| IDENTIFY_DISEASE | Not extracted | The engine intentionally avoids confirmed diagnosis. |
| ASK_TREATMENT / quantity | Safety phrase detection only | Unsafe treatment/dose phrases are blocked; no safe request intent classification. |
| ASK_IRRIGATION / nutrient / cultivation / price / weather / harvest | Not implemented | No intent patterns or supporting knowledge scope. |
| REPORT_PEST | Partial | `insects`/whitefly/fruit-borer/leaf-miner phrase patterns only. |
| Crop | Partial | Tomato aliases only; crop omitted in most supplied inputs. |
| Variety, growth stage, duration, severity, location, quantity, time | Not implemented | No parser output fields. |
| Plant part | Not structured | Only incidental inside regexes/keywords. |
| Pest/disease names | Partial lexical | Observation labels and knowledge-record names; no disease entity extraction. |
| Soil/irrigation condition | Partial lexical | Waterlogging/water-stress patterns; not an extracted context object. |

## 9. Follow-up, confidence, and uncertainty

### Follow-ups

**Observed/code inspection:** unknown Kannada always receives the same four questions. Retrieved matches receive up to six de-duplicated questions from the top three records. The engine does not track answered fields, question history, priority, or sufficiency; `app.py` keeps a display history only. Repeated questions are possible across turns.

**Recommendation:** select one highest-information-gain question at a time from missing structured fields, record answer state, and prohibit a question whose field has evidence. Keep “do not diagnose” and referral behavior independent of conversational completeness.

### Confidence and uncertainty

**Observed:** `Match.score` is an uncalibrated lexical ranking integer (crop + keyword hits + preferred record bonus). It is not returned as interpretation confidence and must not be interpreted as disease probability. The uncertainty statement is a fixed safety warning, not a confidence estimate.

**Recommended separation (no numerical values proposed):** language/normalization confidence; crop extraction confidence; symptom evidence confidence; retrieval relevance; and agricultural assessment confidence. Each must carry evidence and abstention/fallback rules.

## 10. Safety and knowledge connection

**Retain:** `build_guidance` calls `validate_safety` before retrieval, avoids disease confirmation, keeps source records separate, and returns referral/safe-initial-action content. Existing tests cover chemical quantities, mixing, guaranteed diagnosis, unsupported treatment, and offline operation.

**Limitations:** phrase safety rules do not prove coverage of colloquial Kannada, paraphrases, negated requests, code mixing, or indirect treatment requests. Retrieval may return records from substring overlap even when parser output is absent; the Kannada fallback hides those records when symptom is absent, which is safer than presenting them as an answer.

## 11. Existing test coverage and gaps

**Observed:** 36 tests pass. Tests cover known English and Kannada wording, retrieval, selected record prioritization, source metadata, safety phrases, offline engine operation, and TTS request configuration.

Missing or insufficient language-understanding tests:

- Colloquial/dialectal Kannada and spelling/transcription variants beyond current patterns.
- Crop omission followed by conversational crop context.
- Negation and polarity (`ಇಲ್ಲ`, `ಆಗಿಲ್ಲ`, `ಕಡಿಮೆ ಇಲ್ಲ`).
- Multiple symptoms and independently preserved evidence.
- Plant part, flower/fruit set, stunting, spread, duration, severity, and time context.
- Deliberate code-switch/Romanized Kannada categories.
- Counterfactuals where a keyword should *not* activate a record.
- Follow-up state, redundancy prevention, and sufficient-information stopping.
- STT transcript perturbation resilience; current tests do not exercise STT output variants.
- Human adjudication of benchmark labels; the Phase 0 dataset/report is explicitly draft.

## 12. SLM feasibility assessment

The existing `SLM_FEASIBILITY_STUDY.md` already concludes that model selection is not justified from model cards alone and recommends a benchmark-first hybrid path. This audit agrees.

| Approach | Strengths | Limits / risks | Assessment |
|---|---|---|---|
| Current deterministic rules | Fast, offline, inspectable, safe fallback, no hallucinated recommendations. | Exact-phrase brittleness; no polarity/context/multi-symptom handling; poor code mixing. | Retain as safety and baseline layer. |
| Expanded deterministic dictionaries + context rules | Can address aliases, common inflections, negation, explicit phrases, and high-value contexts cheaply/offline. | Vocabulary maintenance; weak on unseen paraphrases and long free speech. | First implementation priority. |
| SLM interpretation | Potentially better flexible Kannada/code-mix paraphrase and structured extraction. | Must measure Kannada agricultural accuracy; RAM/latency/licensing; hallucinated structure/diagnosis; unreliable JSON without validation. | Research only after deterministic benchmark improvements. |
| Hybrid | Deterministic preprocessing/validation/safety + model proposes evidence-bound structured observations + deterministic retrieval. | More components and evaluation burden. | Best future architecture if acceptance gates pass. |

**Recommendation:** do not select or download a model in Task 2. First create gold-reviewed language data and deterministic structured-output controls. Later compare an Indic-language encoder (e.g., task-specific extraction) and a small generative model only on unseen Kannada/code-mixed examples, Windows CPU and future Android constraints. The SLM must never author agricultural recommendations, sources, doses, or diagnoses.

## 13. Recommended future architecture

```text
Original transcript (immutable)
  -> deterministic script/language & code-switch detector
  -> deterministic Kannada/English normalization + alias/ASR-variant map
  -> token/evidence-span representation
  -> polarity + multi-observation extraction
  -> context/intent rules for known high-risk asks
  -> optional SLM/encoder semantic extractor (strict JSON schema; evidence required)
  -> deterministic schema, evidence, conflict, and safety validator
  -> clarification state / next-question selector
  -> deterministic knowledge retrieval (source-backed only)
  -> agricultural guidance + referral/safety gate
```

| Component | Recommended method |
|---|---|
| Unicode normalization, aliases, safety, schema validation | Deterministic |
| Kannada/English phrase dictionaries and common ASR variants | Dictionary + rule based |
| Negation, quantities, duration, basic plant part/context | Rules first; evidence spans required |
| Flexible paraphrase, code-mix semantic candidates | Optional model-assisted, validated against deterministic constraints |
| Crop-health advice, sources, pesticides/fertilizer quantities | Curated deterministic knowledge + mandatory safety validation |

## 14. Proposed structured output contract

This supersedes neither current code nor the existing evaluation schema; it is a future design proposal.

```json
{
  "schema_version": "2.0-draft",
  "original_text": "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆ ಹಳದಿ ಆಗ್ತಿದೆ",
  "normalized_text": "...",
  "language": {"primary": "kn-IN", "code_mixed": false, "evidence": []},
  "intent": {"value": "REPORT_CROP_PROBLEM", "evidence": [], "confidence": null},
  "crops": [{"value": "tomato", "evidence": [{"text": "ಟೊಮೆಟೋ", "start": null, "end": null}], "confidence": null}],
  "crop_variety": {"value": null, "evidence": []},
  "plant_parts": [{"value": "leaf", "polarity": "positive", "evidence": []}],
  "symptoms": [{"value": "yellowing", "polarity": "positive", "severity": null, "duration": null, "evidence": [], "is_diagnosis": false}],
  "context": {"growth_stage": null, "irrigation": [], "soil": [], "weather": [], "location": null, "distribution": null, "time_references": []},
  "ambiguities": [],
  "missing_information": [],
  "follow_up_candidates": [],
  "confidence": {"language": null, "crop": null, "extraction": null, "retrieval": null},
  "requires_follow_up": true,
  "abstention": false,
  "warnings": ["Language understanding does not diagnose crop disease."]
}
```

Requirements: preserve original text; support arrays and positive/negative polarity; store evidence rather than only labels; distinguish unknown from absent; never emit a disease diagnosis from this layer; and validate all model outputs against a versioned JSON schema.

## 15. Prioritized improvement backlog and Phase 1 plan

| Priority / ID | Objective | Files involved | Approach / tests | Complexity / acceptance criteria |
|---|---|---|---|---|
| P0 / LU-01 | Freeze language-understanding contract and gold rubric | New schema/docs/evaluation data only | Reconcile existing Phase 0 label names; Kannada + agricultural review of a held-out set; include evidence/polarity rules. | Medium. Versioned contract and adjudicated test subset; no product behavior change. |
| P0 / LU-02 | Add audit regression suite | New test module(s); no production change initially | Encode the 20 audit inputs plus negation, multi-symptom, code mix, ASR variants as expected current behavior before changing logic. | Low. Tests distinguish supported, clarification, abstention, and incorrect retrieval. |
| P0 / LU-03 | Deterministic normalization/alias design | `agriculture_engine.py`, new reviewed lexicon | Define bounded aliases for crop spellings, frequent colloquial forms, and code-switch forms; test false-positive pairs. | Medium. No change unless every alias has review + regression evidence. |
| P0 / LU-04 | Structured parser refactor | `agriculture_engine.py`, tests, schema | Add a backward-compatible internal observation representation with evidence and multiple symptoms; preserve old adapter until callers migrate. | High. Existing 36 tests pass; multiple observations and no-diagnosis contract tested. |
| P1 / LU-05 | Polarity/context extraction | Parser, tests, controlled lexicon | Add negation window/evidence and explicit plant-part/soil/distribution/duration extraction. | High. Negated symptom never becomes a positive observation without an ambiguity marker. |
| P1 / LU-06 | Clarification state machine | New dialogue-state module + app integration later | Select unanswered, highest-value field; prevent repeats; preserve farmer answers. | Medium. Tested multi-turn paths and stop conditions. |
| P1 / LU-07 | Retrieval evidence and thresholds | Engine + tests | Rank only evidence-supported records, surface match rationale, and apply abstention threshold. | Medium. No irrelevant tomato record on crop-omitted/negated counterfactuals. |
| P2 / LU-08 | Offline model evaluation | Evaluation harness only; no app integration | Compare deterministic baseline with a vetted encoder/SLM using reviewed unseen benchmark; measure JSON validity, latency, RAM, abstention, safety. | High. Acceptance gates met before integration. |
| P2 / LU-09 | Hybrid pilot | New adapter/validator behind feature flag | Model proposes structured observations only; deterministic validator/retrieval remains authoritative. | High. No unsafe recommendation or source fabrication; tested fallback on malformed output. |

## 16. Risks and dependencies

- A Kannada-speaker and agricultural-domain reviewer are needed to adjudicate wording, intended observations, and acceptable follow-ups.
- The existing knowledge base is tomato-only; language parsing should not silently infer tomato from a generic plant mention.
- STT robustness requires real, consented transcript-error samples; this audit does not establish STT accuracy.
- Per-account voice support and language UI availability are unrelated to language-understanding capability.
- Any model work needs legal/license review, device benchmarks, data governance, and offline safety evaluation before deployment.

## 17. Acceptance criteria for Phase 1 completion

1. A reviewed, versioned structured-output contract exists.
2. An unseen, human-adjudicated Kannada/English/code-mixed evaluation set includes negation, multi-symptom, crop omission, and ASR-like variants.
3. Deterministic parser changes preserve existing safety and regression behavior while adding evidence, polarity, and multiple observations.
4. Crop omission never receives tomato-specific guidance unless crop context is explicit or safely retained in an approved conversation state.
5. Every retrieval has explainable lexical/semantic evidence and uncertainty remains visible.
6. Follow-ups are stateful, non-redundant, and stop when the required evidence is present.
7. Any model experiment passes structured-output, abstention, safety, latency, RAM, and offline gates against the deterministic baseline.

## 18. Final verdict and Task 2 recommendation

**Good enough to retain:** source-backed tomato records, offline deterministic retrieval, safety-first refusal, explicit uncertainty/referral, Unicode-safe persistence, known Kannada phrase coverage, and the evaluation harness.

**Fundamentally weak:** semantic interpretation beyond exact phrases; crop alias resilience; negation; multi-symptom/context/intent extraction; dialogue memory; code-switch and ASR tolerance; calibrated confidence.

**Improve first:** LU-01/LU-02 (reviewed contract and regression corpus), followed by LU-03/LU-04 (bounded normalization aliases and an evidence-preserving multi-observation parser). These improve reliability without introducing model uncertainty.

**Is an SLM justified?** Potentially, but not yet as a product dependency. It is justified as a later, benchmarked semantic-extraction comparator after deterministic controls and gold data exist. The hybrid design is technically preferable if it outperforms deterministic rules while retaining strict validation and safety authority.

**Recommended Task 2:** approve **LU-01 + LU-02**: define the versioned language-understanding contract and create a human-reviewable regression/evaluation corpus from this audit, without changing agricultural guidance or adding a model.
