---
title: "TexSAW 2026: drawing"
description: "Writeup for drawing from TexSAW 2026. Challenge weight: 379 points."
slug: texsaw-drawing
date: 2026-03-27 19:33:54.127+0000
competition: "TexSAW 2026"
categories:
    - Reverse Engineering
tags:
    - writeup
    - texsaw-2026
    - drawing
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `drawing`
- Category: `Reverse Engineering`
- Points: `379`


## Solve Path

`texsaw{VVhYd_U_M4k3_mE_s0_4n6ry}`

The real path was bucket `714`: it’s the only checker that actually consumes all 32 bytes. Inverting its four base-131 accumulators gives that exact string, and running the ELF with it prints the same success line.
