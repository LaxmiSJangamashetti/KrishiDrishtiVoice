import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATASET=ROOT/"evaluation/datasets/questions.jsonl"
EXPECTED={"kannada_script":120,"english":90,"code_mixed":90}
REQUIRED={"question_id","original_question","language_script_category","expected_crop","expected_plant_part","expected_observable_symptom_topic","expected_farmer_intent","missing_information","acceptable_retrieval_record_ids","expected_clarification_abstention_behaviour","safety_category"}
SAFETY={"pesticide_dose","chemical_mixing","guaranteed_diagnosis","unsupported_treatment"}
def validate():
    errors=[]; rows=[]
    with DATASET.open(encoding="utf-8") as f:
        for n,line in enumerate(f,1):
            if not line.strip(): errors.append(f"blank line {n}"); continue
            try: rows.append(json.loads(line))
            except json.JSONDecodeError as e: errors.append(f"invalid JSONL line {n}: {e}")
    ids=[x.get("question_id") for x in rows]
    if len(rows)!=300: errors.append(f"expected 300 rows, found {len(rows)}")
    if len(set(ids))!=len(ids): errors.append("duplicate IDs")
    for cat,count in EXPECTED.items():
        if sum(x.get("language_script_category")==cat for x in rows)!=count: errors.append(f"wrong count for {cat}")
    if sum(x.get("safety_category") in SAFETY for x in rows)!=20: errors.append("expected exactly 20 safety rows")
    valid={x["id"] for x in json.loads((ROOT/"knowledge.json").read_text(encoding="utf-8"))["entries"]}
    for i,x in enumerate(rows,1):
        if REQUIRED-set(x): errors.append(f"row {i} missing fields")
        if x.get("safety_category") not in {"none",*SAFETY}: errors.append(f"row {i} invalid safety category")
        if any(r not in valid for r in x.get("acceptable_retrieval_record_ids",[])): errors.append(f"row {i} invalid retrieval ID")
    return errors
if __name__=="__main__":
    failures=validate()
    if failures: print("\n".join(failures)); raise SystemExit(1)
    print("VALID: 300 questions; 120 Kannada-script, 90 English, 90 code-mixed; 20 safety")
