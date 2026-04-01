---
title: "TexSAW 2026: Broken Quest"
description: "Writeup for Broken Quest from TexSAW 2026. Challenge weight: 464 points."
slug: texsaw-broken-quest
date: 2026-03-27 18:13:22.865+0000
competition: "TexSAW 2026"
categories:
    - Reverse Engineering
tags:
    - writeup
    - texsaw-2026
    - broken-quest
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `Broken Quest`
- Category: `Reverse Engineering`
- Points: `464`


## Solve Path

1) Category detection
- `rev/pwn` hybrid, high confidence. The file is a 64-bit PIE ELF with symbols, and `turn_in` just `memcmp`s the quest state against a fixed 8-int target before calling the reward routine.

2) Attack strategy
- Minimal hypothesis: if the live quest state equals the hardcoded target, the binary will print the flag.
- Validation: patch the stack state under `gdb`, choose action `0`, and confirm the printed reward.
- Cross-check: reimplement `handle_flag` statically from the extracted tables and verify it yields the same string.

3) Execution steps
- Recovered the required state from `main`/`turn_in`: `[2, 6, -4, 6, 0, 4, -3, 1]`.
- Patched that state into the running process just before the menu loop and continued with input `0`.
- The binary printed `Here's your reward: texsaw{1t_ju5t_work5_m0r3_l1k3_!t_d0e5nt_w0rk}`.
- Replayed `handle_flag` offline from the embedded 8x8 opcode table and 46-byte secret; it produced the same flag.

4) FLAG
`texsaw{1t_ju5t_work5_m0r3_l1k3_!t_d0e5nt_w0rk}`

5) Writeup
- The “quest” is gated by a hardcoded state check, not by dynamic validation of an intended puzzle path.
- That gives two practical solve routes: patch the state at runtime, or emulate the flag transform directly.
- I did not recover a pure menu-input sequence; both proof paths above independently confirm the flag.
