# Phase 3 Farmer Simulation Evaluation

Status: `NEEDS_HUMAN_REVIEW`

The offline runner executed 50 synthetic scenarios across symptom reporting, multiple symptoms, negation, follow-ups, corrections, out-of-order input, ambiguity, retrieval, safety, and Kannada/code-mixed input.

Measured results:

- Total scenarios: 50
- Scenario execution passed: 50
- Scenario execution failures: 0
- Semantic correctness score: not claimed
- Farmer accuracy: not measured
- Kannada naturalness: not measured

Results are stored in `evaluation/phase3_simulation_results.jsonl`. Each record includes category, turns, active observations, pending question, safety flags, response, and execution error. Synthetic expected labels are not treated as validated agricultural truth.

Required next review: inspect scenario-level observation and follow-up correctness with a native Kannada reviewer and agricultural expert, then create development and holdout correctness labels.
