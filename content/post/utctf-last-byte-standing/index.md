---
title: "UTCTF 2026: Last Byte Standing"
description: "Writeup for Last Byte Standing from UTCTF 2026. Challenge weight: 989 points."
slug: utctf-last-byte-standing
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Forensics
tags:
    - writeup
    - utctf-2026
    - last-byte-standing
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Last Byte Standing`
- Category: `Forensics`
- Points: `989`


## Solve Path

1) Category detection

- Detected category: `misc`
- Confidence: high
- Evidence: `last-byte-standing.pcap` is a packet capture dominated by DNS, and the only clear anomaly is a large set of DNS queries from `10.55.0.24/.31/.32` that carry an extra trailing raw byte after the DNS layer.

2) Attack strategy

- Primary hypothesis: the hidden data is in the extra final byte of the anomalous DNS query packets.
- Why it is minimal: the challenge title points at a “last byte,” and these `sync-cache*` queries are the only packets where a one-byte `Raw` tail appears consistently.
- Planned validation tests:
  1. Group anomalous DNS queries by queried hostname.
  2. Concatenate each stream’s trailing bytes.
  3. If the bytes are ASCII `0/1`, decode them as bitstrings.

3) Execution steps

- DNS triage showed three suspicious query-only streams:
  `sync-cache.nexthop-lab.net.` from `10.55.0.24` with `224` packets
  `sync-cache-alpha.nexthop-lab.net.` from `10.55.0.31` with `96` packets
  `sync-cache-beta.nexthop-lab.net.` from `10.55.0.32` with `120` packets
- Every one of those packets had exactly `1` trailing raw byte beyond the DNS query.
- Repro script:
```powershell
@'
from scapy.all import rdpcap, DNS, IP, Raw
from collections import defaultdict

pkts = rdpcap(r'`Downloads/last-byte-standing.pcap`')
chunks = defaultdict(bytearray)

for p in pkts:
    if DNS in p and p[DNS].qr == 0 and p[IP].src.startswith('10.55.0.') and Raw in p:
        chunks[p[DNS].qd.qname.decode()] += bytes(p[Raw].load)

for name, data in chunks.items():
    bits = data.decode()
    decoded = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    print(name, len(data), decoded)
'@ | python -
```
- Key output:
  `sync-cache.nexthop-lab.net. 224 b'utflag{d1g_t0_th3_l4st_byt3}'`
  `sync-cache-alpha... -> b'U\xc3U\xc3U\xc3U\xc3U\xc3U\xc3'`
  `sync-cache-beta...  -> b':V:V:V:V:V:V:VV'`
- The primary stream decodes directly to the flag. The alpha/beta streams are decoys.

4) FLAG

`utflag{d1g_t0_th3_l4st_byt3}`

5) Writeup

The missed anomaly was not in ordinary DNS answers but in the DNS queries themselves: three `sync-cache*` query streams each had one extra trailing byte after the DNS payload. Concatenating those bytes for the main `sync-cache.nexthop-lab.net.` stream produced a long ASCII bitstring beginning with `01110101 01110100...`, which decodes to `ut...`.

Converting the 224-bit main stream into bytes recovers the full flag `utflag{d1g_t0_th3_l4st_byt3}`. The `alpha` and `beta` streams decode to repetitive junk and serve as noise.
