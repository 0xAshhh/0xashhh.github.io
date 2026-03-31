---
title: "BSidesSF 2019: slowfire"
description: "A networked stack overflow where injected shellcode opens the flag file, reads it, and sends it back over the live socket."
slug: bsidessf-2019-slowfire
date: 2026-03-31 07:00:00+0300
categories:
    - Binary Exploitation
tags:
    - bsidessf
    - pwn
    - stack-overflow
    - shellcode
    - socket
---

## Competition

- Competition: [BSidesSF 2019](https://ctftime.org/event/753)
- Challenge: [slowfire](https://ctftime.org/event/753/tasks/)
- Category: Pwn / Binary Exploitation

## Question

The local challenge note reduces the task to this:

> Exploit the stack overflow in the service, redirect execution to shellcode stored in memory, and send the flag back over the socket.

## Flag

`CTF{cOnGrAtZ_oN_t3h_FlAg}`

## Service Review

The program runs a TCP service on port `4141`, accepts a client, asks for a name, then asks for a message.

Two program details matter immediately:

1. The global `name[64]` buffer is writable and stable in `.bss`.
2. The `msg[1024]` buffer sits on the stack inside `handle_client`.

The service flow is:

```c
read_line_safe(fd, name, 64);
read_line_safe(fd, msg, 0x400);
invert_case(msg);
write_string(fd, name);
write_string(fd, msg);
```

The exploit uses the name field to store shellcode and the message field to smash the saved return address.

## Core Idea

Instead of spawning an interactive shell, the solve uses shellcode that:

1. opens `flag.txt`
2. reads its contents into a buffer
3. writes that buffer back to the connected socket

This approach is cleaner for a forked network daemon because we only need one successful exfiltration.

## Key Commands

Local setup and triage:

```bash
checksec ./program
file ./program
```

Run the solver:

```bash
python exploit.py
```

Relevant addresses from the solve:

```text
name (.bss)    = 0x4040c0
read buffer    = 0x404200
write@plt-ish  = 0x401040
read helper    = 0x401080
```

## Shellcode Layout

The provided assembly does not call `/bin/sh`. It performs direct file exfiltration:

```asm
open("flag.txt", O_RDONLY)
read(fd, 0x404200, 0x64)
write(socket_fd, 0x404200, 0x64)
```

The socket file descriptor is recovered from the current stack frame with:

```asm
mov edi, [rsp - 0x444]
```

That allows the shellcode to reuse the already connected client socket without guessing file descriptors.

## Overflow Path

The final payload is split in two stages:

1. Send `flag.txt` plus shellcode in the `name` input.
2. Overflow `msg` and replace the saved return address with the address of the shellcode in `.bss`.

The control-hijack portion is effectively:

```python
'c' * 72 +
'd' * 8 +
p64(0x4040c0 + len(flag_filename) + 1)
```

That value points directly to the shellcode placed after the null-terminated `flag.txt` string inside the global `name` buffer.

## Why It Works

`invert_case(msg)` only mutates alphabetic bytes inside the message buffer. The actual shellcode lives in `name`, so it is not damaged before execution.

Once the overwritten return address is hit, execution jumps into attacker-controlled bytes in `.bss`, the shellcode opens the flag file, and the service writes the contents back to the client connection.

## Result

This challenge is a straightforward but clean stack overflow: place shellcode in a reliable writable region, pivot execution there, and exfiltrate the flag over the existing socket.

Final flag:

`CTF{cOnGrAtZ_oN_t3h_FlAg}`
