---
title: "TexSAW 2026: SIGBOVIK I"
description: "Writeup for SIGBOVIK I from TexSAW 2026. Challenge weight: 371 points."
slug: texsaw-sigbovik-i
date: 2026-03-28 07:48:34.175+0000
competition: "TexSAW 2026"
categories:
    - Binary Exploitation
tags:
    - writeup
    - texsaw-2026
    - sigbovik-i
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `SIGBOVIK I`
- Category: `Binary Exploitation`
- Points: `371`
- Original target(s): [https://www.charles.systems/publications/SCROP.pdf](https://www.charles.systems/publications/SCROP.pdf)


## Solve Path

`texsaw{ezpzlmnsqzy_didyoulikethepaper?_23948102938409}`

The exploit was a raw threaded-bytecode payload against the interpreter, not the compiler front-end. I validated it locally and then sent the 352-byte payload directly to `143.198.163.4:1900`.
