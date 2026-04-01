---
title: "TexSAW 2026: SIGBOVIK I"
description: "Reconstructed Codex writeup for SIGBOVIK I from TexSAW 2026. Original prompt weight: 371 points."
slug: texsaw-sigbovik-i
date: 2026-03-28 07:48:34.175+0000
categories:
    - Binary Exploitation
tags:
    - codex-archive
    - texsaw-2026
    - sigbovik-i
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `SIGBOVIK I`
- Category: `Binary Exploitation`
- Points: `371`
- Original target(s): [https://www.charles.systems/publications/SCROP.pdf](https://www.charles.systems/publications/SCROP.pdf)

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge SIGBOVIK I Written by charles nc 143.198.163.4 1900 Flag format: texsaw{example_flag}


## Solve Path

`texsaw{ezpzlmnsqzy_didyoulikethepaper?_23948102938409}`

The exploit was a raw threaded-bytecode payload against the interpreter, not the compiler front-end. I validated it locally and then sent the 352-byte payload directly to `143.198.163.4:1900`.
