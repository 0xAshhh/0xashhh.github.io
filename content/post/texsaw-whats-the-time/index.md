---
title: "TexSAW 2026: What's the Time?"
description: "Reconstructed Codex writeup for What's the Time? from TexSAW 2026. Original prompt weight: 331 points."
slug: texsaw-whats-the-time
date: 2026-03-27 19:46:53.061+0000
categories:
    - Binary Exploitation
tags:
    - codex-archive
    - texsaw-2026
    - what's-the-time?
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `What's the Time?`
- Category: `Binary Exploitation`
- Points: `331`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Whats the Time? Written by kaber I think one of the hands of my watch broke. Can you tell me what the time is? nc 143.198.163.4 3000 Flag format: texsaw{flag} ex: texsaw{flag}


## Solve Path

1) Category detection

- Detected category: `pwn`
- Confidence: high
- Evidence: 32-bit ELF, no PIE/canary, imported `system`, and `read_user_input()` does `memcpy(stack_buf, user_buf, len)` into a local buffer at `[ebp-0x40]`.

2) Attack strategy

- First leak the XOR key by sending 40 null bytes. The program echoes the transformed bytes, which directly reveals the current minute-based key stream.
- Then reconnect within the same minute and send an XOR-encoded ret2libc payload: padding to EIP, then `system@plt`, a dummy return, and the `"/bin/sh"` string address.
- `win()` is a decoy. It prints `/bin/sh` but actually calls `system("ls")`.

3) Execution steps

- Important addresses:
  - `system@plt = 0x080490b0`
  - `"/bin/sh" = 0x0804a018`
  - EIP offset = `68`
- Remote leak used:
  - displayed time: `Fri Mar 27 19:56:00 2026`
  - leaked key: `0x69c6e0d0`
- Plain payload:
```python
b"A"*68 + p32(0x080490b0) + p32(0x0804935f) + p32(0x0804a018)
```
- After XOR-encoding that payload with the per-4-byte incrementing key and sending it, `cat flag.txt` returned the flag.

4) FLAG

`texsaw{7h4nk_u_f0r_y0ur_71m3}`

5) Writeup

- The binary rounds `time(NULL)` down to the current minute and uses that integer as an XOR key over input in 4-byte chunks, incrementing the key each chunk.
- `read_user_input()` then copies up to `0xa0` bytes into a stack buffer, so the return address is controllable.
- One connection leaks the exact key for that minute; the next connection uses it to encode a ret2libc chain into `system("/bin/sh")`.
- From the spawned shell, `flag.txt` contains the flag.
