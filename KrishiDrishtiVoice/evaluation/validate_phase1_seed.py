"""Validate Phase 1's draft LU seed corpus without importing production modules."""
import json
import sys
from pathlib import Path

PATH = Path(__file__).parents[1] / "PHASE1_LANGUAGE_EVALUATION_SEED.jsonl"
REQUIRED = {"id", "category", "original_sentence", "language", "input_characteristics", "conversation_context", "expected_intent", "expected_crop", "expected_entities", "expected_symptoms", "expected_context", "expected_ambiguity", "expected_missing_information", "expected_follow_up", "difficulty", "review_status", "notes"}
POLARITY = {"present", "absent", "uncertain"}
CONTRACT_REQUIRED = {"contract_version", "expected_intents", "expected_observations", "expected_context_references", "expected_abstention", "expected_lu_safety_flags"}
VALID_STATES = {"proposed", "asked", "answered", "unresolved", "resolved", "irrelevant"}
VALID_VALIDITY = {"active", "superseded", "contradicted", "historical"}

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PATH
    errors, ids, records = [], set(), []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try: record = json.loads(line)
        except json.JSONDecodeError as error: errors.append(f"line {line_no}: {error}"); continue
        records.append(record); missing = REQUIRED - record.keys()
        missing |= CONTRACT_REQUIRED - record.keys()
        if missing: errors.append(f"line {line_no}: missing {sorted(missing)}")
        if record.get("id") in ids: errors.append(f"line {line_no}: duplicate id")
        ids.add(record.get("id"))
        for symptom in record.get("expected_symptoms", []):
            if symptom.get("polarity") not in POLARITY: errors.append(f"line {line_no}: invalid polarity")
        if record.get("contract_version") != "1.0.0": errors.append(f"line {line_no}: contract version")
        if record.get("expected_follow_up", {}).get("state", "proposed") not in VALID_STATES: errors.append(f"line {line_no}: invalid follow-up state")
        known = {item.get("observation_id") for item in record.get("expected_observations", [])}
        for item in record.get("expected_observations", []):
            if item.get("kind") == "symptom" and item.get("polarity") not in POLARITY: errors.append(f"line {line_no}: invalid observation polarity")
            if item.get("validity") not in VALID_VALIDITY: errors.append(f"line {line_no}: invalid validity")
            if item.get("extraction_status") == "extracted" and not item.get("evidence"): errors.append(f"line {line_no}: missing evidence")
            for evidence in item.get("evidence", []):
                if evidence.get("message_id") != record.get("id") or not evidence.get("phrase"): errors.append(f"line {line_no}: invalid evidence")
            for ref in item.get("references", []):
                if ref not in known: errors.append(f"line {line_no}: unresolved observation reference")
        if record.get("review_status") not in {"draft", "reviewed", "approved"}: errors.append(f"line {line_no}: invalid review status")
    categories = {record.get("category") for record in records}
    for category in {"colloquial_kannada", "waterlogging", "leaf_spots", "whitefly", "fruit_damage", "leaf_miner"}:
        if category not in categories: errors.append(f"missing required category: {category}")
    print(f"records={len(records)} unique_ids={len(ids)} categories={len(categories)}")
    if errors:
        print("FAILED"); print("\n".join(errors)); raise SystemExit(1)
    print("OK")

if __name__ == "__main__": main()
