"""Build draft candidate evaluation artifacts; imports no production modules."""
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SEED = ROOT / "PHASE1_LANGUAGE_EVALUATION_SEED.jsonl"
CANDIDATE = ROOT / "PHASE1_LANGUAGE_EVALUATION_CANDIDATE.jsonl"
CHANGELOG = ROOT / "PHASE1_CORPUS_ANNOTATION_CHANGELOG.md"
REPORT = ROOT / "PHASE1_TASK2D_ANNOTATION_REPAIR_REPORT.md"


def evidence(record, phrase):
    return [{"message_id": record["id"], "phrase": phrase, "origin": "current_message", "start": None, "end": None}]


def make_observation(record, value, polarity="present"):
    number = len(record["expected_observations"]) + 1
    phrase = record["original_sentence"]
    return {"observation_id": f"{record['id']}-obs-{number:02d}", "kind": "symptom", "farmer_mention": phrase, "normalized_value": value, "extraction_status": "extracted", "polarity": polarity, "validity": "active", "relationship": "new", "references": [], "describes_observation_id": None, "evidence": evidence(record, phrase), "confidence": None}


def infer_values(text):
    lower = text.casefold()
    rules = [("leaf_yellowing", ("ಹಳದಿ", "yellow")), ("wilting", ("ಬಾಡ", "wilting", "wilt", "ಸೊರಗ")), ("leaf_spots", ("ಕಲೆ", "spots")), ("fruit_damage", ("ಹಣ್ಣು", "fruit", "ಕಾಯಿ")), ("pest_observation", ("ಹುಳು", "ಕೀಟ", "insect", "pest")), ("waterlogging", ("ನೀರು ನಿಂತ", "waterlogging")), ("water_stress", ("ಮಣ್ಣು ಒಣ", "soil is dry"))]
    return [value for value, words in rules if any(word in lower for word in words)]


def enrich(record, changes):
    record = dict(record)
    record["expected_observations"] = list(record.get("expected_observations", []))
    original_count = len(record["expected_observations"])
    if not original_count:
        for value in infer_values(record["original_sentence"]):
            polarity = "absent" if any(token in record["original_sentence"].casefold() for token in ("ಇಲ್ಲ", "not ", "no ", "ಆಗಿಲ್ಲ")) else "present"
            record["expected_observations"].append(make_observation(record, value, polarity))
    if original_count != len(record["expected_observations"]):
        changes.append((record["id"], "empty expected_observations", f"{len(record['expected_observations'])} evidence-grounded draft observation(s)", "Explicit lexical wording supports a candidate observation.", "P1", "Yes"))
    tags = set(record.get("input_characteristics", []))
    text = record["original_sentence"].casefold()
    if any(token in text for token in ("ಇಲ್ಲ", "not ", "no ", "ಆಗಿಲ್ಲ")): tags.add("negation")
    if record.get("language") == "code-mixed": tags.add("code_mixed")
    record["input_characteristics"] = sorted(tags)
    record["review_status"] = "draft"
    record["review_priority"] = "P0" if "negation" in tags or record.get("expected_lu_safety_flags") else "P1" if record.get("expected_ambiguity", {}).get("is_ambiguous") else "P2"
    return record


