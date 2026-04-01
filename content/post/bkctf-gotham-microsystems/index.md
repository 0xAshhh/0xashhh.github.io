---
title: "BKCTF: Gotham MicroSystems"
description: "Writeup for Gotham MicroSystems from BKCTF."
slug: bkctf-gotham-microsystems
date: 2026-02-21 19:51:09.862+0000
competition: "BKCTF"
categories:
    - Cryptography
tags:
    - writeup
    - bkctf
    - gotham-microsystems
---

## Challenge

- Competition: `BKCTF`
- Challenge: `Gotham MicroSystems`
- Category: `Cryptography`


## Solve Path

1) Category detection
- `crypto` (high confidence): AES-CBC service with user-supplied ciphertext decryption in ``Downloads/Server` (2).java`.

2) Attack strategy
- Bypass check `uInput.equals(encString)` by changing only hex letter case.
- `HexFormat.of().parseHex(uInput)` is case-insensitive, so lowercase decodes to identical bytes.

3) Execution steps
- Connected to `gotham-microsystems-fd36ad5aa10df4e5.instancer.batmans.kitchen:1337` with SSL.
- Read welcome ciphertext (uppercase hex).
- Sent the same ciphertext in lowercase.
- Server accepted it as a different string, decrypted to original plaintext, and returned flag.

4) FLAG
- `bkctf{b4rb4r4_g0rd0ns_f4v0r1t3_4tt4ck}`

5) Writeup
- The auth gate compares raw input string to block replay (`equals(encString)`), but this is not a byte-level check.
- Lowercasing the ciphertext avoids the string match while preserving identical ciphertext bytes after `parseHex`.
- Decryption output equals stored `plaintext`, so the success branch is reached and flag is disclosed.
