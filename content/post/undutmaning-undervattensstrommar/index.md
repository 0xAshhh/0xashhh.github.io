---
title: "Undutmaning 2026: Undervattensströmmar"
description: "Reconstructed Codex writeup for Undervattensströmmar from Undutmaning 2026. Original prompt weight: 500 points."
slug: undutmaning-undervattensstrommar
date: 2026-03-21 11:01:06.497+0000
categories:
    - Cryptography
tags:
    - codex-archive
    - undutmaning-2026
    - undervattensströmmar
---

## Challenge

- Competition: [Undutmaning 2026](https://undutmaning.se/)
- Challenge: `Undervattensströmmar`
- Category: `Cryptography`
- Points: `500`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Undervattensströmmar svår krypto Under en utflykt i de mer trasiga delarna av CASCADA har Harriet hittat ett USB-minne, märkt Viktigt!!!. Dra på trissor! Inte mindre än tre utropstecken, så det måste vara något i hästväg! Tyvärr är stickan illa åtgången och har minst ett...


## Solve Path

1) Category detection
- Detected category: `crypto`
- Confidence: high
- Evidence: `ibtool.c` encrypts with XOR against a 16-bit LCG keystream, and the plaintext file must start with the fixed header `IBTOOLBACKUP\x00\x00`.

2) Attack strategy
- Primary hypothesis: use the known 14-byte header to recover the first 7 keystream words, then solve the LCG parameters `(a, c, m)` from those outputs.
- Validation: decrypt the full file and check whether the result has a real file signature.

3) Execution steps
- XORing the first 14 ciphertext bytes with the known header gave keystream words:
  `1b3d 1308 55dd 22f5 17a1 45be 01d6`
- Solving `x[n+1] = (a*x[n] + c) mod m` over those values gave a unique LCG:
  `m = 22661`, `a = 35`, `c = 10088`
- A valid seed representative is `22572` modulo `22661` (`45233` is equivalent as a `uint16_t` seed).
- Decrypting with that keystream produced:
  `IBTOOLBACKUP\x00\x00` followed by gzip magic `1f 8b 08`
- Decompressing the gzip yielded a tar archive containing member `f2`, whose contents were:
  `undut{lcg_w4s_n3v3r_s4f3}`

4) FLAG
`undut{lcg_w4s_n3v3r_s4f3}`

5) Writeup
- The tool leaks enough keystream immediately because the backup header is fixed and known.
- Those 7 known keystream outputs are enough to uniquely recover the LCG parameters.
- Once the stream is reconstructed, the ciphertext decrypts cleanly into a gzip-compressed tar archive.
- The recovered tar member contains the flag, so the result is proven.
