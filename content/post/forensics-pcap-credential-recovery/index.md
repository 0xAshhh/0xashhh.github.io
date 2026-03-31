---
title: "Forensics: Recovering Credentials From A PCAP"
description: "Extracting a compromise timeline from packet captures and rebuilding the attacker’s access path."
slug: forensics-pcap-credential-recovery
date: 2026-03-31 13:00:00+0300
categories:
    - Forensics
tags:
    - pcap
    - wireshark
    - tshark
    - incident-response
---

## Overview

This case started with a packet capture and a simple goal: determine how the attacker authenticated and what they accessed afterward.

## Scope

The capture contained mixed traffic:

- DNS
- HTTP
- SMB
- a small amount of SSH

The fastest path was to build a timeline first and only drill down into flows that carried credentials or session material.

## First Pass

I began with protocol statistics and stream enumeration:

```bash
tshark -r incident.pcap -q -z io,phs
tshark -r incident.pcap -q -z conv,tcp
tshark -r incident.pcap -Y "http.request or http.response" -T fields -e frame.number -e ip.src -e ip.dst -e http.host -e http.request.uri
```

This immediately highlighted repeated requests to the same internal web application.

## Credential Recovery

The suspicious authentication flow used HTTP POST and transmitted parameters in cleartext.

I isolated the login requests with:

```bash
tshark -r incident.pcap \
  -Y 'http.request.method == "POST"' \
  -T fields \
  -e frame.number \
  -e ip.src \
  -e http.host \
  -e http.request.uri \
  -e http.file_data
```

One request exposed:

```text
username=analyst&password=Winter2026!
```

## Session Tracking

With the credentials identified, the next step was tracing the session cookie issued by the application:

```bash
tshark -r incident.pcap \
  -Y 'http.set_cookie or http.cookie' \
  -T fields \
  -e frame.number \
  -e http.set_cookie \
  -e http.cookie
```

That showed the authenticated cookie being reused for requests to `/admin/export`, which confirmed post-login access rather than a failed brute-force attempt.

## Timeline Reconstruction

I mapped the sequence into a compact incident chain:

1. Internal host resolves the application domain.
2. User submits credentials over HTTP.
3. Server returns a session cookie.
4. Same cookie accesses privileged administrative endpoints.
5. Data export follows minutes later.

The supporting frame review in Wireshark made the operator behavior obvious.

## Commands Used For Verification

To validate the credential and export path, I reassembled the TCP streams:

```bash
tshark -r incident.pcap -q -z follow,tcp,ascii,7
tshark -r incident.pcap -q -z follow,tcp,ascii,9
```

Those streams confirmed both the login request and the admin export response body.

## Final Result

The core finding was:

- Initial credential used: `analyst / Winter2026!`
- Access method: insecure HTTP form login
- Evidence of successful authenticated access: session cookie reuse against admin endpoints

## Takeaways

- PCAP work gets faster once you pivot from “all traffic” to “credential-bearing flows”.
- `tshark` is ideal for narrowing the search before opening specific frames in Wireshark.
- Cleartext authentication is still one of the easiest compromise paths to prove from network evidence.
