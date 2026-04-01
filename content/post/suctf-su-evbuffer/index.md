---
title: "SUCTF 2026: SU_evbuffer"
description: "Writeup for SU_evbuffer from SUCTF 2026."
slug: suctf-su-evbuffer
date: 2026-03-14 04:58:01.286+0000
competition: "SUCTF 2026"
categories:
    - Binary Exploitation
tags:
    - writeup
    - suctf-2026
    - su-evbuffer
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_evbuffer`
- Category: `Binary Exploitation`


## Solve Path

FLAG:
flag{80e59f78-d2a3-4e6a-bbbf-8027d25c2b9b}

WRITEUP:
1) Given
- Files: `pwn`, `libc.so.6`, `libevent-2.1.so.7.0.1`
- Remote: `101.245.104.190 tcp 10001 / udp 10011`
- Observations: TCP input seeds stack state; UDP request leaks PIE/libevent/stack and the overflow is reachable over UDP.

2) Recon
- file: 64-bit stripped PIE ELF
- checksec: Full RELRO, Canary, NX, PIE
- libc info: provided `libc.so.6`; custom `libevent-2.1.so.7.0.1`
- key symbols / functions: vuln core at `0x13a4`; `bufferevent_get_output`; `evbuffer_add_reference`; UDP handler built on `recvfrom`

3) Vulnerability
- Type: global overflow + stack leak
- Root cause: `memcpy(ctx, input, len)` copies up to `0x3ff` bytes into small `.bss` context structs, corrupting adjacent globals; `gethostname` output copies 0x40 bytes of uninitialized stack into the response
- Control primitive: leak PIE/libevent/stack, forge fake `bufferevent`/`evbuffer`, pivot through libevent callback machinery into a `.bss` ROP chain

4) Exploit Plan
- Attack branch: leak + ORW ROP under seccomp
- Mitigations & bypass: seccomp makes shell-oriented paths poor, so ORW is the right branch
- Leaks used:
  - `pie_base = leak[7] - 0x1619`
  - `libevent_base = leak[1] - 0x13b1a`
  - `peer_ptr = leak[2] - 0x3e0`
- Final primitive:
  - TCP only seeds stack
  - UDP leak gets bases
  - UDP overflow forges fake libevent objects
  - ROP does `connect(6, peer, 16) -> open("/flag") -> read(10, buf, 0x40) -> write(6, buf, 0x40)`

5) Exploit (pwntools)
- Full script: `solve.py`
- Key engineering fix: the original UDP ORW chain was too long for the `0x3ff` overwrite window. I compacted the fake layout and reused `BUF` as both pathname storage and read buffer so the full chain fits.

6) Proof
- Local validation:
```text
python3 ./solve.py LOCAL
[local harness placeholder omitted]
```
- Remote extraction:
```text
TRY 10001 10011 10 b'/flag\x00'
[*] trigger response: b'flag{80e59f78-d2a3-4e6a-bbbf-8027d25c2b9b}\n...'
FLAG flag{80e59f78-d2a3-4e6a-bbbf-8027d25c2b9b}
```
