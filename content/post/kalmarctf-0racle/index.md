---
title: "KalmarCTF 2026: 0racle"
description: "Writeup for 0racle from KalmarCTF 2026. Challenge weight: 145 points."
slug: kalmarctf-0racle
date: 2026-03-27 19:48:40.957+0000
competition: "KalmarCTF 2026"
categories:
    - Reverse Engineering
tags:
    - writeup
    - kalmarctf-2026
    - 0racle
---

## Challenge

- Competition: [KalmarCTF 2026](https://kalmarc.tf/)
- Challenge: `0racle`
- Category: `Reverse Engineering`
- Points: `145`


## Solve Path

1) Category detection

Detected category: `rev` with high confidence. Evidence: `0racle.exe` is a 32-bit Windows GUI PE built with Lazarus/Delphi, exposing `inputFieldKeyPress` handlers and a staged validation blob copied from `.data` into RWX memory.

2) Attack strategy

I located the input handler from the Lazarus method table, disassembled it, extracted the staged blob, derived its 7-byte decrypt key from the required NOP prelude, then analyzed the decrypted 64-bit second stage. That second stage gave the uppercase flag template and seven FNV-1 segment hashes, which uniquely fixed the mixed-case letters.

3) Execution steps

- `inputFieldKeyPress` copies `0x4b7` bytes from `.data` at `0x556260` and executes them.
- The first-stage x86 stub decrypts the payload with the first 7 input bytes; forcing its first decrypted bytes to `0x90` yields `kalmar{`.
- The decrypted 64-bit stage uppercases the input and checks it against a polynomial-generated string:
  `KALMAR{M15S_TH3_S1GN5_4ND_3NTER_TH3_M4Z3}`
- It then hashes raw-input segments with FNV-1, giving unique case choices:
  `M15S`, `Th3`, `S1gN5`, `4Nd`, `3NteR`, `tH3`, `M4Z3`

4) FLAG

`kalmar{M15S_Th3_S1gN5_4Nd_3NteR_tH3_M4Z3}`

5) Writeup

The executable hides its real checker behind a Delphi GUI event handler, then a self-decrypting x86 stub, then a `Heaven's Gate` jump into x86-64 code. Once decrypted, the second stage reveals the uppercase flag structure directly and uses FNV-1 on the inner segments to pin down the exact letter casing, yielding the final flag above.
