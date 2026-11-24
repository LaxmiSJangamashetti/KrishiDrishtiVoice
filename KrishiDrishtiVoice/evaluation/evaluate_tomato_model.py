"""Held-out evaluation for the trained MobileNetV3-Small experiment."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--model",type=Path,required=True); p.add_argument("--test-data",type=Path,required=True); p.add_argument("--metadata",type=Path,required=True); a=p.parse_args()
    if not a.model.exists() or not a.test_data.exists(): raise SystemExit("BLOCKED: model or independent test data is missing.")
    meta=json.loads(a.metadata.read_text(encoding="utf-8")); classes=[meta["class_mapping"][str(i)] for i in range(len(meta["class_mapping"]))]; ds=datasets.ImageFolder(a.test_data,transform=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor(),transforms.Normalize(meta["preprocessing"]["mean"],meta["preprocessing"]["std"])]))
    if ds.classes!=classes: raise SystemExit(f"BLOCKED: class mapping mismatch: {ds.classes} != {classes}")
    model=models.mobilenet_v3_small(weights=None); model.classifier[3]=torch.nn.Linear(model.classifier[3].in_features,len(classes)); model.load_state_dict(torch.load(a.model,map_location="cpu",weights_only=True)); model.eval(); ys=[]; ps=[]; elapsed=0.0
    with torch.no_grad():
        for x,y in DataLoader(ds,batch_size=32,shuffle=False,num_workers=0): start=time.perf_counter(); out=model(x); elapsed+=time.perf_counter()-start; ys.extend(y.tolist()); ps.extend(out.argmax(1).tolist())
    pre,rec,f1,sup=precision_recall_fscore_support(ys,ps,labels=list(range(len(classes))),zero_division=0); report={"accuracy":accuracy_score(ys,ps),"balanced_accuracy":balanced_accuracy_score(ys,ps),"macro_precision":float(np.mean(pre)),"macro_recall":float(np.mean(rec)),"macro_f1":float(np.mean(f1)),"per_class":{c:{"precision":float(pre[i]),"recall":float(rec[i]),"f1":float(f1[i]),"support":int(sup[i])} for i,c in enumerate(classes)},"confusion_matrix":confusion_matrix(ys,ps,labels=list(range(len(classes)))).tolist(),"sample_count":len(ys),"cpu_batch_inference_seconds":elapsed}; print(json.dumps(report,indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
