---
title: "BSidesSF CTF 2026: ghostcrypt"
description: "Reconstructed Codex writeup for ghostcrypt from BSidesSF CTF 2026. Original prompt weight: 744 points."
slug: bsidessf-ghostcrypt
date: 2026-03-21 20:44:35.085+0000
categories:
    - Cryptography
tags:
    - codex-archive
    - bsidessf-ctf-2026
    - ghostcrypt
---

## Challenge

- Competition: [BSidesSF CTF 2026](https://ctf.bsidessf.net/challenges)
- Challenge: `ghostcrypt`
- Category: `Cryptography`
- Points: `744`
- Original target(s): [https://ghostcrypt-2c7aa570.challenges.bsidessf.net/](https://ghostcrypt-2c7aa570.challenges.bsidessf.net/)

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge ghostcrypt Crypto We've summoned a new challenge for you. Hurry, find the flag, before it finds you! Author: symmetric


## Solve Path

**FLAG**

`CTF{murmursfromthebeyond}`

`/summon-litany` returns the ciphertext `HONHONL RNKH PQD CDZKFE`. The `/invoke` endpoint is a chosen-plaintext oracle over a 5x5 `I/J`-merged square, where odd arcana positions permute columns and even positions permute rows with a simple swap schedule. Brute-forcing the 120 row permutations and 120 column permutations gives one clear plaintext: `MURMURS FROM THE BEYOND`.

I verified it live by re-encrypting `MURMURS FROM THE BEYOND` with an equivalent 9-char arcana, `AAABBBDBD`, and the service returned the exact summon ciphertext.

Outcome: `solved`
