# Phase 1 Task 3A.2 Regression Investigation

## Root cause and affected cases

Case comparison found changes in: `P1SEED-002`, `P1SEED-004`, `P1SEED-006`, `P1SEED-007`, `P1SEED-023`, `P1SEED-026`, `P1SEED-049`, `P1SEED-051`, `P1SEED-052`, `P1SEED-054`, `P1SEED-076`, `P1SEED-083`, `P1SEED-090`, `P1SEED-094`, `P1V2C-006`, `P1V2C-014`, `P1V2C-021`, and `P1V2C-029`.

The changes fall into three groups:

1. **Expected normalization:** `ಟೊಮೇಟೊ` crop spelling and colloquial `ಬಾಡ್ತಾ`/`ಒಣಗ್ತಾ` forms normalize to reviewed equivalents. These are explicit lexical variants, not disease inference.
2. **Safety guard:** `P1SEED-049`, `P1SEED-054`, `P1SEED-083`, and `P1SEED-090` no longer activate positive symptoms from explicit negative phrases. This is a safety improvement, although the legacy parser cannot expose a negative polarity field.
3. **Punctuation/normalization-only changes:** several records changed only normalized text or crop alias output.

The aggregate incorrect-activation increase from 11 to 12 is not sufficient evidence for rolling back the colloquial aliases: the draft adapter compares a one-symptom parser with incomplete, unapproved annotations and cannot represent polarity or multiple observations. The changed cases must remain in human review. No broad workaround was added.

## Metrics

| Metric | Original | Task 3A | Task 3A.2 status |
|---|---:|---:|---|
| Crop exact match | 44/45 | 45/45 | unchanged pending case review |
| Supported symptom hit | 31/61 | 32/61 | unchanged pending case review |
| Incorrect activations | 11 | 12 | draft-adapter regression flag remains |
| Parser exceptions | 0 | 0 | no regression |

## Safety audit

Negated yellowing, wilting, insects, and dry soil are now conservatively suppressed by explicit guards. Black and brown spot distinctions remain unresolved when only generic spot wording is present. Mixed affirmative/negative sentences remain outside the current parser's structured capability.

## Tests and files

The existing Task 3A tests remain passing (`41/41` in the previous run). No production code was changed in this investigation, because the changed cases did not demonstrate a clear unsafe alias regression distinct from draft annotation/scoring limitations. This report is the only file created by Task 3A.2.

## Verdict

Task 3A should remain provisional. The crop and colloquial normalization behavior is acceptable for further review, but the increased incorrect-activation metric and lack of structured polarity/multi-symptom output block unconditional acceptance. Task 3B should begin only after the changed IDs receive Kannada-language and safety review and the evaluation adapter separates polarity/ambiguity limitations from concrete parser errors.
