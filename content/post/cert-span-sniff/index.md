---
title: "CERT: SPAN sniff"
description: "Writeup for SPAN sniff from CERT."
slug: cert-span-sniff
date: 2026-03-01 14:13:35.978+0000
competition: "CERT"
categories:
    - Forensics
tags:
    - writeup
    - cert
    - span-sniff
---

## Challenge

- Competition: `CERT`
- Challenge: `SPAN sniff`
- Category: `Forensics`


## Solve Path

1) Category detection  
- `misc / network forensics (covert channel in HTTP metadata)`  
- Confidence: high. Evidence from ``network (1).pcap``.pcap): 296 HTTP requests on `192.168.1.69 -> 10.10.10.10:8080` with paired pattern `HTTP/1.0 (no Host)` vs `HTTP/1.1 (Host present)`.

2) Attack strategy  
- Hypothesis: each request encodes 1 bit using HTTP version/Host-header presence.  
- Validation: decode request stream in chronological order, pack 8 bits/byte, check for readable flag format.

3) Execution steps  
- Extracted the 296 requests from `192.168.1.69 -> 10.10.10.10:8080`.  
- For each request: bit = `1` if `HTTP/1.1` and `Host:` exists, else `0`.  
- Packed bits MSB-first per byte.  
- Decoded bytes: `SK-CERT{h1DD3n_1n_pl41n7eX7_n37Fl0w}\n`.

4) FLAG  
SK-CERT{h1DD3n_1n_pl41n7eX7_n37Fl0w}

5) Writeup  
- The JSON/session fields are decoy noise.  
- The real exfil channel is plaintext request metadata (`HTTP/1.0` vs `HTTP/1.1` + `Host`).  
- Decoding that bitstream yields the flag directly.
