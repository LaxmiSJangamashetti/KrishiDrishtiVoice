"""Compare a PyTorch checkpoint and ONNX export on a deterministic sample."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument('--weights',required=True); p.add_argument('--metadata',required=True); p.add_argument('--onnx',required=True); p.add_argument('--data',required=True); a=p.parse_args()
    import onnxruntime as ort
    import torch
    from torchvision import models
    m=json.loads(Path(a.metadata).read_text(encoding='utf-8')); classes=[m['class_mapping'][str(i)] for i in range(len(m['class_mapping']))]
    model=models.mobilenet_v3_small(weights=None); model.classifier[3]=torch.nn.Linear(model.classifier[3].in_features,len(classes)); model.load_state_dict(torch.load(a.weights,map_location='cpu',weights_only=True)); model.eval()
    sess=ort.InferenceSession(a.onnx,providers=['CPUExecutionProvider']); name=sess.get_inputs()[0].name
    paths=sorted([p for p in Path(a.data).rglob('*') if p.is_file()])[:30*len(classes)]; xs=[]; ys=[]
    for pth in paths:
        x=np.asarray(Image.open(pth).convert('RGB').resize((224,224)),dtype=np.float32)/255.; x=(x-np.asarray(m['preprocessing']['mean']))/np.asarray(m['preprocessing']['std']); xs.append(x.transpose(2,0,1)); ys.append(pth.parent.name)
    x=np.asarray(xs,dtype=np.float32); on=sess.run(None,{name:x})[0];
    with torch.no_grad(): pt=model(torch.from_numpy(x)).numpy()
    result={'sample_count':len(xs),'top1_agreement':float(np.mean(on.argmax(1)==pt.argmax(1))),'mean_max_probability_difference':float(np.mean(np.abs((np.exp(on-on.max(1,keepdims=True))/np.exp(on-on.max(1,keepdims=True)).sum(1,keepdims=True)).max(1)-(np.exp(pt-pt.max(1,keepdims=True))/np.exp(pt-pt.max(1,keepdims=True)).sum(1,keepdims=True)).max(1))))}
    print(json.dumps(result))


if __name__ == '__main__': main()
