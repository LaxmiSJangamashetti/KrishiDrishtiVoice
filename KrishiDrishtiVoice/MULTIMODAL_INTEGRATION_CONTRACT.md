# Multimodal Integration Contract

The future vision adapter must return the schema implemented by `ImageResult` in `image_processing_contract.py`.

## Safety rules

- An image candidate is an observation or hypothesis, never a confirmed diagnosis.
- The adapter must abstain on unsupported crops, poor quality, unknown classes, or uncalibrated confidence.
- The existing Language Understanding, Conversation Manager, safety validator, knowledge retrieval, and evidence-backed guidance remain authoritative.
- Chemical dose and mixing requests follow the existing safety refusal path.
- Image output must not bypass clarification or retrieval.

## Integration sequence

1. Validate image quality and supported format.
2. Run a versioned inference adapter when one is actually available.
3. Convert output to `ImageResult`.
4. Add visible observations to conversation context with image provenance.

## Task 12.5 reliability boundary

Tomato, potato and maize image outputs remain experimental visual hypotheses. Rice and chilli image analysis is unavailable and must remain text-only. Image outputs may trigger clarification and source-backed investigation, but never a confirmed disease, pesticide, fertilizer, mixing, or spray recommendation.
5. Ask clarification questions when evidence is insufficient.
6. Retrieve only source-backed agricultural guidance.
7. Preserve uncertainty and referral warnings in text and optional voice output.
