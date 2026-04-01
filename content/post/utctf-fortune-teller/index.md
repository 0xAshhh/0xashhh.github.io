---
title: "UTCTF 2026: Fortune Teller"
description: "Writeup for Fortune Teller from UTCTF 2026. Challenge weight: 961 points."
slug: utctf-fortune-teller
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Cryptography
tags:
    - writeup
    - utctf-2026
    - fortune-teller
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Fortune Teller`
- Category: `Cryptography`
- Points: `961`


## Solve Path

1) Category detection

- Detected category: `crypto`
- Confidence: high
- Evidence: `lcg.txt` explicitly gives an LCG over `m = 2^32`, four consecutive outputs, and says the flag was XORed with `output_5` as a 4-byte repeating key.

2) Attack strategy

- Primary hypothesis: recover the LCG parameters from the first four states, compute `output_5`, then XOR-decrypt the ciphertext.
- Why this is minimal: for an LCG,
  `x_(n+1) = a*x_n + c mod m`, so with consecutive outputs:
  `a = (x3 - x2) * (x2 - x1)^(-1) mod m`, then `c = x2 - a*x1 mod m`.
- Validation test: recompute `x3` and `x4` from the recovered `a, c`. If both match, derive `x5` and decrypt.

3) Execution steps

- Compute differences:
  `d1 = x2 - x1 mod 2^32 = 2799810421`
  `d2 = x3 - x2 mod 2^32 = 3154644521`
- Since `gcd(d1, 2^32) = 1`, `d1` is invertible modulo `2^32`.
- Recover parameters:
  `a = 3355924837`
  `c = 2915531925`
- Verify:
  `a*x2 + c mod 2^32 = 1541137174 = x3`
  `a*x3 + c mod 2^32 = 3272915523 = x4`
- Compute next output:
  `output_5 = x5 = 1233863684`
- Convert `x5` to a 4-byte key:
  big-endian bytes = `49 8b 44 04`
- XOR the ciphertext with that repeating key:
  plaintext = `utflag{pr3d1ct_th3_futur3_lcg}`

Repro command:
```powershell
@'
xs = [4176616824, 2681459949, 1541137174, 3272915523]
ct = bytes.fromhex("3cff226828ec3f743bb820352aff1b7021b81b623cff31767ad428672ef6")
m = 2**32
x1,x2,x3,x4 = xs
a = ((x3-x2) % m) * pow((x2-x1) % m, -1, m) % m
c = (x2 - a*x1) % m
x5 = (a*x4 + c) % m
key = x5.to_bytes(4, "big")
pt = bytes(b ^ key[i % 4] for i, b in enumerate(ct))
print(a, c, x5, key.hex(), pt.decode())
'@ | python -
```

4) FLAG

`utflag{pr3d1ct_th3_futur3_lcg}`

5) Writeup

The challenge hands you four consecutive LCG outputs and tells you the flag was XORed with the fifth output as a repeating 4-byte key. Because the modulus is `2^32` and `x2-x1` is odd, that difference has a modular inverse, so `a` can be recovered directly from two adjacent differences. From there, `c` follows immediately. The recovered parameters reproduce the known outputs exactly, proving the state recovery is correct. Advancing once gives `output_5 = 1233863684`, whose big-endian bytes `49 8b 44 04` decrypt the ciphertext to the valid flag `utflag{pr3d1ct_th3_futur3_lcg}`.
