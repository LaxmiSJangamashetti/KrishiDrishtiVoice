# Phase 1 Language Understanding Contract — Version 1 Draft

**Status:** Approved Version `1.0.0`. This contract is technology-independent and does not alter the current parser.

## 1. Responsibility and boundary

Language Understanding (LU) turns a farmer message and explicitly permitted conversation facts into evidence-traceable structured observations. It may identify a farmer's crop, pest, disease, symptom, or unsafe-request *mention*. It never verifies a finding, diagnoses disease, invents observations/facts, retrieves sources, recommends management, or gives chemical/fertilizer instructions.

The downstream safety validator owns refusal/escalation. The agricultural engine owns source-backed guidance.

## 2. Input

| Field | Type | Required | Rule |
|---|---|---:|---|
| `message_id` | string | yes | Unique within session. |
| `original_text` | string | yes | Immutable, non-empty user expression/transcript. |
| `input_channel` | enum | yes | `text` or `speech_transcript`; does not establish accuracy. |
| `interaction_type` | enum | yes | `initial_report`, `follow_up_response`, `correction`, `repetition`, `other`; message-level conversational role only. |
| `language_hint` | string/null | no | UI/STT hint, not ground truth. |
| `conversation_context` | object/null | no | Approved prior observation/follow-up references only. |

Input channel and interaction type are independent. Intent describes farmer purpose and must not duplicate either field. A message may carry several observations with different observation-level relationships; `interaction_type` never forces one relationship onto all of them.

## 3. Output envelope

`schema_version` is `1.0.0`. Breaking changes require a new major version; additive optional fields require a minor version. Consumers must fail safely on incompatible major versions.

| Field | Required | Meaning |
|---|---:|---|
| `message_id`, `original_text`, `normalized_text` | yes | Input identity and auditable derived text. |
| `language` | yes | `{primary, code_mixed, evidence, confidence}`. |
| `intents` | yes | Array of zero or more independently evidenced farmer purposes; may contain `UNKNOWN`. |
| `observations` | yes | Crop, symptom, plant part, pest/disease mention, soil/irrigation, stage, time, severity, spread, location, fertilizer mention. |
| `conversation_delta` | yes | New/updated/superseded references and contradictions. |
| `ambiguities`, `missing_information` | yes | Unresolved alternatives and only relevant missing fields. |
| `follow_up` | yes | Candidates and state; may be empty. |
| `confidence` | yes | Nullable stage-specific confidence. |
| `abstention` | yes | Structured decision not to assert/proceed. |
| `lu_safety_flags` | yes | Request-risk flags for downstream validator. |

## 4. Evidence and observations

### Evidence object

```json
{"message_id":"m-17","phrase":"ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ","origin":"current_message","start":null,"end":null}
```

`message_id` and exact `phrase` are required for every extracted value. `origin` is `current_message` or `conversation_context`. Multiple evidence objects are permitted. `start`/`end` are optional future offsets; any implementation that populates them must document its Unicode indexing convention.

### Observation object

```json
{"observation_id":"obs-m17-01","kind":"symptom","farmer_mention":"ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ","normalized_value":"leaf_yellowing","extraction_status":"extracted","polarity":"absent","validity":"active","relationship":"new","references":[],"evidence":[{"message_id":"m-17","phrase":"ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ","origin":"current_message","start":null,"end":null}],"confidence":null}
```

`observation_id` is stable within a session. `kind` is `crop`, `crop_variety`, `plant_part`, `symptom`, `pest_mention`, `disease_mention`, `growth_stage`, `soil`, `irrigation`, `fertilizer_mention`, `location`, `duration`, `severity`, `spread`, or `other`. Every reference must resolve to an observation in permitted conversation context or the current output. An unresolved reference is a schema-validation failure: it must not be ignored, and LU must safely abstain or clarify rather than apply the relationship.

### Value representation by kind

| Kind | `normalized_value` representation | Attribute link rule |
|---|---|---|
| `crop`, `plant_part`, `soil`, `irrigation` | Controlled vocabulary value, for example `tomato`, `leaf`, `dry`, `standing_water`. | Independent fact unless it describes a symptom. |
| `symptom` | Controlled observation label, for example `leaf_yellowing`. | May reference supporting plant-part, duration, severity, or spread observations. |
| `duration`, `severity`, `spread` | Normalized text/value, for example `three_days`, `severe`, `field_wide`. | `describes_observation_id` is required when it qualifies a symptom. |
| `location`, `growth_stage`, `crop_variety` | Controlled value or preserved phrase. | May remain general session context. |
| `fertilizer_mention`, `pest_mention`, `disease_mention` | Farmer-reported mention; never verified finding. | May reference its affected observation when explicit. |

`describes_observation_id` is an optional single observation reference. It links a related attribute to the symptom it qualifies without nesting or duplicating that attribute. It is required only when the evidence makes that relationship explicit.

### Separate semantics

