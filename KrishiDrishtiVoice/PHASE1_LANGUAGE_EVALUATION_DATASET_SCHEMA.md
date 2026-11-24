# Phase 1 Language Evaluation Dataset Schema

**Dataset status:** draft, human-reviewable seed set. It is not farmer-validated or agricultural-expert-validated.

## JSONL record fields

Contract-alignment fields required in each record: `contract_version` (`1.0.0`), `expected_intents` (array with evidence), `expected_observations` (observation IDs, evidence objects, polarity where applicable, validity, relationships/references, nullable confidence), `expected_context_references`, `expected_abstention`, and `expected_lu_safety_flags`. Evidence requires the record/message ID and exact phrase; offsets are null unless a documented indexing convention is used. Observation references must resolve within the record or an explicitly represented permitted context.

| Field | Type | Required | Rule |
|---|---|---:|---|
| `id` | string | yes | Unique stable ID, `P1SEED-###`. |
| `category` | string | yes | One primary coverage category. |
| `original_sentence` | string | yes | Exact sentence; no normalization. |
| `language` | enum | yes | `kn-IN`, `en-IN`, `code-mixed`, `unknown`. |
| `input_characteristics` | array[string] | yes | E.g. `colloquial`, `negation`, `stt_like`, `context_dependent`. |
| `conversation_context` | object/null | yes | Only explicit synthetic prior facts/questions; null for independent input. |
| `expected_intent` | string | yes | Draft label from contract taxonomy. |
| `expected_crop` | object | yes | `{value, status}`; value may be null. |
| `expected_entities` | object | yes | Structured expected entities; absent values are empty arrays/null, never guessed. |
| `expected_symptoms` | array | yes | Each item has `meaning`, `polarity`, `plant_part`, `evidence_status`. |
| `expected_context` | object | yes | Soil/irrigation/growth/spread/duration/severity/location values or null. |
| `expected_ambiguity` | object | yes | `{is_ambiguous, reasons}`. |
| `expected_missing_information` | array[string] | yes | Fields needed before targeted guidance. |
| `expected_follow_up` | object | yes | `{required, focus, answer_type}`. |
| `difficulty` | enum | yes | `low`, `medium`, `high`. |
| `review_status` | enum | yes | `draft`, `reviewed`, `approved`; this seed uses `draft`. |
| `notes` | string | yes | Annotation caveat; never agricultural advice. |

## Annotation rules

- Label observations, not diagnoses. `leaf_yellowing` is acceptable; “bacterial wilt” is not a gold label unless the speaker explicitly says it, and then it remains a disease *mention*.
- Preserve negation with `polarity: absent`; do not omit it.
- Use arrays for independently mentioned symptoms. Do not add plausible symptoms.
- Mark crop omitted/ambiguous rather than assuming tomato from a plant-only message.
- For a context-dependent record, expected entities may use `status: contextual`; the context object must specify why.
- Contradictions retain both claims with the newer claim identified in context; they are not silently overwritten.
- Draft expected meanings need Kannada-speaker review. Agricultural implications need agricultural-expert review.

## Versioning and review

The dataset file is append-only by ID. Changes to an existing record require an annotation note, reviewer identity/role recorded outside the public corpus if personal data is involved, and a version bump. A record may move `draft -> reviewed -> approved`; metrics for release gates must name the included review status.
