# KrishiDrishti AI — SLM Feasibility Study

**Status:** Research only. No model downloaded, installed, fine-tuned, or connected to the application.

**Scope:** Kannada, English, Kannada-English code-mixed agricultural question understanding for the existing tomato prototype, with future extension to rice and chilli. The SLM must extract and clarify observations; it must not become the source of agricultural recommendations.

## Executive recommendation

Use a two-track evaluation:

1. **Desktop evaluation:** start with `Qwen/Qwen2.5-3B-Instruct` as the structured-extraction baseline and compare it with `google/gemma-3-1b-it` and `microsoft/Phi-3.5-mini-instruct`. Qwen is attractive for JSON-oriented extraction and multilingual instruction following, but its `qwen-research` license requires legal review before commercial deployment. Phi has an MIT license and is a strong English/structured-output baseline, but its Kannada suitability must be measured rather than assumed. Gemma is a credible mobile-oriented candidate, but it has Google-specific terms and distribution notices.
2. **Future budget Android:** prioritize a small Gemma family model supported by Google AI Edge/LiteRT after device testing; keep a GGUF `Qwen2.5-1.5B/3B` or similar fallback only if its license is approved. For the lowest RAM tier, use an encoder model such as IndicBERTv2 or MuRIL for classification/slot extraction instead of a generative SLM.

No candidate is approved for production from model-card claims alone. Kannada, code-mixing, JSON validity, latency, RAM, and agricultural abstention must be tested on unseen data.

## 1. Existing architecture and insertion point

### Current pipeline

```text
Audio capture/upload
    -> gnani_service.transcribe_audio()
    -> original Unicode transcript
    -> agriculture_engine.normalize_text()
    -> parse_question()
    -> identify_crop() / search()
    -> build_guidance()
    -> safety validation + source-backed knowledge.json guidance
    -> Streamlit display
```

The current application already has a safe authority boundary:

- `gnani_service.py` owns Prisma STT, credentials, supported audio formats, and error handling.
- `agriculture_engine.py` owns normalization, conservative crop/symptom parsing, retrieval, follow-up questions, safety blocks, and guidance assembly.
- `knowledge.json` owns curated records, source references, uncertainty, and safe actions.
- `app.py` owns the dashboard and currently labels translation, SLM, conversation orchestration, and TTS as planned.

### Recommended SLM location

Add a future `slm_interpreter.py` or equivalent service between transcript preservation and retrieval:

```text
Prisma transcript
    -> deterministic normalization and safety pre-check
    -> SLM interpreter (optional, local/offline)
    -> schema validation + confidence/abstention gate
    -> deterministic reconciliation with parse_question()
    -> search() using only approved crop/topic fields
    -> knowledge.json / RAG
    -> safety validator
    -> guidance
```

The SLM should produce structured observations, aliases, missing fields, and follow-up questions. It should not produce pesticide doses, disease confirmations, treatment schedules, or source claims. A failed, low-confidence, malformed, or conflicting SLM result must fall back to the deterministic engine.

### Required authority rules

1. Preserve the exact original transcript.
2. Run existing safety validation before accepting SLM output.
3. Treat SLM fields as hypotheses/observations, never diagnoses.
4. Permit retrieval only against records already present in the curated knowledge base.
5. Keep existing source references and safety wording authoritative.
6. Log evaluation metadata without logging credentials or unnecessary farmer audio/text.

## 2. Candidate comparison

Sizes below are planning estimates, not measured results on this project machine. Quantized sizes depend on tokenizer, runtime, quantization scheme, and packaging overhead. A 4-bit estimate is approximately `parameter_count × 0.5 bytes` plus scales/metadata; actual files can be larger.

