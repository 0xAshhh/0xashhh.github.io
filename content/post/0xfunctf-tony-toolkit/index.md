---
title: "0xFunCTF: Tony Toolkit"
description: "Writeup for Tony Toolkit from 0xFunCTF. Challenge weight: 500 points."
slug: 0xfunctf-tony-toolkit
date: 2026-02-12 18:14:20.900+0000
competition: "0xFunCTF"
categories:
    - Web Exploitation
tags:
    - writeup
    - 0xfunctf
    - tony-toolkit
---

## Challenge

- Competition: `0xFunCTF`
- Challenge: `Tony Toolkit`
- Category: `Web Exploitation`
- Points: `500`
- Original target(s): [http://chall.0xfun.org:11588](http://chall.0xfun.org:11588)


## Solve Path

**Flag**
- `0xfun{T0ny'5_T00ly4rd._1_H0p3_Y0u_H4d_Fun_SQL1ng,_H45H_Cr4ck1ng,_4nd_W1th_C00k13_M4n1pu74t10n}`  
  (raw HTML shows `&#39;` instead of `'`)

**Quick solve path**
- `GET /robots.txt` leaks `/main.pyi`.
- `main.pyi` shows broken auth in `is_logged_in()` (it never checks cookie value; it always returns `True` when users exist).
- `/user` only needs a `userID` cookie, so admin profile is readable with:
- `curl.exe -s http://chall.0xfun.org:11588/user -H "Cookie: userID=1"`  

Want a short write-up payload list you can submit?
