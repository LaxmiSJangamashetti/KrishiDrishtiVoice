"""Offline baseline runner with explicit, non-destructive output paths."""
import argparse, datetime, json, sys
from pathlib import Path
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT))
from agriculture_engine import parse_question

def main():
    p=argparse.ArgumentParser(); p.add_argument('--corpus',default=str(ROOT/'PHASE1_LANGUAGE_EVALUATION_CANDIDATE_V2.jsonl')); p.add_argument('--results-output',default=str(ROOT/'evaluation/phase1_baseline_results.jsonl')); p.add_argument('--report-output',default=str(ROOT/'PHASE1_BASELINE_EVALUATION_REPORT.md')); p.add_argument('--overwrite',action='store_true'); a=p.parse_args()
    corpus=Path(a.corpus); out=Path(a.results_output); report=Path(a.report_output)
    if not corpus.is_file(): raise SystemExit(f'Corpus not found: {corpus}')
    if (out.exists() or report.exists()) and not a.overwrite: raise SystemExit('Refusing to overwrite existing output; use distinct paths or --overwrite.')
    rows=[json.loads(x) for x in corpus.read_text(encoding='utf-8').splitlines()]; results=[]; crop_n=crop_d=sym_n=sym_d=wrong=exceptions=0; excluded={}
    for r in rows:
        expected=r.get('expected_observations',[]); eligible=bool(expected) and not r.get('expected_empty_classification'); reasons=[] if eligible else [r.get('expected_empty_classification') or 'UNCLASSIFIED_EMPTY_OBSERVATIONS']
        try:
            actual=parse_question(r['original_sentence']); status='COMPARABLE' if eligible else 'EXCLUDED'
            crop=r.get('expected_crop',{}).get('value')
            if crop is not None: crop_d+=1; crop_n+=actual.get('crop')==crop
            exp=[o.get('normalized_value') for o in expected if o.get('kind')=='symptom' and o.get('polarity')=='present']
            if eligible and exp: sym_d+=1; sym_n+=actual.get('symptom') in exp; wrong+=actual.get('symptom') is not None and actual.get('symptom') not in exp
            error=None
        except Exception as e: actual={}; status='EXCEPTION'; error=type(e).__name__; reasons.append(error); exceptions+=1
        for x in reasons: excluded[x]=excluded.get(x,0)+1
        results.append({'record_id':r['id'],'original_sentence':r['original_sentence'],'input_characteristics':r.get('input_characteristics',[]),'draft_expected':{'crop':r.get('expected_crop'),'observations':expected},'actual_parser_output':actual,'mapped_comparable_fields':{'crop':actual.get('crop'),'single_symptom':actual.get('symptom')},'comparison_status':status,'unsupported_fields':['intents','polarity','plant_parts','context','confidence','multi_symptom','follow_up_history'],'exclusion_reasons':reasons,'exception':error,'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in results)+'\n',encoding='utf-8')
    pct=lambda n,d:'N/A' if not d else f'{100*n/d:.1f}%'; report.parent.mkdir(parents=True,exist_ok=True); report.write_text(f'# Phase 1 Provisional Baseline Evaluation\n\nDraft-data results only. Corpus records: {len(rows)}. Crop: {crop_n}/{crop_d} ({pct(crop_n,crop_d)}). Single symptom: {sym_n}/{sym_d} ({pct(sym_n,sym_d)}). Incorrect activations: {wrong}. Exceptions: {exceptions}. Exclusions: {excluded}.\n\nUnsupported fields are not scored.\n',encoding='utf-8')
    print(json.dumps({'records':len(rows),'crop':f'{crop_n}/{crop_d}','symptom':f'{sym_n}/{sym_d}','incorrect':wrong,'exceptions':exceptions,'excluded':excluded}))
if __name__=='__main__': main()