| Candidate | Best role | Kannada / code-mix evidence | Approx. weight size | 4-bit planning size | License / commercial risk | Android/runtime fit |
|---|---|---|---:|---:|---|---|
| `ai4bharat/IndicBERTv2-MLM-only` | Kannada-aware classifier, reranker, slot extractor after fine-tuning | IndicBERTv2 is an Indic encoder covering 26 languages; it is not a chat/instruction model and cannot reliably emit the full JSON schema without a task head or fine-tuning. | HF repository shows about 1.12 GB PyTorch; BERT-base-class architecture | roughly 0.2–0.3 GB with suitable integer quantization, plus runtime | MIT shown on model card; verify model and data terms before redistribution | Good candidate for ONNX/TFLite-style encoder deployment; not a generative conversational engine. Fine-tune for intent/slots/NER. |
| `google/muril-base-cased` | Kannada and transliterated/code-mixed encoder baseline | Model card states 17 Indian languages plus transliterated counterparts; useful for Kannada and Romanized/code-mixed input, but it is masked-LM/encoder, not instruction tuned. | HF repository about 3.47 GB across framework files; PyTorch file about 953 MB | roughly 0.2–0.3 GB for an 0.3B-class encoder, runtime-dependent | Apache-2.0 shown on model card; check Google model/data notices | Strong conceptual fit for Android classification/slot extraction; requires a task head and export/benchmark work. |
| `ai4bharat/IndicBART` | Indic text generation, normalization, paraphrase or question generation | Model card explicitly includes Kannada and English among 11 Indic languages; representations and generation behavior need task-specific testing. | Size not stated in the inspected model card; larger seq2seq model than an encoder | Must measure; do not infer from “smaller than mBART” | Model page should be checked before commercial use; do not assume a permissive license from the model name alone | Less attractive for budget phones than a small decoder or encoder; Transformers/ONNX route possible after validation. |
| `Qwen/Qwen2.5-3B-Instruct` | Desktop structured extraction and code-mixed prompt baseline | Model card advertises 29+ languages and JSON/structured-output improvements, but does not establish Kannada agricultural accuracy; benchmark required. | HF repository about 6.18 GB safetensors | about 1.8–2.2 GB for common 4-bit GGUF-style packaging | `qwen-research` license shown on model card; commercial distribution requires legal review | Excellent llama.cpp/GGUF evaluation path; 3B Q4 likely too heavy for the lowest budget tier, potentially usable on higher-RAM Android. |
| `microsoft/Phi-3.5-mini-instruct` | Desktop English and structured extraction comparison | Microsoft describes multilingual and multi-turn improvements, but the published benchmark excerpt does not include Kannada; Kannada must be treated as unverified. | HF repository about 7.64 GB; 4B parameters listed | about 2.0–2.5 GB at 4-bit | MIT shown on model card; still review notices, acceptable-use and downstream obligations | ONNX/mobile variants and general inference ecosystem are useful; 4B Q4 is not the first budget-phone choice. |
| `google/gemma-3-1b-it` | Mobile-oriented generative extraction candidate | Model card positions it as a lightweight model; Kannada quality and code-mix behavior are not established by the inspected sources. | Exact current file size must be measured from the selected runtime artifact; 1B FP16 is roughly 2 GB before packaging | roughly 0.6–0.9 GB planning range depending on format | Gemma Terms of Use permit responsible commercial use but impose use restrictions, notices, and distribution conditions; not an OSI-style MIT/Apache grant | Strongest documented Google AI Edge path: Gemma 3 1B artifacts are documented for MediaPipe/LiteRT-style Android use. Device-specific RAM and speed still require measurement. |

### Interpretation of the comparison

- **Best Kannada signal:** MuRIL and IndicBERTv2 are the most defensible language-specific baselines because their model cards explicitly cover Indian languages; MuRIL also explicitly includes transliterated counterparts.
- **Best first generative extractor:** Qwen2.5-3B-Instruct is technically attractive for JSON extraction, but the `qwen-research` license is a deployment blocker until reviewed.
- **Best permissive desktop comparator:** Phi-3.5-mini-instruct has MIT licensing and documented structured/instruction use, but Kannada is an empirical question.
- **Best mobile path:** Gemma 3 1B is the most directly aligned with documented Google mobile tooling, subject to Gemma terms and actual budget-phone tests.
- **Best low-RAM architecture:** a fine-tuned IndicBERTv2/MuRIL classifier or token/slot extractor, not a chat model. This may deliver more reliable extraction with less memory, but it requires labeled training data and cannot itself conduct a rich conversation.

## 3. Structured output contract

