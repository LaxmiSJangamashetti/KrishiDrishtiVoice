"""Measure ONNX parity, validation calibration, and a labeled unknown protocol."""
from __future__ import annotations

import argparse
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image


def preprocess(path: Path, metadata: dict) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    h, w = metadata["input_size"]
    image = image.resize((w, h), Image.Resampling.BILINEAR)
    x = np.asarray(image, dtype=np.float32) / 255.0
    x = (x - np.asarray(metadata["preprocessing"]["mean"])) / np.asarray(metadata["preprocessing"]["std"])
    return x.transpose(2, 0, 1)


def metrics(logits: np.ndarray, labels: np.ndarray, temperature: float = 1.0) -> dict:
    z = logits / temperature
    z -= z.max(axis=1, keepdims=True)
    p = np.exp(z); p /= p.sum(axis=1, keepdims=True)
    pred = p.argmax(1); conf = p.max(1)
    correct = pred == labels
    n = len(labels)
    nll = float(-np.log(np.clip(p[np.arange(n), labels], 1e-12, 1)).mean())
    onehot = np.eye(p.shape[1])[labels]
    brier = float(((p - onehot) ** 2).sum(axis=1).mean())
    ece = 0.0
    for lo, hi in zip(np.linspace(0, 1, 11)[:-1], np.linspace(0, 1, 11)[1:]):
        mask = (conf >= lo) & ((conf < hi) if hi < 1 else (conf <= hi))
        if mask.any(): ece += float(mask.mean()) * abs(float(conf[mask].mean()) - float(correct[mask].mean()))
    accepted = conf >= 0.60
    return {"accuracy": float(correct.mean()), "ece": float(ece), "nll": nll, "brier": brier, "coverage_at_0_60": float(accepted.mean()), "selective_error_at_0_60": float((~correct[accepted]).mean()) if accepted.any() else None, "mean_confidence": float(conf.mean())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", required=True); ap.add_argument("--validation", required=True)
    ap.add_argument("--onnx", required=True); ap.add_argument("--metadata", required=True)
    ap.add_argument("--archive", required=True); ap.add_argument("--output", required=True)
    args = ap.parse_args()
    import onnxruntime as ort
    import torch
    from torchvision import models

    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    classes = [metadata["class_mapping"][str(i)] for i in range(len(metadata["class_mapping"]))]
    class_index = {name: i for i, name in enumerate(classes)}
    session = ort.InferenceSession(args.onnx, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    model = models.mobilenet_v3_small(weights=None); model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(classes))
    model.load_state_dict(torch.load(Path(args.onnx).parent.parent / "mobilenet_v3_small_tomato.pt", map_location="cpu", weights_only=True)); model.eval()

    def collect(root: str):
        xs=[]; ys=[]
        for folder in sorted(Path(root).iterdir()):
            if not folder.is_dir() or folder.name not in class_index: continue
            for path in sorted(folder.iterdir())[:30]:
                try: x=preprocess(path, metadata)
                except (OSError, ValueError): continue
                xs.append(x); ys.append(class_index[folder.name])
        ort_all=[]; pt_all=[]
        for start in range(0, len(xs), 64):
            batch=np.asarray(xs[start:start+64], dtype=np.float32)
            ort_all.append(session.run(None, {input_name:batch})[0])
            with torch.no_grad(): pt_all.append(model(torch.from_numpy(batch)).numpy())
        ort_logits=np.concatenate(ort_all); pt_logits=np.concatenate(pt_all)
        op=np.exp(ort_logits-ort_logits.max(1,keepdims=True)); op/=op.sum(1,keepdims=True)
        pp=np.exp(pt_logits-pt_logits.max(1,keepdims=True)); pp/=pp.sum(1,keepdims=True)
        agreements=(ort_logits.argmax(1)==pt_logits.argmax(1)).astype(int).tolist()
        confdiff=np.abs(op.max(1)-pp.max(1)).tolist()
        return ort_logits, np.asarray(ys), agreements, confdiff

    val_logits, val_labels, _, _ = collect(args.validation)
    test_logits, test_labels, agreements, confdiff = collect(args.test)
    candidates=np.arange(0.50,3.01,0.01); best=min(candidates, key=lambda t: metrics(val_logits,val_labels,float(t))["nll"])
    before=metrics(val_logits,val_labels); after=metrics(val_logits,val_labels,float(best)); test=metrics(test_logits,test_labels,float(best))

    unknown=[]; unknown_counts={}
    wanted=("Rice", "Potato", "Maize", "Corn", "Chilli", "Pepper")
    with zipfile.ZipFile(args.archive) as z:
        for name in z.namelist():
            if not name.lower().endswith((".jpg", ".jpeg", ".png")) or "raw/color/" not in name: continue
            parent=name.split("/")[-2]
            if any(w.lower() in parent.lower() for w in wanted) and unknown_counts.get(parent, 0) < 40:
                unknown.append((name,parent,z.read(name))); unknown_counts[parent]=unknown_counts.get(parent, 0)+1
    unknown_conf=[]
    for _,_,data in unknown:
        try:
            x=preprocess(io.BytesIO(data), metadata) if False else preprocess(Path("\\\\?\\"), metadata)
        except Exception:
            image=Image.open(io.BytesIO(data)).convert("RGB"); h,w=metadata["input_size"]; image=image.resize((w,h),Image.Resampling.BILINEAR); x=np.asarray(image,dtype=np.float32)/255.; x=(x-np.asarray(metadata["preprocessing"]["mean"]))/np.asarray(metadata["preprocessing"]["std"]); x=x.transpose(2,0,1)
        logits=session.run(None,{input_name:x[None].astype(np.float32)})[0][0]; q=np.exp(logits-logits.max()); q/=q.sum(); unknown_conf.append(float(q.max()))
    result={"calibration":{"temperature":float(best),"validation_before":before,"validation_after":after,"independence_note":"Validation data was used for model development; calibration is provisional, not independent of model selection."},"export_parity":{"sample_count":len(agreements),"top1_agreement":float(np.mean(agreements)),"mean_confidence_difference":float(np.mean(confdiff))},"test_after_calibration":test,"unknown_protocol":{"source":"PlantVillage archive already acquired; non-tomato RGB classes only; no PlantDoc", "sample_count":len(unknown),"categories":sorted(set(parent for _,parent,_ in unknown)),"false_acceptance_at_0_60":float(np.mean(np.asarray(unknown_conf)>=0.60)) if unknown_conf else None,"mean_max_confidence":float(np.mean(unknown_conf)) if unknown_conf else None,"development_only":True}}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    export_meta=Path(args.metadata); metadata["calibration"]={"temperature":float(best),"method":"validation_grid_temperature_scaling","metrics":result["calibration"]}; metadata["rejection"]={"method":"calibrated_maximum_softmax_only","confidence_threshold":0.60,"status":"provisional"}; export_meta.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