| Field | Enum | Meaning |
|---|---|---|
| `extraction_status` | `extracted`, `ambiguous`, `unknown`, `unavailable` | Ability to represent a value from evidence. |
| `polarity` | `present`, `absent`, `uncertain`, `not_applicable` | Assertion about a symptom only. |
| `validity` | `active`, `superseded`, `contradicted`, `historical` | Current usability of a fact. |
| `relationship` | `new`, `repeated`, `confirmed`, `corrects`, `contradicts`, `none` | Relationship to prior observation IDs. |

`repeated` is a relationship, never an extraction status. Polarity never changes merely because an observation is repeated or corrected.

Validity semantics: `active` is currently usable information; `superseded` was explicitly corrected or replaced; `contradicted` has conflicting evidence that remains unresolved; `historical` was previously valid but is no longer current. An `extraction_status` of `extracted` only means a value was obtained from evidence—it does not imply high confidence. Confidence is independent and remains null unless a documented method populates it.

`farmer_mention` preserves what the farmer said. A `pest_mention` or `disease_mention` can be extracted but is never an independently verified finding.

## 5. Corrections and contradictions

A correction targets exact previous `observation_id` values in `references`; it never deletes unrelated facts. If earlier observations are yellow leaves (`obs-01`) and wilting (`obs-02`), then “leaves are not yellow; they have white spots; plant is still wilting” makes `obs-01` `superseded`, adds active white-spots observation with `relationship: corrects` and `references:["obs-01"]`, and retains `obs-02` active with a current confirmation reference.

`conversation_delta` lists new, updated, superseded IDs and contradiction pairs. Evidence for superseded facts remains available for audit.

## 6. Normalization and context

Permitted normalization: Unicode normalization, meaningful case/whitespace/punctuation cleanup, and reviewed aliases/ASR variants that preserve evidence and negation. Prohibited: deleting/reversing negation; collapsing distinct symptoms without ambiguity; silently correcting crop/pest/disease; replacing original text; translating away evidence; or assigning diagnosis.

Each missing field is `not_mentioned`, `unknown`, `ambiguous`, `not_required`, or `required_to_proceed`. Only ambiguous or required fields normally create follow-ups.

## 7. Intent, follow-ups, confidence, abstention

`intents` is a collection, not a primary-intent choice. Each item has `value`, `evidence`, `extraction_status`, and nullable `confidence`. Initial values are `REPORT_CROP_PROBLEM`, `ASK_AGRICULTURAL_INFORMATION`, `ASK_MANAGEMENT_ADVICE`, `ASK_CROP_INFORMATION`, `ASK_WEATHER`, `ASK_MARKET_PRICE`, `ASK_HARVEST_PRICE_FORECAST`, `ASK_PREVENTIVE_ADVICE`, and `UNKNOWN`. One message may report symptoms and request management advice without forcing priority between them.

A follow-up candidate has `follow_up_id`, `target_field`, `reason`, `question`, `expected_answer_type`, and `state`: `proposed`, `asked`, `answered`, `unresolved`, `resolved`, or `irrelevant`. Allowed transitions are `proposed -> asked`; `asked -> answered` when any answer arrives; `answered -> resolved` when the answer satisfies the target; `answered -> unresolved` when it is insufficient/ambiguous; and any non-final state -> `irrelevant` when correction or context change makes the target unnecessary. A proposed candidate may become irrelevant before being asked. An answered question keeps its original ID and remains in history. An insufficient answer may create a new, more specific follow-up with a new ID; the earlier question must not be repeated verbatim. Resolved and irrelevant questions remain in history. Reopening a target after correction must be explicit and reference the correction and prior target field.

Confidence is nullable and stage-specific: `language_detection`, `intent_extraction`, `observation_extraction`, and `context_resolution`. Retrieval relevance belongs to a future retrieval/RAG module, not LU. A populated value must declare a documented method/version. It is never disease probability and no arbitrary score is allowed.

```json
{"required":true,"reason_codes":["INSUFFICIENT_EVIDENCE"],"missing_information":[{"field":"crop","state":"required_to_proceed"}],"safe_clarification":"Which crop are you observing?"}
```

`abstention.required` is true only when LU cannot safely assert a needed interpretation. Reason codes: `INSUFFICIENT_EVIDENCE`, `AMBIGUOUS_ENTITY`, `CONFLICTING_CONTEXT`, `UNSUPPORTED_LANGUAGE_FORM`, `SCHEMA_VALIDATION_FAILED`, `MODEL_OUTPUT_UNVERIFIABLE`. A crop-needed clarification uses `INSUFFICIENT_EVIDENCE` with missing field `crop`; `CROP_REQUIRED` is not a contract reason code.

## 8. Safety and integration

LU can flag `REQUESTS_PESTICIDE_DOSE`, `REQUESTS_CHEMICAL_MIXING`, `REQUESTS_FERTILIZER_QUANTITY`, `REQUESTS_GUARANTEED_DIAGNOSIS`, and `REQUESTS_UNSUPPORTED_TREATMENT`; it must not answer them. Before agricultural retrieval, LU output requires deterministic schema, evidence, correction-reference, polarity, and safety validation. A future model may propose output but cannot bypass these controls.