The future interpreter should return JSON only, validated against a strict schema. Every field needs a value, `null`, or an explicit `unknown`; never silently guess.

```json
{
  "schema_version": "1.0",
  "language": "kn-IN",
  "original_text": "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ",
  "crop": {"value": "tomato", "confidence": 0.98, "evidence": "ಟೊಮೆಟೋ"},
  "crop_variety": {"value": null, "confidence": 0.0, "evidence": null},
  "plant_part": [{"value": "leaf", "confidence": 0.96, "evidence": "ಎಲೆಗಳು"}],
  "observed_symptoms": [
    {"value": "yellowing", "confidence": 0.93, "evidence": "ಹಳದಿಯಾಗುತ್ತಿವೆ", "is_diagnosis": false}
  ],
  "duration": {"value": null, "unit": null, "confidence": 0.0, "evidence": null},
  "severity": {"value": "unknown", "confidence": 0.0, "evidence": null},
  "environmental_conditions": [],
  "farmer_intent": {"value": "understand_symptom", "confidence": 0.86},
  "missing_information": ["crop_age", "distribution", "soil_moisture"],
  "follow_up_questions": [
    "Are lower or upper leaves affected?",
    "Is the soil continuously wet or dry?"
  ],
  "abstain": false,
  "model_confidence": 0.89,
  "warnings": ["Observation only; not a confirmed diagnosis."]
}
```

Allowed values should be controlled vocabularies backed by the deterministic engine: `tomato`, `rice`, `chilli`; `leaf`, `stem`, `root`, `flower`, `fruit`, `whole_plant`; current symptom/topic IDs; `unknown`; and a small set of farmer intents such as `understand_symptom`, `irrigation_question`, `pest_observation`, `disease_concern`, `fertilizer_question`, `chemical_request`, and `expert_referral`.

The schema should reject:

- disease names presented as confirmed facts;
- pesticide or fertilizer dose fields;
- unsupported crops or treatments;
- missing evidence for a non-null field;
- invalid JSON, duplicate contradictory values, or confidence without evidence.

## 4. Evaluation benchmark

### Dataset design

Create a versioned, private evaluation set outside the application code first. Do not reuse the current 29 regression tests as the only benchmark.

Target an initial **300 unseen questions**:

- 120 Kannada-script questions;
- 80 English questions;
- 80 Kannada-English code-mixed questions, including Romanized Kannada;
- 20 adversarial/safety questions.

Balance the set across the current tomato topics: yellowing, wilting/water stress, waterlogging, brown spots, leaf curling, whitefly observations, fruit-borer observations, leaf-miner observations, fruit damage, unknown/ambiguous symptoms, and crop-missing questions. Include natural inflections, spelling variation, indirect descriptions, short voice-transcript fragments, and irrelevant questions.

Keep the test set unseen by prompt authors and model developers. Split by farmer wording/template, not randomly by near-duplicate sentence. Have two independent agricultural/NLP reviewers annotate disagreements and preserve an adjudication record.

### Gold labels

For every question, annotate:

- language/script and code-mixing level;
- crop and variety, if explicitly stated;
- plant part;
- observable symptoms/topics;
- duration, severity, environment;
- farmer intent;
- required missing information;
- acceptable follow-up questions;
- whether the question is unsafe, unsupported, ambiguous, or irrelevant;
- acceptable retrieval record IDs;
- whether abstention is required.

### Metrics

Compare deterministic engine, each SLM, and a hybrid system.

- Exact and macro-F1 for crop/topic/plant-part slots.
- Span or evidence accuracy for symptom extraction.
- Duration/severity/environment exact match, with `unknown` handled explicitly.
- Intent macro-F1.
- Missing-information precision/recall.
- Follow-up question recall and duplicate-question rate.
- JSON validity rate and schema-validation pass rate.
- Abstention precision: unsupported/ambiguous questions must not receive a confident topic.
- Retrieval hit@1 and hit@3 against approved `knowledge.json` record IDs.
- Safety-block recall for dose, chemical-mixing, guaranteed-diagnosis, and unsupported-treatment requests.
- Unsupported-claim rate: any diagnosis, dose, treatment, or source not present in the curated records is a critical failure.
- Desktop latency, peak RSS, model load time, tokens/second, and Android cold/warm latency.

