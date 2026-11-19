# Task 2D-C Correction Report

V1 candidate: 130 records. V2 candidate: 130 records. Corrected named seed records: 10. Replaced contrastive records: 30 (`P1CAND-*` replaced by `P1V2C-*`; old IDs retained only in V1).

## Record-level changes
- P1SEED-027: `['fruit_damage:present']` -> draft correction. Reason: poor fruit set is taxonomy gap, not fruit damage. Independent review required.
- P1SEED-052: `['pest_observation:present']` -> draft correction. Reason: dosage request is intent/safety only, not pest presence. Independent review required.
- P1SEED-084: `['fruit_damage:present']` -> draft correction. Reason: small fruit is not physical fruit damage. Independent review required.
- P1SEED-090: `['wilting:present', 'water_stress:present']` -> draft correction. Reason: not dry soil is not positive water stress. Independent review required.
- P1SEED-048: `['fruit_damage:present', 'pest_observation:present']` -> draft correction. Reason: insects on fruit are not physical fruit damage. Independent review required.
- P1SEED-043: `['pest_observation:absent']` -> draft correction. Reason: preserve insect absence. Independent review required.
- P1SEED-049: `['leaf_yellowing:absent']` -> draft correction. Reason: preserve negated yellowing. Independent review required.
- P1SEED-053: `['leaf_yellowing:present']` -> draft correction. Reason: preserve correction scope. Independent review required.
- P1SEED-054: `['leaf_yellowing:absent', 'leaf_spots:absent']` -> draft correction. Reason: preserve negation scope. Independent review required.
- P1SEED-089: `['leaf_yellowing:present', 'wilting:present']` -> draft correction. Reason: yellowing present, wilting absent. Independent review required.

## Empty-observation classification
{'unclassified': 52, 'unsupported_vocabulary': 2, 'insufficient_evidence': 3, 'legitimate_intent_only': 1}

No exact duplicate normalized contrast sentence was intentionally retained; contrastive semantic diversity still requires human review. Taxonomy gaps include poor fruit set and small fruit observations where no safe controlled label exists. V2 is usable only for a provisional, explicitly unapproved baseline after reviewer exclusion of unresolved empty records.
