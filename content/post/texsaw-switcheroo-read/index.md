---
title: "TexSAW 2026: Switcheroo Read"
description: "Reconstructed Codex writeup for Switcheroo Read from TexSAW 2026. Original prompt weight: 361 points."
slug: texsaw-switcheroo-read
date: 2026-03-27 19:03:04.921+0000
categories:
    - Reverse Engineering
tags:
    - codex-archive
    - texsaw-2026
    - switcheroo-read
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `Switcheroo Read`
- Category: `Reverse Engineering`
- Points: `361`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge Switcheroo Read Written by Ben Whoopsie, some wild functions started switching my string. Please determine a string to fit their confusion. Flag format: texsaw{string} ex: texsaw{confused_String}


## Solve Path

1) Category detection

`rev`, high confidence. ``Downloads/switcheroo` (2)` is a stripped 64-bit ELF that mutates a 27-byte input through several reversible byte shuffles/arithmetic checks.

2) Attack strategy

I reconstructed the transform chain statically, then modeled the checks and validated candidates by running the ELF itself under WSL with `README.txt` present.

3) Execution steps

- Identified the binary as ELF64 and lifted the mutator/check functions from disassembly.
- Recovered the hidden filename check as `README.txt`.
- Solved the staged constraints across the `5, 6, 13, 3, 24, 10, 7` transforms.
- Verified candidate inputs by piping them into the real binary; each printed `You have entered the flag`.

4) FLAG

The checker is underconstrained and accepts four valid flag strings:

- `texsaw{pAs1ence!!_V0rKn0w?}`
- `texsaw{pAt1ence!!_W0rKn0w?}`
- `texsaw{pAs1ence!!_W0rKn0w?}`
- `texsaw{pAt1ence!!_V0rKn0w?}`

5) Writeup

The non-uniqueness comes from the final checker: two equations use doubled-byte arithmetic, which leaves two possible byte values each, so `2 x 2 = 4` valid inputs survive. If the platform only accepts one canonical answer despite the local checker accepting four, try `texsaw{pAt1ence!!_W0rKn0w?}` first, but the ELF itself accepts all four.
