---
title: "BKCTF: Appreciating Graphic Design"
description: "Writeup for Appreciating Graphic Design from BKCTF."
slug: bkctf-appreciating-graphic-design
date: 2026-02-22 10:17:02.853+0000
competition: "BKCTF"
categories:
    - Misc
tags:
    - writeup
    - bkctf
    - appreciating-graphic-design
---

## Challenge

- Competition: `BKCTF`
- Challenge: `Appreciating Graphic Design`
- Category: `Misc`


## Solve Path

1) Category detection
- `misc` (stego/forensics), high confidence.
- Evidence: the supplied `.png` has PSD magic (`8BPS`), many hidden/overlay layers, and explicit `STEG!!` clues.

2) Attack strategy
- Minimal hypothesis: the flag is hidden in non-obvious PSD layers rather than normal visible text.
- Validate by extracting raw hidden/visible layer rasters and reading anomalous text layers/assets.

3) Execution steps
- Confirmed file type mismatch (`8BPS` header).
- Parsed PSD structure (63 layers), extracted smart objects, and rendered hidden/visible composites.
- Exported raw layers with `topil()` and found the decisive payload in `raw_layers/025_vis_pixel_Layer_42.png`.
- Zooming that layer reveals the full flag string; component segmentation confirms final word is `0ni0n` and ends with `}`.

4) FLAG
`bkctf{4rt_h4z_l4y3rz_l1k3_0ni0n}`

5) Writeup
- The “PNG” is actually a PSD with layered decoys and clues (`Access here`, `STEG!!`).
- The true payload is a rasterized hidden text strip in `Layer 42`.
- Reading that strip yields the final flag exactly above.
