---
title: "UTCTF 2026: QRecreate"
description: "Writeup for QRecreate from UTCTF 2026. Challenge weight: 977 points."
slug: utctf-qrecreate
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Misc
tags:
    - writeup
    - utctf-2026
    - qrecreate
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `QRecreate`
- Category: `Misc`
- Points: `977`


## Solve Path

1) Category detection

- Detected category: `misc`
- Confidence: high
- Evidence: `TaxReports2008.zip` extracts into `100` numbered directories, each containing one `74x74` PNG. The directory names are base64-encoded indices (`MDAx` -> `001`, ..., `MTAw` -> `100`), and the images visually form QR-style fragments.

2) Attack strategy

- Primary hypothesis: the PNGs are tiles of one larger QR code, ordered by the decoded directory indices.
- Why it is minimal: the filenames already give a clean `001..100` ordering, and the corner tiles visibly contain QR finder patterns consistent with a `10x10` mosaic.
- Planned validation tests:
  1. Decode folder names from base64 and sort numerically.
  2. Stitch the 100 tiles into a `10x10` image.
  3. Decode the reconstructed QR payload.
  4. Check for one more embedded encoding layer in the decoded text.

3) Execution steps

- Confirmed structure:
  - `count 100`
  - indices decoded from folder names are exactly `1..100`
  - each `img.png` is `74x74`
- Reconstruction script:
```powershell
@'
from pathlib import Path
from PIL import Image
import base64, zxingcpp

root = Path(r'`TaxReports2008_extracted/output`')
items = sorted(root.iterdir(), key=lambda d: int(base64.b64decode(d.name).decode()))

canvas = Image.new('RGB', (74 * 10, 74 * 10), 'white')
for d in items:
    idx = int(base64.b64decode(d.name).decode())
    r = (idx - 1) // 10
    c = (idx - 1) % 10
    canvas.paste(Image.open(d / 'data' / 'img.png'), (c * 74, r * 74))

text = zxingcpp.read_barcode(canvas).text
print(text)
'@ | python -
```
- Key output: the reconstructed QR decodes to lorem ipsum text containing:
  `dXRmbGFne3MzY3IzdHNfQHJlX0Bsd0B5c193MXRoMW5fczNjcjN0c30=`
- Final decode:
```powershell
@'
import base64
print(base64.b64decode("dXRmbGFne3MzY3IzdHNfQHJlX0Bsd0B5c193MXRoMW5fczNjcjN0c30=").decode())
'@ | python -
```
- Output:
  `utflag{s3cr3ts_@re_@lw@ys_w1th1n_s3cr3ts}`

4) FLAG

`utflag{s3cr3ts_@re_@lw@ys_w1th1n_s3cr3ts}`

5) Writeup

The archive is a tiled exfil format. Each folder name is a base64-encoded sequence number, and the 100 PNGs are QR fragments rather than standalone codes. Sorting by decoded index and placing them row-major into a `10x10` grid reconstructs a full QR image.

That QR does not contain the flag directly. Its text payload is filler with one embedded base64 token. Decoding that token yields the final flag: `utflag{s3cr3ts_@re_@lw@ys_w1th1n_s3cr3ts}`.
