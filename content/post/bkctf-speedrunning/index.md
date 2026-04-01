---
title: "BKCTF: Speedrunning"
description: "Writeup for Speedrunning from BKCTF."
slug: bkctf-speedrunning
date: 2026-02-21 09:26:28.205+0000
competition: "BKCTF"
categories:
    - Misc
tags:
    - writeup
    - bkctf
    - speedrunning
---

## Challenge

- Competition: `BKCTF`
- Challenge: `Speedrunning`
- Category: `Misc`


## Solve Path

1) Category detection
- Detected category: `misc` (high confidence).
- Evidence: artifact is a Minecraft world save (`level.dat`, `region/*.mca`, `playerdata`, screenshots), so this is world-forensics, not crypto/rev/pwn.

2) Attack strategy
- Primary hypothesis: the flag is split across in-world sign text inside chunk `block_entities`.
- Minimal validation test: parse NBT from all `.mca` files, extract `minecraft:sign` text, and look for ordered fragments (`1/4`, `2/4`, etc.).
- Pass condition: recover all numbered fragments and concatenate them in order.

3) Execution steps
- Unzipped ``Downloads/challenge.zip``.
- Parsed NBT in world data and all chunk region files with a local Python NBT/Anvil parser.
- Extracted sign fragments:
  - `region\r.-2.0.mca` at `(-569,-59,71)`: `bkctf{m1nc` with `1/4`
  - `region\r.-10.0.mca` at `(-4779,80,246)`: `3dr4ft_m4` with `2/4`
  - `DIM1\region\r.0.0.mca` at `(1,63,0)`: `nhunt_0n` with `3/4`
  - `DIM1\region\r.4.5.mca` at `(2057,148,2754)`: `3_hunt3r}` with `4/4`
- Concatenated in order `1/4 -> 4/4`:
  - `bkctf{m1nc3dr4ft_m4nhunt_0n3_hunt3r}`

4) FLAG
bkctf{m1nc3dr4ft_m4nhunt_0n3_hunt3r}

5) Writeup
- The world contains multiple sign tile entities with explicit ordered chunks of the flag.  
- By directly reading NBT `block_entities` in chunk files (not guessing from screenshots), I recovered all four parts and assembled them deterministically into the final flag.
