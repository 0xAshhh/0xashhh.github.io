---
title: "SUCTF 2026: SU_Chronos_Ring"
description: "Reconstructed Codex writeup for SU_Chronos_Ring from SUCTF 2026."
slug: suctf-su-chronos-ring
date: 2026-03-14 14:42:01.132+0000
categories:
    - Binary Exploitation
tags:
    - codex-archive
    - suctf-2026
    - su-chronos-ring
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_Chronos_Ring`
- Category: `Binary Exploitation`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: SU_Chronos_Ring 416PT Pwn a y no , pwn it plz nc 101.245.64.169 10000 (Please attack the target machine after the local EXP is successfully utilized


## Solve Path

FLAG:
SUCTF{VGhhc19BU19XSEFUX1Vfd0FudF9mbGFnX2ZsYWdfZmxhZyEhIQ==}

WRITEUP:
1) Given
- Files: `bzImage`, `chronos_ring.ko`, `initramfs.cpio.gz`, boot scripts, remote `101.245.64.169:10000`
- Remote: `nc 101.245.64.169 10000`
- Observations: init runs a root loop executing `/bin/sh /tmp/job` every 3 seconds and exposes `/dev/chronos_ring`

2) Recon
- Module surface: `chronos_ioctl` and `chronos_mmap`
- Key ioctl cmds: `0x1001` alloc, `0x1002` auth, `0x1003` pin page, `0x1004` attach file page, `0x1005` create view, `0x1007` write buffer, `0x1008` sync buffer to view, `0x1009` info
- File gate: `0x1004` hashes basename `job`, which matches `/tmp/job`

3) Vulnerability
- Type: logic bug / privileged file-page write
- Root cause: after auth, the module lets an unprivileged user bind a page-cache page for `/tmp/job`, create a file-backed view, and copy attacker-controlled data into that page while marking it dirty
- Control primitive: arbitrary overwrite of `/tmp/job` contents without write permission

4) Exploit Plan
- Use `0x1001` to allocate the buffer
- Use `0x1007` to stage a short shell payload: `#!/bin/sh\ncat /flag>/home/ctf/f #`
- Brute-force the auth bucket with `0x1002` and detect success via `0x1009`
- Use `0x1003` to satisfy the pinned-page requirement
- Use `0x1004` on `/tmp/job`, then `0x1005`, then `0x1008` to mirror the payload into the page cache
- Wait for the root helper to execute `/tmp/job`, then read `/home/ctf/f`

5) Exploit (pwntools)
- I implemented this as a guest-side Linux exploit plus a host-side uploader/runner:
- Guest exploit: `guest_exploit.c`
- Host runner: `solve_remote.py`

6) Proof
- Remote run succeeded end-to-end and printed:
- `FLAG: SUCTF{VGhhc19BU19XSEFUX1Vfd0FudF9mbGFnX2ZsYWdfZmxhZyEhIQ==}`

Submit the literal flag above, not the Base64-decoded text.
