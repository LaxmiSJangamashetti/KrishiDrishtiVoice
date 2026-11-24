"""Reproducible MobileNetV3-Small tomato classifier training."""
from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--dataset",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--epochs",type=int,default=2); p.add_argument("--batch-size",type=int,default=32); p.add_argument("--seed",type=int,default=42); p.add_argument("--device",default="cpu"); p.add_argument("--limit-per-class",type=int); p.add_argument("--pretrained",action="store_true"); p.add_argument("--learning-rate",type=float,default=1e-3); a=p.parse_args()
    if not a.dataset.exists(): raise SystemExit("BLOCKED: approved dataset path does not exist.")
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed); device=torch.device(a.device if a.device!="auto" else ("cuda" if torch.cuda.is_available() else "cpu")); base=datasets.ImageFolder(a.dataset); by={c:[] for c in base.classes}
    for i,(_,y) in enumerate(base.samples): by[base.classes[y]].append(i)
    rng=random.Random(a.seed); selected=[]
    for ids in by.values(): rng.shuffle(ids); selected.extend(ids[:a.limit_per_class] if a.limit_per_class else ids)
    targets=[base.targets[i] for i in selected]; train_idx,rem,_,rem_y=train_test_split(selected,targets,test_size=.30,random_state=a.seed,stratify=targets); val_idx,test_idx=train_test_split(rem,test_size=.50,random_state=a.seed,stratify=rem_y)
    norm=([.485,.456,.406],[.229,.224,.225]); train_tf=transforms.Compose([transforms.Resize((224,224)),transforms.RandomHorizontalFlip(),transforms.RandomRotation(8),transforms.ToTensor(),transforms.Normalize(*norm)]); eval_tf=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor(),transforms.Normalize(*norm)]); train_ds=Subset(datasets.ImageFolder(a.dataset,transform=train_tf),train_idx); val_ds=Subset(datasets.ImageFolder(a.dataset,transform=eval_tf),val_idx); train_loader=DataLoader(train_ds,batch_size=a.batch_size,shuffle=True,num_workers=0); val_loader=DataLoader(val_ds,batch_size=a.batch_size,shuffle=False,num_workers=0)
    model=models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT if a.pretrained else None)
    for q in model.features.parameters(): q.requires_grad=False
    model.classifier[3]=nn.Linear(model.classifier[3].in_features,len(base.classes)); model.to(device); opt=torch.optim.Adam(model.classifier[3].parameters(),lr=a.learning_rate); loss_fn=nn.CrossEntropyLoss(); history=[]; best=float("inf"); a.output.mkdir(parents=True,exist_ok=True)
    for epoch in range(a.epochs):
        model.train(); train_loss=0
        for x,y in train_loader: opt.zero_grad(); loss=loss_fn(model(x.to(device)),y.to(device)); loss.backward(); opt.step(); train_loss+=loss.item()*len(y)
        model.eval(); val_loss=0; correct=0; count=0
        with torch.no_grad():
            for x,y in val_loader: out=model(x.to(device)); y=y.to(device); val_loss+=loss_fn(out,y).item()*len(y); correct+=(out.argmax(1)==y).sum().item(); count+=len(y)
        row={"epoch":epoch+1,"train_loss":train_loss/max(1,len(train_ds)),"val_loss":val_loss/max(1,count),"val_accuracy":correct/max(1,count)}; history.append(row); print(json.dumps(row))
        torch.save(model.state_dict(), a.output/f"checkpoint_epoch_{epoch+1}.pt")
        if row["val_loss"]<best: best=row["val_loss"]; torch.save(model.state_dict(),a.output/"mobilenet_v3_small_tomato.pt")
    weights_path=a.output/"mobilenet_v3_small_tomato.pt"; digest=hashlib.sha256(weights_path.read_bytes()).hexdigest(); meta={"model_version":"tomato-mobilenet-v3-small-exp1","architecture":"mobilenet_v3_small","class_mapping":{str(i):c for i,c in enumerate(base.classes)},"input_size":[224,224],"preprocessing":{"mean":norm[0],"std":norm[1]},"dataset":"PlantVillage RGB tomato subset","seed":a.seed,"limit_per_class":a.limit_per_class,"split_counts":{"train":len(train_idx),"validation":len(val_idx),"test":len(test_idx)},"device":str(device),"weights_sha256":digest,"abstention_threshold":0.60,"status":"experimental"}; (a.output/"metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8"); (a.output/"history.json").write_text(json.dumps(history,indent=2),encoding="utf-8"); (a.output/"split_manifest.json").write_text(json.dumps({"train":train_idx,"validation":val_idx,"test":test_idx},indent=2),encoding="utf-8"); return 0

if __name__ == "__main__": raise SystemExit(main())
