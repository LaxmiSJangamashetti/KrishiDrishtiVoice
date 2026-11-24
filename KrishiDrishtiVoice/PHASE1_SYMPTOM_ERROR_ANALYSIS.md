# Phase 1 Symptom Error Analysis

Status: `IMPLEMENTED_AND_TESTED`

The 130-record draft V2 corpus was evaluated with structured LU. The focused comparison included 30 records with exactly one present expected symptom and no expected ambiguity. This is not a human-reviewed or real-farmer benchmark.

Before the fixes: 10 misses and 7 false activations. Observed root causes were missing leaf-trail/leaf-spot and fruit-hole vocabulary, broad insect and fruit-damage overlap, missing code-mixed terminology, and negation scope crossing contrast clauses.

Implemented fixes:

- Added reusable leaf-spot, serpentine leaf-trail, and fruit-entry-hole aliases.
- Suppressed broad insect observations when a specific whitefly observation exists.
- Suppressed broad fruit damage when entry holes are specifically observed.
- Reset negation scope at punctuation and Kannada/English contrast conjunctions.
- Preserved abstention for unsupported Romanized Kannada instead of guessing.

After the fixes on the same subset: 5 misses and 4 false activations. The legacy adapter remains separately measured at 45/45 crop, 32/61 symptom, 12 incorrect activations, and 0 exceptions.

Draft labels such as `white_insect_observation` versus `whitefly_observation` require human contract/data reconciliation.
