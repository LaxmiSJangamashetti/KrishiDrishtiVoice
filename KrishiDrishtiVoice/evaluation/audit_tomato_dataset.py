"""Audit image integrity, dimensions, exact duplicates and class distribution."""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("dataset",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); report={"dataset":str(a.dataset),"classes":{},"total":0,"corrupt":[],"exact_duplicate_groups":0,"dimensions":{},"format_counts":{}}; hashes=defaultdict(list); sizes=Counter(); formats=Counter()
    for path in sorted(a.dataset.rglob("*")):
        if not path.is_file(): continue
        cls=path.parent.name; report["classes"].setdefault(cls,{"count":0,"bytes":0}); report["classes"][cls]["count"]+=1; report["classes"][cls]["bytes"]+=path.stat().st_size; report["total"]+=1
        try:
            with Image.open(path) as image: image.verify()
            with Image.open(path) as image: sizes[f"{image.width}x{image.height}"]+=1; formats[image.format]+=1
            hashes[hashlib.sha256(path.read_bytes()).hexdigest()].append(str(path))
        except Exception as exc: report["corrupt"].append({"path":str(path),"error":str(exc)})
    report["dimensions"]=dict(sizes); report["format_counts"]=dict(formats); report["exact_duplicate_groups"]=sum(1 for paths in hashes.values() if len(paths)>1); report["exact_duplicate_images"]=sum(len(paths)-1 for paths in hashes.values() if len(paths)>1); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2),encoding="utf-8"); print(json.dumps({"total":report["total"],"corrupt":len(report["corrupt"]),"classes":{k:v["count"] for k,v in report["classes"].items()},"exact_duplicate_groups":report["exact_duplicate_groups"]},indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