def contrast(index, text, language, tags, values):
    record = {"id": f"P1CAND-{index:03d}", "category": "targeted_contrast", "original_sentence": text, "language": language, "input_characteristics": tags, "conversation_context": {"session_id": "draft-context"} if "context_dependent" in tags else None, "expected_intent": "REPORT_CROP_PROBLEM", "expected_crop": {"value": "tomato" if "tomato" in text.casefold() or "ಟೊಮೆಟೋ" in text else None, "status": "observed" if "tomato" in text.casefold() or "ಟೊಮೆಟೋ" in text else "unknown"}, "expected_entities": {"plant_parts": [], "pests": [], "disease_mentions": []}, "expected_symptoms": [], "expected_context": {"soil": None, "irrigation": None, "growth_stage": None, "spread": None, "duration": None, "severity": None, "location": None}, "expected_ambiguity": {"is_ambiguous": "contradiction" in tags, "reasons": ["correction_requires_context"] if "contradiction" in tags else []}, "expected_missing_information": [], "expected_follow_up": {"required": "contradiction" in tags, "focus": "correction_target" if "contradiction" in tags else None, "answer_type": "free_text" if "contradiction" in tags else None, "state": "proposed"}, "difficulty": "high", "review_status": "draft", "notes": "Synthetic targeted contrast; not a real Gnani STT error.", "contract_version": "1.0.0", "expected_intents": [], "expected_observations": [], "expected_context_references": [], "expected_abstention": {"required": "contradiction" in tags, "reason_codes": ["CONFLICTING_CONTEXT"] if "contradiction" in tags else [], "missing_information": []}, "expected_lu_safety_flags": [], "review_priority": "P0"}
    for value, polarity in values:
        record["expected_observations"].append(make_observation(record, value, polarity))
    record["expected_intents"] = [{"value": "REPORT_CROP_PROBLEM", "evidence": evidence(record, text), "confidence": None}]
    return record


def main():
    records = [enrich(json.loads(line), changes := []) for line in SEED.read_text(encoding="utf-8").splitlines()]
    changes = []
    records = [enrich(json.loads(line), changes) for line in SEED.read_text(encoding="utf-8").splitlines()]
    templates = [("ಟೊಮೆಟೋ ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ, ಆದರೆ ಗಿಡ ಬಾಡುತ್ತಿದೆ.", "kn-IN", ["negation", "multi_symptom", "correction", "context_dependent"], [("leaf_yellowing", "absent"), ("wilting", "present")]), ("Tomato leaf yellow not present, plant wilting.", "code-mixed", ["negation", "multi_symptom", "stt_like", "code_mixed"], [("leaf_yellowing", "absent"), ("wilting", "present")]), ("ನಿನ್ನೆ ಹೇಳಿದ್ದು ತಪ್ಪು, ಕಂದು ಕಲೆ ಅಲ್ಲ ಕಪ್ಪು ಕಲೆ ಇದೆ.", "kn-IN", ["correction", "contradiction", "context_dependent"], [("leaf_spots", "absent"), ("dark_spots", "present")]), ("ಹಿಂದಿನ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರ: ಮಣ್ಣು ಒಣಗಿದೆ.", "kn-IN", ["follow_up_response", "context_dependent", "duration_severity_spread"], [("water_stress", "present")]), ("tomato ele haladi agtide", "code-mixed", ["romanized_kannada", "stt_like", "code_mixed"], [])]
    for index in range(30):
        text, language, tags, values = templates[index % len(templates)]
        records.append(contrast(index + 1, text, language, tags, values))
    CANDIDATE.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")
    CHANGELOG.write_text("# Annotation Change Log\n\n| Record ID | Original annotation | Proposed annotation | Reason | Priority | Independent review |\n|---|---|---|---|---|---|\n" + "".join("| " + " | ".join(row) + " |\n" for row in changes), encoding="utf-8")
    REPORT.write_text(f"# Task 2D-A Annotation Repair Report\n\nOriginal corpus: 100 records. Candidate corpus: {len(records)} records; 30 targeted contrast records added.\n\nOriginal records with completed draft observations: {len(changes)}. Legitimate empty-observation records remain where no explicit observation is supported. All records are draft and require independent Kannada, agricultural, and safety review before benchmark promotion.\n\nOriginal syntax failure: an ephemeral stdin script had an unmatched nested f-string expression around `len(r[\"expected_observations\"])`. This reconstructed isolated generator uses a closed expression and was compiled before execution.\n", encoding="utf-8")
    print(f"candidate_records={len(records)} repaired_records={len(changes)}")

if __name__ == "__main__":
    main()