### Acceptance gates

The SLM cannot replace the deterministic engine unless, on the held-out set:

1. safety-block recall is 100% for the adversarial set;
2. unsupported-claim rate is zero in structured output and rendered guidance;
3. crop/topic macro-F1 beats the deterministic baseline by a meaningful pre-registered margin;
4. JSON/schema validity is at least 99% without repair prompting;
5. ambiguous-question abstention precision is at least 95%;
6. the hybrid system never performs worse than the current engine on existing regression tests;
7. budget-phone memory, latency, battery, and thermal measurements meet a written product threshold.

## 5. SLM versus current deterministic engine

| Capability | Deterministic engine today | SLM opportunity | Required guardrail |
|---|---|---|---|
| Exact known phrases | Strong, transparent | May generalize paraphrases | Keep deterministic result when confidence is higher |
| Kannada inflections/code-mix | Improving through reviewed patterns | Better contextual interpretation is plausible | Test unseen forms; no silent translation assumptions |
| Crop/symptom slots | Small controlled vocabulary | More flexible extraction | Map only to controlled vocabulary |
| Ambiguity | Explicit fallback/follow-up logic | May overcommit | Require abstention and evidence fields |
| Retrieval | Source-backed local records | Can select/query better | SLM may not create records or sources |
| Safety | Explicit hard-coded rejection patterns | May miss or imitate unsafe advice | Existing safety validator remains authoritative |
| Explainability | Keywords, score, record IDs | Model rationale is not evidence | Display deterministic evidence and record source |
| Offline operation | Already works for text | Possible after model deployment | No claim until full device test |

The correct near-term design is hybrid: use the SLM to propose normalized slots and follow-up candidates, then reconcile them with deterministic parsing and retrieve only from the local curated base. A disagreement should be shown as uncertainty or sent to follow-up, not resolved by model confidence alone.

## 6. Runtime and device plan

### Desktop

- Use a reproducible Transformers or llama.cpp evaluation harness.
- Keep model artifacts outside the project until a candidate is approved; if later downloaded, put them on D: under a dedicated cache.
- Measure cold start, warm latency, peak process RSS, JSON validity, and CPU-only speed.
- Prefer Q4/Q5 quantization for generative candidates, but compare extraction accuracy against FP16 on a small sample.

### Android

Two paths should be evaluated:

1. **Google AI Edge/LiteRT path:** appropriate for Gemma-family artifacts with documented Android support. Google documents mobile deployment and the current AI Edge documentation identifies Gemma 3 1B artifacts for LLM inference. Confirm current API status and artifact format at implementation time.
2. **llama.cpp/GGUF path:** more model-flexible and usable with Android bindings. The official llama.cpp Android documentation covers Android Studio bindings, GGUF loading, hardware acceleration, and warns that context size affects memory. This path is attractive for Qwen-family models, subject to license approval and packaging work.

Budget-phone tiers should be defined before selection:

- **Low tier:** 3–4 GB RAM, CPU-first, target encoder or approximately 0.5–1B quantized generative model.
- **Middle tier:** 4–6 GB RAM, approximately 1B quantized model, short context, one request at a time.
- **High tier:** 6–8+ GB RAM, possibly 3B Q4, but still measure thermal throttling and app memory pressure.

These are engineering planning bands, not guarantees. Android process memory, tokenizer/runtime overhead, concurrent audio/STT, and other apps reduce usable RAM.

## 7. Fine-tuning decision

Do not fine-tune in the next milestone. First collect the benchmark and run zero-shot/few-shot extraction. Fine-tuning becomes justified only if:

- the chosen base model is license-compatible;
- at least several thousand reviewed Kannada/code-mixed examples can be created or licensed;
- the model consistently misses inflections or slot boundaries after prompt/schema controls;
- the hybrid baseline and safety gates are already stable.

For a low-RAM deployment, fine-tuning an IndicBERTv2 or MuRIL task head for intent/slot classification may be more efficient and safer than fine-tuning a generative chat model. A generative model should not be fine-tuned on unverified agricultural advice.

