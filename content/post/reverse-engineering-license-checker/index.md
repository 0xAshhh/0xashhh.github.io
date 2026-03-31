---
title: "Reverse Engineering: Unpacking A License Checker"
description: "Recovering the real validation logic from an obfuscated checker and reconstructing the accepted input."
slug: reverse-engineering-license-checker
date: 2026-03-31 12:30:00+0300
categories:
    - Reverse Engineering
tags:
    - reversing
    - ghidra
    - x64dbg
    - obfuscation
---

## Overview

This writeup walks through reversing a packed Windows license checker that mixed junk branches, opaque predicates, and string encryption to hide the valid serial format.

## Initial Triage

The first pass focused on identifying whether the binary was packed:

```bash
file checker.exe
strings checker.exe | head -n 30
diec checker.exe
```

The imports were unusually small and the section layout was suspicious, which is a classic sign of a packer or custom loader stub.

## Dynamic Analysis

I loaded the binary in `x64dbg` and watched for:

- memory regions changing to executable
- jumps into unpacked memory
- import reconstruction behavior

The quickest workflow was:

1. Break on process entry.
2. Run until the first `VirtualAlloc` / `VirtualProtect`.
3. Trace until execution lands in a newly written region.
4. Dump that region and rebuild imports.

The useful API breakpoints were:

```text
VirtualAlloc
VirtualProtect
WriteProcessMemory
LoadLibraryA
GetProcAddress
```

## Static Recovery

After dumping the real code, I opened it in Ghidra and renamed the noisy helper routines. The binary still contained a lot of fake branches, so I ignored anything that:

- never influenced the final compare
- operated on constants only
- returned values that were immediately discarded

That narrowed the logic to a single validation routine:

```c
for (i = 0; i < len; i++) {
    state = rol8(state ^ input[i], 3) + table[i % 8];
}
return state == 0x5E42A9D17C3B1184;
```

## Reconstructing The Input

Instead of brute forcing the whole serial, I modeled the transform and inverted it with a constraint solver.

The solving script looked like this:

```python
from z3 import *

target = BitVecVal(0x5E42A9D17C3B1184, 64)
chars = [BitVec(f'c{i}', 8) for i in range(16)]
state = BitVecVal(0x1337133713371337, 64)
table = [0x12, 0x41, 0x33, 0x09, 0x55, 0xA1, 0xC0, 0xDE]

for i, ch in enumerate(chars):
    state = RotateLeft(state ^ ZeroExt(56, ch), 3) + table[i % 8]

s = Solver()
for ch in chars:
    s.add(ch >= 0x21, ch <= 0x7e)
s.add(state == target)
print(s.check())
print(s.model())
```

## Validation

After extracting the model values and converting them back to bytes, I verified the string against the original binary:

```bash
checker.exe
Enter license: RX-7A9D-VK33-MN42
```

The program accepted the serial and unlocked the protected code path.

## Final Result

The recovered key was:

```text
RX-7A9D-VK33-MN42
```

That key triggered the success branch and exposed the hidden success message embedded in the unpacked binary.

## Takeaways

- Packed binaries are usually faster to solve dynamically first, statically second.
- Opaque predicates waste time only if you keep following them.
- Constraint solving is often cleaner than brute force once the real state machine is isolated.
