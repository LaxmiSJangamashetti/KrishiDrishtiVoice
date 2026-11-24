# Remaining Work and Human Review

Status: `BLOCKED_ON_HUMAN_REVIEW`

The implemented LU layer is structurally tested, but benchmark readiness is not established by unit tests alone.

Human review remains required for:

- Kannada morphology, colloquial wording, STT variants, and code-mixed phrasing.
- Evidence phrase correctness and polarity for negated or uncertain statements.
- Multi-observation and multi-turn correction semantics.
- Agricultural safety review of any request involving diagnosis, pesticide dosage, chemical mixing, fertilizer quantities, or treatment.
- Evaluation against the approved Phase 1 corpus before accepting parser-quality claims.

Task 3 review items:

- Reconcile draft labels such as `white_insect_observation`, `pest_observation`, and `whitefly_observation`.
- Review Romanized Kannada examples such as `tomato ele haladi agtide` before adding aliases.
- Review whether generic `spots` should map to `leaf_spots` without an explicit plant-part phrase.

Task 4 remaining work:

- Add Kannada descriptions only after native-speaker review.
- Expand tomato coverage only from verified agricultural sources.
- Create independently reviewed development and holdout retrieval sets.
- Measure retrieval precision/recall once relevance labels exist.

Task 5 remaining work:

- Native Kannada review of follow-up questions and answer phrasing.
- Broader correction and out-of-order-answer handling.
- Explicit end-conversation and new-session controls in the UI.
- Human validation that selected follow-ups are useful for real farmer investigations.

Task 6 review requirements:

- Review all 50 simulation results for semantic correctness; execution success is not conversational correctness.
- Native Kannada review of prompts, corrections, negative statements, and code-mixed turns.
- Agricultural expert review of retrieval relevance and safe follow-up priorities.
- Add explicit UI support for retaining/exporting completed conversation history if required by product design.

Task 7 remaining work:

- Controlled real Kannada and English audio tests with user approval.
- Human verification of microphone permissions, recording quality, latency, transcript accuracy, and playback.
- Native Kannada review of voice prompts and transcript interpretation.
- Real-device verification of browser audio playback and repeated recording behavior.

Task 8 blockers:

- Live Gnani validation is explicitly unauthorized.
- Pytest is not installed; the existing unittest suite was used without installing packages.
- Physical microphone, browser permission, transcript accuracy, latency, and audible playback require human/device testing.

Frontend integration review:

- Review the imported profile UI visually in a browser.
- Review imported Kannada labels with a native speaker.
- Test persistent profile/farm/crop workflows on the target device.

Task 10 remaining work:

- Browser visual comparison of all imported profile pages against the ZIP source.
- Desktop and mobile viewport review.
- Authorized live Gnani STT/TTS validation.
- Physical microphone and audible playback validation.
- Human Kannada and agricultural expert review.

Not implemented in this increment: SLM inference, translation, semantic embeddings, a new retrieval service, persistent conversation storage, or autonomous conversational orchestration.
## Task 11.1 remaining blockers

- Human Kannada review is required before new crop aliases or translations are operational.
- Agricultural experts must review every new crop record and any disease/pest claim.
- Image datasets, licenses, field representativeness, annotations, and model evaluation are absent.
- Budget Android latency/RAM/quantization measurements are absent.
- Real Gnani voice and physical-device validation remain pending.

## Task 11.9 remaining blockers

- Unknown-image rejection is not reliable: the development non-tomato protocol produced 0.5361 false acceptance at the provisional threshold.
- Calibration used a validation split that was part of model development; independent calibration data are still required.
- No real field-image or representative device evaluation was performed.
- Browser-level Crop Image Analysis verification was not completed; manual verification remains required.

## Task 12.5 remaining work

- Obtain authorization and inspect candidate rice/chilli datasets before acquisition; no new datasets were downloaded.
- Build independent calibration and unknown/wrong-crop evaluation sets for tomato, potato and maize.
- Complete field-image and agricultural-expert review before expanding image guidance.
- Verify the corrected Crop Image Analysis route in a real browser at desktop and narrow widths.
