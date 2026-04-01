---
title: "SUCTF 2026: SU_babyAI"
description: "Reconstructed Codex writeup for SU_babyAI from SUCTF 2026."
slug: suctf-su-babyai
date: 2026-03-14 04:37:23.107+0000
categories:
    - Cryptography
tags:
    - codex-archive
    - suctf-2026
    - su-babyai
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_babyAI`
- Category: `Cryptography`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: SU_babyAI 344PT AI It seems like something is missing. 请输入题目Flag


## Solve Path

1) Category detection
- Detected category: `crypto`, confidence `high`.
- Evidence: the model reduces to a noisy modular linear system over a large prime `q = 1000000007`; the recovered structure is LWE-like, with the neural-net framing as a wrapper.

2) Attack strategy
- Primary hypothesis: expand the conv+fc stack into one linear map over the 41 flag bytes, fix the known `SUCTF{...}` format, and recover the bounded ASCII plaintext with a lattice CVP solve.
- Planned validation tests: recover a printable candidate, then recompute the published `Y` and check all noise terms stay within `[-160, 160]`.

3) Execution steps
- Loaded the saved weights from the provided archive and inferred the real length is `41`; the fake placeholder in `task.py` is intentionally inconsistent.
- Collapsed the network into a `15 x 41` matrix `M` over `Z_q`.
- Fixed prefix `SUCTF{` and suffix `}` and centered the remaining 34 unknown bytes around ASCII `79`.
- Built the lattice basis `B = [[qI, M_u], [0, λI]]` with `λ = 3`, ran LLL, then used Babai nearest-plane on the target derived from `Y`.
- Recovered the printable candidate:
  `SUCTF{PyT0rch_m0del_c4n_h1d3_LWE_pr0bl3m}`
- Verified it exactly against the challenge equations. The recomputed outputs match the published `Y`, with noise:
  `[53, -105, -105, 55, -9, 17, -65, 2, -140, 111, -101, -76, -81, -126, 109]`
  and `max |noise| = 140`, which satisfies the bound.

4) FLAG
SUCTF{PyT0rch_m0del_c4n_h1d3_LWE_pr0bl3m}

5) Writeup
- The PyTorch model is a red herring around a noisy linear modular system. After expanding the layers, the problem becomes bounded plaintext recovery under a large modulus with tiny additive noise. LLL plus nearest-plane recovers the unique printable solution, and plugging it back into the original arithmetic reproduces the exact published outputs within the allowed noise range.
