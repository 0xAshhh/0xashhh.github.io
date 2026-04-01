---
title: "UTCTF 2026: Cold Workspace"
description: "Writeup for Cold Workspace from UTCTF 2026. Challenge weight: 981 points."
slug: utctf-cold-workspace
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Forensics
tags:
    - writeup
    - utctf-2026
    - cold-workspace
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Cold Workspace`
- Category: `Forensics`
- Points: `981`


## Solve Path

1) Category detection

- Detected category: `misc` (memory forensics / artifact recovery)
- Confidence: high
- Evidence: `cold-workspace.dmp` is a synthetic Windows dump (`PAGEDU64`, `ColdWorkspaceSyntheticDump`) containing process/env strings, desktop file paths, and an embedded PowerShell encryption workflow.

2) Attack strategy

- Primary hypothesis: the deleted desktop artifact was `flag.jpg`, and the dump preserved enough runtime state to recover its encrypted contents and decryption material.
- Why it is minimal: the dump already exposes:
  ``Desktop/flag.jpg``
  a PowerShell script outline with `ENCD`, `ENCK`, `ENCV`
  a preserved environment block for `powershell.exe`
- Planned validation tests:
  1. Extract the `ENCD`/`ENCK`/`ENCV` values from the dump.
  2. Decrypt `ENCD` with the recovered key/IV.
  3. Check whether the plaintext is a real desktop artifact and whether it contains the flag.

3) Execution steps

- String triage exposed the deleted file and encryption path:
  `ReadAllBytes('`Desktop/flag.jpg`')`
  `Remove-Item `Desktop/flag.jpg``
  `Set-Content `Desktop/flag.enc` $env:ENCD`
- The same dump also preserved the real env block:
  `ENCD=S4wX8ml7/f9C2ffc8vENqtWw8Bko1RAhCwLLG4vvjeT2iJ26nfeMzWEyx/HlK1KmOhIrSMoWtmgu2OKMtTtUXddZDQ87FTEXIqghzCL6ErnC1+GwpSfzCDr9woKXj5IzcU2C/Ft5u705bY3b6/Z/Q/N6MPLXV55pLzIDnO1nvtja123WWwH54O4mnyWNspt5`
  `ENCK=Ddf4BCsshqFHJxXPr5X6MLPOGtITAmXK3drAqeZoFBU=`
  `ENCV=xXpGwuoqihg/QHFTM2yMxA==`
- Repro decryption:
```powershell
@'
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

encd = "S4wX8ml7/f9C2ffc8vENqtWw8Bko1RAhCwLLG4vvjeT2iJ26nfeMzWEyx/HlK1KmOhIrSMoWtmgu2OKMtTtUXddZDQ87FTEXIqghzCL6ErnC1+GwpSfzCDr9woKXj5IzcU2C/Ft5u705bY3b6/Z/Q/N6MPLXV55pLzIDnO1nvtja123WWwH54O4mnyWNspt5"
enck = "Ddf4BCsshqFHJxXPr5X6MLPOGtITAmXK3drAqeZoFBU="
encv = "xXpGwuoqihg/QHFTM2yMxA=="

pt = AES.new(base64.b64decode(enck), AES.MODE_CBC, base64.b64decode(encv)).decrypt(base64.b64decode(encd))
pt = unpad(pt, 16)
print(pt[:96])
'@ | python -
```
- Key output:
  plaintext begins with a valid JPEG/JFIF header:
  `ff d8 ff e0 00 10 4a 46 49 46 ...`
- The recovered bytes then contain:
  `Recovered desktop image bytes...`
  `FLAG:utflag{m3m0ry_r3t41ns_wh4t_d1sk_l053s}`

4) FLAG

utflag{m3m0ry_r3t41ns_wh4t_d1sk_l053s}

5) Writeup

The dump is not a full raw memory image; it is a compact synthetic artifact containing process command lines, MFT-style path references, a PowerShell encryption script fragment, and a preserved environment block. That fragment identifies the missing desktop artifact as `flag.jpg` and shows that its encrypted form was stored in `ENCD`, with the AES key and IV in `ENCK` and `ENCV`.

Extracting those three values from the dump and decrypting `ENCD` as AES-CBC with the recovered 32-byte key and 16-byte IV yields valid JFIF bytes. The recovered JPEG payload is tiny and includes plain embedded text, which directly reveals the flag: `utflag{m3m0ry_r3t41ns_wh4t_d1sk_l053s}`.
