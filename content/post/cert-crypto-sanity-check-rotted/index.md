---
title: "CERT: Crypto Sanity Check - rotted"
description: "Writeup for Crypto Sanity Check rotted from CERT."
slug: cert-crypto-sanity-check-rotted
date: 2026-03-01 13:14:36.166+0000
competition: "CERT"
categories:
    - Cryptography
tags:
    - writeup
    - cert
    - crypto-sanity-check-rotted
---

## Challenge

- Competition: `CERT`
- Challenge: `Crypto Sanity Check rotted`
- Category: `Cryptography`


## Solve Path

1) Category detection  
- Detected category: `crypto`  
- Confidence: `high`  
- Evidence: challenge name includes “rotted”, and ciphertext `FX-PREG{...}` looks like a ROT-substituted flag format.

2) Attack strategy  
- Primary hypothesis: apply `ROT13` to the full string.  
- Why minimal: lowest-cost test for a “rotted” sanity-check crypto challenge.  
- Validation test: decode once and check if result is a clean CTF-style flag.

3) Execution steps  
- Command used:
```bash
python -c "import codecs; s='FX-PREG{flzz37evp_e0747v0a}'; print(codecs.decode(s,'rot_13'))"
```
- Output:
```text
SK-CERT{symm37ric_r0747i0n}
```

4) FLAG  
`SK-CERT{symm37ric_r0747i0n}`

5) Writeup  
The prompt strongly suggests a ROT-family substitution. Applying ROT13 directly to the provided ciphertext transforms it into a valid-looking flag with meaningful leetspeak (`symm37ric_r0747i0n`), confirming the hypothesis.
