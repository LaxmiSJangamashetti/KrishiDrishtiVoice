# Phase 1 Evaluation Report

Status: `IMPLEMENTED_BUT_NOT_FULLY_TESTED`

The new deterministic LU module has offline unit coverage for Kannada, English, code-mixed input, multiple observations, negation, missing crop information, unknown input, context retention, and multiple safety flags.

Measured result: 8 new LU tests passed, and the pre-existing 41 tests also passed, for 49/49 total.

These are structural and targeted behavior tests, not a human-reviewed benchmark score. The existing evaluation corpora remain draft and require independent Kannada-speaker and agricultural-expert review.

The existing 130-record offline baseline runner measured crop exact match 45/45 (100.0%), supported single-symptom match 32/61 (52.5%), incorrect activations 12, and parser exceptions 0. The runner excludes records according to its documented draft-corpus rules; these are not real-farmer accuracy results.
