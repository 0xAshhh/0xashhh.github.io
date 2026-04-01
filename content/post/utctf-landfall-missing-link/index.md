---
title: "UTCTF 2026: Landfall Missing Link"
description: "Writeup for Landfall Missing Link from UTCTF 2026. Challenge weight: 960 points."
slug: utctf-landfall-missing-link
date: 2026-03-13 03:22:45.383+0000
competition: "UTCTF 2026"
categories:
    - Forensics
tags:
    - writeup
    - utctf-2026
    - landfall-missing-link
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Landfall Missing Link`
- Category: `Forensics`
- Points: `960`


## Solve Path

1) Category detection
- Detected category: `misc/forensics`
- Confidence: high
- Evidence: Windows triage artifacts including `Amcache.hve`, `$MFT`, `$J`, LNKs, browser history, and encrypted checkpoint ZIPs.

2) Attack strategy
- Primary hypothesis: Checkpoint B wanted the exact SHA1 recorded for the suspicious executable in Amcache, and the ZIP password was case-sensitive.
- Validation tests: parse Amcache with the bundled EZTools, correlate the candidate with `$J` creation events, then test the exact lowercase SHA1 against `checkpointB.zip`.

3) Execution steps
- Parsed `Amcache unassociated entries` and found:
  ``2ga2pl/calc.exe``
  SHA1: `67198a3ca72c49fb263f4a9749b4b79c50510155`
- Correlated it with `USN output`, which shows `Calc.exe` being created on `2026-03-12 03:39:07`.
- Tested `checkpointB.zip` with that exact lowercase hash; it succeeded.
- Extracted `B.txt`: `m1551n6_l1nk`
- Combined with `A.txt`: `pr1v473_3y3`

4) FLAG
- `utflag{pr1v473_3y3-m1551n6_l1nk}`

5) Writeup
- Checkpoint B was the dropped `Calc.exe` from `ithqsu.zip`, not `gkape.exe`, `Calculator.exe`, or `notepad.exe`.
- The decisive detail was the parsed Amcache `SHA1` field, and the ZIP password had to be the lowercase hex string exactly: `67198a3ca72c49fb263f4a9749b4b79c50510155`.
