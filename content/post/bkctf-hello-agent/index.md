---
title: "BKCTF: Hello Agent"
description: "Writeup for Hello Agent from BKCTF."
slug: bkctf-hello-agent
date: 2026-03-06 21:35:05.738+0000
competition: "BKCTF"
categories:
    - OSINT
tags:
    - writeup
    - bkctf
    - hello-agent
---

## Challenge

- Competition: `BKCTF`
- Challenge: `Hello Agent`
- Category: `OSINT`


## Solve Path

1) Category detection  
- Detected category: `OSINT + stego/misc` (confidence: high).  
- Evidence: clue explicitly references Bluesky (`blue sky`) + handle clue (`ends with nmos`) + image artifact with hidden appended binary stream.

2) Attack strategy  
- Primary hypothesis: the cat image has an intentional hidden payload, and `inmos`/Bluesky clues provide decryption context.  
- Validation tests used: PNG structural forensics, chunk reconstruction, metadata extraction, Bluesky actor/repo/blob pivots, and multi-algorithm decode attempts.

3) Execution steps  
- Confirmed hidden appended payload in [cat_attachment.png](/mnt/c/Users/anas/cat_attachment.png): PNG ends at offset `292527`, with `82254` extra bytes in [cat_attachment_extra.bin](/mnt/c/Users/anas/cat_attachment_extra.bin).  
- Reconstructed valid chunk stream from trailer into [extra_tail_as_png.png](/mnt/c/Users/anas/extra_tail_as_png.png): chunk CRCs valid, but image data is intentionally obfuscated (`BadZlibHeader`).  
- Extracted and analyzed `inmos*` Bluesky repos, follows, records, avatars, and blobs (including [inmos-obvi_blob.png](/mnt/c/Users/anas/inmos-obvi_blob.png), [inmos_blob.jpg](/mnt/c/Users/anas/inmos_blob.jpg), [inmosky_blob.jpg](/mnt/c/Users/anas/inmosky_blob.jpg)).  
- Verified no direct flag text in visible posts/records/profile metadata for `inmos`, `inmosky`, `inmos-obvi`, and related pivots.  
- Ran broad decode/crypto passes (XOR/add/sub, RC4, AES modes, Salsa20, ChaCha20, transform stacks, bitplane/channel/stego checks, dictionary and clue-derived keyspace). No reproducible flag extraction path succeeded.  
- Notable side finding: unrelated local binary [supercool](/mnt/c/Users/anas/supercool) contains `bkctf{sup3rv3ryt074llyc00l}`, but this does not match evidence chain for your cat/Bluesky mission, so I did not treat it as mission flag.

4) FLAG  
- `FLAG: not recovered`

5) Writeup  
- The strongest confirmed fact is that the cat image contains a deliberate secondary hidden container (`extra` trailer), not just normal metadata.  
- The `inmos` Bluesky pivot is real and reproducible, but public repo data did not expose a direct flag or matching cat artifact.  
- Current blocker is the decryption/decoding step for the obfuscated trailer payload.  
- Fastest next pivot: one additional challenge-side constraint (expected flag format/prefix, or one extra hint from challenge page) to collapse keyspace and finish extraction.
