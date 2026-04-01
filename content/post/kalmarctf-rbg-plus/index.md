---
title: "KalmarCTF 2026: RBG+"
description: "Writeup for RBG+ from KalmarCTF 2026. Challenge weight: 1000 points."
slug: kalmarctf-rbg-plus
date: 2026-03-27 17:05:43.087+0000
competition: "KalmarCTF 2026"
categories:
    - Cryptography
tags:
    - writeup
    - kalmarctf-2026
    - rbg+
---

## Challenge

- Competition: [KalmarCTF 2026](https://kalmarc.tf/)
- Challenge: `RBG+`
- Category: `Cryptography`
- Points: `1000`


## Solve Path

1) Category detection
- `crypto`, confidence high. Evidence: RSA-style modulus `N = p*q`, modular exponentiation `pow(m, e, N)`, and an LCG update `e <- 3e + 1337 (mod N)`.

2) Attack strategy
- Let `c_i = m^{e_i} mod N` and `y_i = c_i + c_{i+1}`. The sums make every `c_i` an affine function of `c_0`.
- Because `e_{i+1} = 3e_i + 1337 - q_i N` with known `q_i in {0,1,2}`, the residues satisfy `c_{i+1} ≡ B * D^{q_i} * c_i^3 (mod N)` for fixed unknowns `B, D`.
- For indices with the same `q_i`, the unknown multiplier cancels: `c_{i+1} c_j^3 ≡ c_{j+1} c_i^3 (mod N)`. After substituting the affine forms, these become cubic polynomials in `c_0`. Their gcd modulo `N` is linear, which recovers `c_0`.

3) Execution steps
- Parsed the provided output and built the affine residue chain.
- Computed the common polynomial gcd modulo `N`, which gave `c_0 = 306601066755714804869508880426525687654812111328465119672604886895194149996027634910723081737328697966456584392379680730523462585779139283564580976741383463062630061858607039415252337947157977855199531076303335406520433962`.
- Recovered all `c_i` from the printed sums.
- Since `gcd(e_0, e_1) = 1`, used extended gcd to get `u, v` with `u e_0 + v e_1 = 1`, then recovered `m = c_0^u c_1^v mod N`.
- Verified `pow(m, e_i, N) == c_i` for all 14 exponents.
- Reproducible solver: `solve_rbg_plus.py`

4) FLAG
- `kalmar{GCD_is_handy_like_always}`

5) Writeup
- The key weakness is the raw sum leak plus reuse of a structured exponent stream. The LCG relation lets you group transitions by the same wrap count `q_i`, eliminate the hidden multiplier, and reduce the problem to low-degree congruences in the first ciphertext residue. Once `c_0` is known, the rest of the residues and then the plaintext follow immediately.
