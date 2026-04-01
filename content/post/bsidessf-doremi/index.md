---
title: "BSidesSF CTF 2026: doremi"
description: "Reconstructed Codex writeup for doremi from BSidesSF CTF 2026. Original prompt weight: 516 points."
slug: bsidessf-doremi
date: 2026-03-21 20:44:50.834+0000
categories:
    - Mobile
tags:
    - codex-archive
    - bsidessf-ctf-2026
    - doremi
---

## Challenge

- Competition: [BSidesSF CTF 2026](https://ctf.bsidessf.net/challenges)
- Challenge: `doremi`
- Category: `Mobile`
- Points: `516`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge doremi Mobile 101 Can you find the flag on the app? Author: itsc0rg1


## Solve Path

`CTF{sl1ce_and_d1c3_th3m}`

I recovered it by rendering the five vector drawables and stacking them with the frame asset. The green note labels `Do Re Mi Fa Sol` give the read order for the purple fragments: `CTF{` `sl1ce` `and` `d1c3` `th3m}`.

!`composed flag`
