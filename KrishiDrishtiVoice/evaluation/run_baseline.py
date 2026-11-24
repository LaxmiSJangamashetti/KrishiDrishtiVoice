import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from agriculture_engine import build_guidance,identify_crop,parse_question,search
DATASET=ROOT/"evaluation/datasets/questions.jsonl"; OUTPUT=ROOT/"evaluation/results/deterministic_baseline.jsonl"
def main():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); out=[]
    for line in DATASET.open(encoding="utf-8"):
        x=json.loads(line); start=time.perf_counter()
        try:
            p=parse_question(x["original_question"]); ms=search(x["original_question"]); g=build_guidance(x["original_question"],"ಕನ್ನಡ (Kannada)" if x["language_script_category"]=="kannada_script" else "English")
            out.append({"question_id":x["question_id"],"language_script_category":x["language_script_category"],"expected":{"crop":x["expected_crop"],"topic":x["expected_observable_symptom_topic"],"retrieval_ids":x["acceptable_retrieval_record_ids"],"safety_category":x["safety_category"]},"observed":{"crop":identify_crop(x["original_question"]),"topic":p.get("symptom"),"retrieval_ids":[m.record["id"] for m in ms],"clarification_requested":bool(g.get("follow_up_questions")),"abstention_or_safety_rejection":bool(g.get("safety_category")) or g.get("crop") is None or not ms},"error":None,"processing_time_ms":round((time.perf_counter()-start)*1000,3)})
        except Exception as e: out.append({"question_id":x["question_id"],"language_script_category":x["language_script_category"],"expected":{},"observed":{},"error":f"{type(e).__name__}: {e}","processing_time_ms":None})
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        for row in out: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    print(f"Wrote {len(out)} baseline rows to {OUTPUT}")
if __name__=="__main__": main()
