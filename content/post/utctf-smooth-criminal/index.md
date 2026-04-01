---
title: "UTCTF 2026: Smooth Criminal"
description: "Writeup for Smooth Criminal from UTCTF 2026. Challenge weight: 967 points."
slug: utctf-smooth-criminal
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Cryptography
tags:
    - writeup
    - utctf-2026
    - smooth-criminal
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Smooth Criminal`
- Category: `Cryptography`
- Points: `967`


## Solve Path

1) Category detection

- Detected category: `crypto`
- Confidence: high
- Evidence: `dlp.txt` gives a classic finite-field DLP instance `h = g^x mod p` and asks to recover `x` and decode it as bytes.

2) Attack strategy

- Primary hypothesis: `p - 1` is smooth, so Pohlig-Hellman will recover `x` efficiently.
- Why it is minimal: the prompt explicitly hints the weakness is the group order, and for `F_p*` the relevant order is `p - 1`.
- Planned validation tests:
  1. Factor `p - 1` and check whether its prime factors are small.
  2. Confirm `g` has full order `p - 1`.
  3. Solve the DLP and verify `pow(g, x, p) == h`.
  4. Convert `x` to bytes and check for a valid flag string.

3) Execution steps

- Smoothness check:
  `factorint(p - 1)` shows `p - 1` has `45` distinct prime factors and the largest prime factor is only `197`.
- Generator check:
  `n_order(g, p) == p - 1`, so `g = 223` generates the full multiplicative group.
- Solve with Pohlig-Hellman:
```powershell
@'
from sympy import factorint
from sympy.ntheory import n_order
from sympy.ntheory.residue_ntheory import _discrete_log_pohlig_hellman

p = 1363402168895933073124331075716158793413739602475544713040662303260999503992311247861095036060712607168809958344896622485452229880797791800555191761456659256252204001928525518751268009081850267001
g = 223
h = 1009660566883490917987475170194560289062628664411983200474597006489640893063715494610197294704009188265361176318190659133132869144519884282668828418392494875096149757008157476595873791868761173517

f = factorint(p - 1)
x = _discrete_log_pohlig_hellman(p, h, g, p - 1, f)
print(x)
print(pow(g, x, p) == h)
print(x.to_bytes((x.bit_length() + 7) // 8, 'big').decode())
'@ | python -
```
- Key output:
  `x = 810642462826781236630409314742801724164468986543937060322593530182136957`
  `pow(g, x, p) == h -> True`
  decoded bytes -> `utflag{sm00th_cr1m1nal_caught}`

4) FLAG

`utflag{sm00th_cr1m1nal_caught}`

5) Writeup

The intended weakness is that the multiplicative group order `p - 1` is extremely smooth despite `p` being a 649-bit prime. That makes the DLP easy via Pohlig-Hellman: factor the group order, solve the log modulo each small prime power, then recombine with CRT. Here, `p - 1` factors entirely into tiny primes up to `197`, and `g` has full order, so the recovered exponent is unique modulo `p - 1`. The recovered `x` satisfies `g^x mod p = h`, and converting `x` from an integer to bytes yields the flag `utflag{sm00th_cr1m1nal_caught}`.
