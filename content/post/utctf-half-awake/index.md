---
title: "UTCTF 2026: Half Awake"
description: "Writeup for Half Awake from UTCTF 2026. Challenge weight: 981 points."
slug: utctf-half-awake
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Forensics
tags:
    - writeup
    - utctf-2026
    - half-awake
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Half Awake`
- Category: `Forensics`
- Points: `981`


## Solve Path

1) Category detection

- Detected category: `misc`
- Confidence: high
- Evidence: `half-awake.pcap` is a tiny packet capture with fake TLS-looking TCP blobs, mDNS hint traffic, and an embedded file signature.

2) Attack strategy

- Primary hypothesis: one of the fake HTTPS/TLS records hides a file, and the mDNS traffic provides the decode key.
- Why it is minimal:
  `instructions.hello` explicitly says:
  `mDNS names are hints`
  `Not every 'TCP blob' is really what it pretends to be`
  `If you find a payload that starts with PK, treat it as a file`
- Planned validation tests:
  1. Inspect raw TCP payloads on port 443 for non-TLS content.
  2. Carve any payload beginning with `PK`.
  3. Read extracted files and use the mDNS TXT answer `00b7` as the decode key.

3) Execution steps

- Packet 6 gives the solve instructions over HTTP:
  `mDNS names are hints: alert.chunk, chef.decode, key.version`
- Packet 11 answers `key.version.local` with TXT:
  `00b7`
- Packets 30/32/34/36 are fake TLS-looking records. Packet 36 starts with a TLS alert header:
  `15 03 03 01 32`
  and then immediately contains ZIP magic:
  `50 4b 03 04`
- Carving off the first 5 bytes of packet 36 yields a ZIP archive containing:
  `stage2.bin`
  `readme.txt`
- `readme.txt` says:
  `not everything here is encrypted the same way`
- Decoding `stage2.bin` with repeating XOR key bytes `00 b7` gives the flag.

Repro command:
```powershell
@'
from scapy.all import rdpcap, Raw
from zipfile import ZipFile
from io import BytesIO

pkts = rdpcap(r'`Downloads/half-awake.pcap`')
zip_bytes = bytes(pkts[35][Raw].load)[5:]   # strip fake TLS alert header
zf = ZipFile(BytesIO(zip_bytes))
stage2 = zf.read('stage2.bin')

key = [0x00, 0xb7]
pt = bytes(b ^ key[i % 2] for i, b in enumerate(stage2))
print(pt.decode())
'@ | python -
```

Key output:
```text
utflag{h4lf_aw4k3_s33_th3_pr0t0c0l_tr1ck}
```

4) FLAG

`utflag{h4lf_aw4k3_s33_th3_pr0t0c0l_tr1ck}`

5) Writeup

The capture mixes normal-looking traffic with several TCP streams on port 443 that only mimic TLS by prepending record-like headers. The HTTP instructions point directly at the solve path: use mDNS as hints and treat any payload beginning with `PK` as a file. The decisive packet is the last fake TLS alert record, which contains a ZIP archive after the first 5 bytes.

Inside the ZIP, `readme.txt` warns that the content is encoded differently. The mDNS TXT response for `key.version.local` is `00b7`, which works as a two-byte repeating XOR key. Applying `00 b7 00 b7 ...` to `stage2.bin` cleanly recovers the flag `utflag{h4lf_aw4k3_s33_th3_pr0t0c0l_tr1ck}`.
