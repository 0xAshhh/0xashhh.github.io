---
title: "UTCTF 2026: Oblivious Error"
description: "Writeup for Oblivious Error from UTCTF 2026. Challenge weight: 994 points."
slug: utctf-oblivious-error
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Cryptography
tags:
    - writeup
    - utctf-2026
    - oblivious-error
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Oblivious Error`
- Category: `Cryptography`
- Points: `994`


## Solve Path

RSA detected. Beginning prime autopsy.

**Attack Plan**
- Inspect the bug in `my-code.txt`: `k ^ e` is bitwise XOR, not RSA exponentiation.
- Use that bug to force `v = x1` by sending `k = e ^ ((x1 - x0) mod N)`.
- When `v = x1`, the sender computes the `x1` branch pad as `0`, so that branch’s message is returned in the clear.
- Read the cleartext-bearing message and strip the trailing newline.

**Execution**
- Values extracted: the service gives `N`, `e`, `x0`, `x1`; the buggy client line is `v = (x0 + (int(k) ^ e)) % N`.
- Chosen attack: set `k = e ^ ((x1 - x0) % N)` so `v = x0 + ((k ^ e)) = x0 + (x1 - x0) = x1 (mod N)`.
- Code snippet (Python):
```python
import socket, re
from Crypto.Util.number import long_to_bytes

s = socket.create_connection(("challenge.utctf.live", 8379), timeout=10)
data = b""
while b"Please pick a value k." not in data:
    data += s.recv(4096)

text = data.decode()
N  = int(re.search(r"N = (\d+)", text).group(1))
e  = int(re.search(r"e = (\d+)", text).group(1))
x0 = int(re.search(r"x0: (\d+)", text).group(1))
x1 = int(re.search(r"x1: (\d+)", text).group(1))

k = e ^ ((x1 - x0) % N)
s.sendall(f"{k}\n".encode())

out = b""
while True:
    chunk = s.recv(4096)
    if not chunk:
        break
    out += chunk

m1 = int(re.search(rb"Message 1:\s*(\d+)", out).group(1))
m2 = int(re.search(rb"Message 2:\s*(\d+)", out).group(1))
print(long_to_bytes(m1))
print(long_to_bytes(m2))
```
- Key intermediate results: on a clean run, one message decoded directly to `b'utflag{my_obl1v10u5_fr13nd_ru1n3d_my_c0de}\n'`.

**Flag Extraction**
- Conversion method: integer output -> bytes with `long_to_bytes(...)`, then strip `\n`.
- Final flag: `utflag{my_obl1v10u5_fr13nd_ru1n3d_my_c0de}`

**Writeup (clean & structured)**
- Problem statement: the RSA OT client code was corrupted, and one branch became “undecodable.”
- Observations: the bug is not just using `x0`; it also uses `^`, which in Python is XOR, not exponentiation. That gives direct algebraic control over `v`.
- Attack reasoning: because `v = x0 + (k ^ e) mod N`, choosing `k = e ^ t` makes `v = x0 + t mod N`. Setting `t = x1 - x0 mod N` forces `v = x1`, which makes the server’s recovered pad for the `x1` branch equal to `0`.
- Steps: connect, parse `N/e/x0/x1`, compute `k`, send it, convert the returned integers to bytes, and read the cleartext branch.
- Final result: `utflag{my_obl1v10u5_fr13nd_ru1n3d_my_c0de}`
