"""Isolated structural validator for the local agricultural knowledge base."""
import json
import sys
from pathlib import Path


REQUIRED = ("id", "crop", "topic", "keywords", "description_en", "possible_causes", "follow_up_questions", "safe_initial_actions", "source", "limitations", "evidence_status")
VALID_STATUS = {"official_educational_information", "official_list_not_diagnostic", "official_referral_information", "partial_source_supported_observation", "partial_source_supported_triage", "cautious_triage_pending_field_confirmation"}


def validate(path: Path) -> list[str]:
    errors = []
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    ids = [entry.get("id") for entry in entries]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_ids")
    for index, entry in enumerate(entries, 1):
        for field in REQUIRED:
            if field not in entry:
                errors.append(f"record_{index}_missing_{field}")
        source = entry.get("source", {})
        if not isinstance(source, dict) or not str(source.get("url", "")).startswith("https://"):
            errors.append(f"record_{index}_invalid_source_url")
        if entry.get("evidence_status") not in VALID_STATUS:
            errors.append(f"record_{index}_invalid_evidence_status")
        if entry.get("crop") != data.get("scope", {}).get("crop"):
            errors.append(f"record_{index}_crop_scope_mismatch")
    return errors


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "knowledge.json"
    errors = validate(target)
    print({"path": str(target), "records": len(json.loads(target.read_text(encoding="utf-8")).get("entries", [])), "errors": errors, "valid": not errors})
    raise SystemExit(1 if errors else 0)
