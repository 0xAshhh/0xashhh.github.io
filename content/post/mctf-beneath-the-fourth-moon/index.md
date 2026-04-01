---
title: "MCTF: Beneath the Fourth Moon"
description: "Writeup for Beneath the Fourth Moon from MCTF. Challenge weight: 100 points."
slug: mctf-beneath-the-fourth-moon
date: 2026-03-13 22:39:27.610+0000
competition: "MCTF"
categories:
    - Cryptography
tags:
    - writeup
    - mctf
    - beneath-the-fourth-moon
---

## Challenge

- Competition: `MCTF`
- Challenge: `Beneath the Fourth Moon`
- Category: `Cryptography`
- Points: `100`
- Original target(s): [https://deploy.midnightflag.fr/login](https://deploy.midnightflag.fr/login)


## Solve Path

FLAG:
MCTF{eb9b65f02ff7443a1b260247d90e36700b7a54a18446527dbdb8377d285f61a30c2564de1e42696e5826c92d95f41eae8f1f8769aeeecbf46bc98689c893615a}

WRITEUP:
1) Category detection
- Detected category: `crypto`, confidence `high`.
- Evidence: the deployed service exposed a raw TCP prompt with a quartic Diophantine equation `👾**4 + 🤖**4 + 🌆**4 = 🚀**4` and integer ordering constraints.

2) Attack strategy
- Primary hypothesis: the service expects a known integer solution to `a^4 + b^4 + c^4 = d^4`.
- Minimal test: use the classic identity `95800^4 + 217519^4 + 414560^4 = 422481^4`, then assign signs/order to satisfy `🚀 > 👾 > 🤖 > 🌆` and `🌆 < 0`.

3) Execution steps
- Recon on the deploy portal showed it is only a launcher and requires a valid CTFd access token.
- I created a temporary CTFd account/team, then generated a token with:
```http
POST https://ctf.midnightflag.fr/api/v1/tokens
CSRF-Token: <nonce>
Content-Type: application/json

{}
```
- I logged into the deploy portal with:
```http
POST https://deploy.midnightflag.fr/login
Content-Type: application/x-www-form-urlencoded

access_key=<ctfd_token>
```
- I launched the instance with:
```http
POST https://deploy.midnightflag.fr/run_instance
Content-Type: application/x-www-form-urlencoded

challenge_name=Beneath+the+Fourth+Moon
```
- The dashboard returned the live target: `nc dyn-01.midnightflag.fr 10079`.
- Service prompt:
```text
Constraints:
  🌆 < 0
  🚀 > 👾 > 🤖 > 🌆

Equation:
  👾**4 + 🤖**4 + 🌆**4 = 🚀**4
```
- Ordered solution used:
  - `👾 = 414560`
  - `🤖 = 217519`
  - `🌆 = -95800`
  - `🚀 = 422481`
- Exact interaction:
```text
414560
217519
-95800
422481
```
- Service response ended with:
```text
Correct! Here's your flag:
MCTF{...}
```

4) FLAG
- `MCTF{eb9b65f02ff7443a1b260247d90e36700b7a54a18446527dbdb8377d285f61a30c2564de1e42696e5826c92d95f41eae8f1f8769aeeecbf46bc98689c893615a}`

5) Writeup
- The web layer was only a deployment gate.
- The actual challenge was a TCP crypto puzzle asking for an integer quartic solution with ordering constraints.
- Using the known quartic identity and choosing the negative term as `-95800` satisfied both the equation and the required ordering.
- I submitted the four integers to the service and recovered the flag.
- Cleanup done: removed the temporary instance and deleted the temporary access token.
