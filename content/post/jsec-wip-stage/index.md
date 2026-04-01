---
title: "JSEC: Wip Stage"
description: "Writeup for Wip Stage from JSEC. Challenge weight: 100 points."
slug: jsec-wip-stage
date: 2026-03-06 20:07:32.863+0000
competition: "JSEC"
categories:
    - Cryptography
tags:
    - writeup
    - jsec
    - wip-stage
---

## Challenge

- Competition: `JSEC`
- Challenge: `Wip Stage`
- Category: `Cryptography`
- Points: `100`


## Solve Path

1) Category detection
- Detected category: `crypto` (confidence: high).
- Evidence: 312 notes give 624 raw 32-bit values (`X`,`Y`), exactly the MT19937 state size (624 words), and challenge asks to predict a far-future output.

2) Attack strategy
- Primary hypothesis: `X` and `Y` are consecutive outputs from one MT19937 PRNG.
- Minimal validation: untemper first 624 outputs, rebuild MT state, generate forward to output indices for note 3939 (`2*3939-1`, `2*3939`), then test payload decryption using derived SHA-256 key.

3) Execution steps
- Parsed `procedural_map (1).txt`.txt) and extracted 312 `(X,Y)` pairs.
- Flattened to 624 outputs: `x1,y1,x2,y2,...,x312,y312`.
- Untempered all 624 outputs to recover MT internal state.
- Advanced PRNG to outputs `7877` and `7878`:
  - `X3939 = 4077400209`
  - `Y3939 = 228196029`
- Computed:
  - `SHA256("4077400209_228196029") = 5d89cc3e1d396899cef720cb79cec227e3dec40a10969524743b13be1e21fd06`
- Decoded payload base64 and decrypted with AES-256-ECB using that SHA-256 digest as key, yielding plaintext:
  - `JSEC{m3rs3nn3_tw1st3r_1s_n0t_s3cur3_3939}`

4) FLAG
JSEC{m3rs3nn3_tw1st3r_1s_n0t_s3cur3_3939}

5) Writeup
- The “unpredictable” generator is MT19937 used directly for 32-bit coordinates.
- Because exactly 624 outputs were leaked, MT state recovery is complete and deterministic.
- Forward prediction gives note 3939 coordinates, whose `X_Y` hash is the decryption key.
- Decrypting the provided payload with that key recovers the flag above.
