# Phase 1 Corpus Quality Audit

## Dataset summary

**Observed:** 100 JSONL records, 100 unique IDs, 22 primary categories, and existing structural validator result `OK`. All are `draft`. No semantic, farmer, Kannada-speaker, agricultural-expert, or safety approval is implied.

## Coverage matrix

| Characteristic | Count | Assessment | Gap |
|---|---:|---|---|
| standard | 10 | limited | Needs more independent standard forms |
| colloquial | 10 | limited | Dialect/regional review needed |
| code-mixed language | 11 | preliminary | Few deliberate annotations; no Romanized Kannada tag |
| English | 9 | limited | Not enough agricultural diversity |
| STT-like | 2 | insufficient | Needs realistic transcript error pairs |
| negation | 1 | insufficient | No broad negation-scope set |
| multi-symptom | 3 | insufficient | Needs linked attributes/corrections |
| ambiguity | 6 | insufficient | Need disambiguation alternatives |
| crop omitted | 7 | limited | Need context-carrying cases |
| duration/severity/spread | 1 each | insufficient | No meaningful variation |
| safety flags | 5 | limited | Needs indirect/colloquial unsafe requests |

The 70 `draft_seed` records are a material coverage-quality concern. More broadly, 75 records have no expected observations; they are structurally valid but not ready as detailed extraction gold labels.

## Duplicate and template analysis

**Observed:** no exact duplicate sentence. However, 75 records have an empty expected-observation list, and many use the same `diverse_farmer_input`/`draft_seed` template. This is a near-duplicate annotation pattern, even where wording differs. Six records share exactly `leaf_yellowing`; expected-observation equality is not itself an error but requires coverage justification.

## Annotation inconsistencies and review risks

- `P1SEED-021` onward require review for evidence/observation completeness because many were generated with empty expected observations.
- `P1SEED-023`, `024`, `047`, `048`, `071`, `079`–`081`, `091`–`093`: code-mixed/unsafe wording needs Kannada-English linguistic review.
- `P1SEED-026`, `035`, `036`, `067`, `068`, `073`, `074`: negation, correction, or contradiction scope needs explicit annotation review.
- `P1SEED-051`, `052`, `079`–`081`: safety flags need safety review.
- Pest/disease/fruit/leaf-miner mentions require agricultural review before a controlled normalized value is treated as appropriate.

## Readiness

The corpus is suitable only for **provisional structural and harness testing**. It is not ready for a trustworthy semantic baseline because broad tag coverage is shallow and 70 records lack rich expected observations. Before benchmark use: split generic records into meaningful characteristic tags, independently review Kannada wording, verify agricultural observation labels, and add reviewed negation, correction, multi-turn, and code-mixed examples.