## 8. Phased implementation roadmap

### Phase 0 — benchmark and contract

Freeze the JSON schema, annotation guide, safety adversarial set, and deterministic baseline. No model download is necessary.

### Phase 1 — desktop offline comparison

Evaluate Qwen2.5-3B-Instruct, Phi-3.5-mini-instruct, Gemma 3 1B, IndicBERTv2, and MuRIL only if licenses and hardware permit. Produce per-language and per-topic metrics, not a single aggregate score.

### Phase 2 — hybrid adapter

Add an optional interpreter interface with timeouts, schema validation, confidence thresholds, deterministic fallback, and no changes to `gnani_service.py`. Keep the UI label explicit: “SLM interpretation — experimental.”

### Phase 3 — mobile proof of concept

Test the leading generative candidate and the leading encoder candidate on representative budget Android devices using airplane mode. Measure cold/warm latency, peak RSS, battery/thermal behavior, crash rate, and accuracy on the held-out Kannada/code-mix set.

### Phase 4 — limited pilot

Only after acceptance gates pass, enable SLM-assisted interpretation for a small cohort. Continue to make the knowledge base, safety validator, and agricultural expert referral authoritative.

## 9. Risks and unresolved questions

- Model cards do not prove Kannada agricultural understanding; Kannada and code-mixing need direct evaluation.
- Quantized file size is not the same as peak RAM.
- Gemma commercial use is conditional on Google Terms of Use and notices; Qwen’s `qwen-research` license needs legal review.
- IndicBERTv2 and MuRIL are encoders, not drop-in conversational SLMs; task heads and labeled data are required.
- Structured JSON can still contain confident false interpretations; schema validity is not semantic correctness.
- Voice transcription errors can propagate into SLM extraction; benchmark both clean typed text and real Prisma transcripts.
- Agricultural recommendations must remain outside the SLM. The model may identify observations and missing information only.

## Sources inspected

- [Existing project README](README.md), [agriculture_engine.py](agriculture_engine.py), [gnani_service.py](gnani_service.py), [knowledge.json](knowledge.json), and existing tests — inspected locally.
- [AI4Bharat IndicBERTv2 model card](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only) — languages, MIT label, model artifact size, encoder usage.
- [Google MuRIL model card](https://huggingface.co/google/muril-base-cased) — 17 Indian languages, transliteration training, Apache-2.0 label, downstream-task limitations.
- [AI4Bharat IndicBART model card](https://huggingface.co/ai4bharat/IndicBART) — Kannada/English support and intended fine-tuning use.
- [Qwen2.5-3B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) — parameter family, multilingual/structured-output claims, artifact size, license label.
- [Microsoft Phi-3.5-mini model card](https://huggingface.co/microsoft/Phi-3.5-mini-instruct) — multilingual positioning, 4B size, MIT license, limitations.
- [Google Gemma 3 1B model card](https://huggingface.co/google/gemma-3-1b-it) — lightweight model and access terms.
- [Gemma Terms of Use](https://ai.google.dev/gemma/terms) — commercial-use conditions, restrictions, notices, distribution requirements.
- [Google mobile deployment guidance](https://ai.google.dev/gemma/docs/integrations/mobile) and [AI Edge LLM inference documentation](https://developers.google.com/edge/mediapipe/solutions/genai/llm_inference/index) — Android/mobile runtime direction and Gemma 3 1B artifact support.
- [llama.cpp Android documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md) — Android bindings, GGUF loading, hardware acceleration, and memory/context cautions.

## Final decision

Proceed with a **benchmark-first hybrid design**. For desktop research, evaluate Qwen2.5-3B-Instruct, Phi-3.5-mini-instruct, and Gemma 3 1B against IndicBERTv2/MuRIL encoder baselines. Do not select Qwen for a shipped commercial product until its license is cleared. For future budget Android, make Gemma 3 1B the first generative mobile candidate because Google documents an AI Edge path, while keeping a fine-tuned IndicBERTv2/MuRIL extractor as the likely low-RAM safety-oriented option. In every case, the deterministic parser, curated source-backed knowledge base, and safety validator remain authoritative.
