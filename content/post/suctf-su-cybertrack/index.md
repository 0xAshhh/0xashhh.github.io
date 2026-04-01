---
title: "SUCTF 2026: SU_CyberTrack"
description: "Writeup for SU_CyberTrack from SUCTF 2026."
slug: suctf-su-cybertrack
date: 2026-03-15 09:08:18.872+0000
competition: "SUCTF 2026"
categories:
    - OSINT
tags:
    - writeup
    - suctf-2026
    - su-cybertrack
---

## Challenge

- Competition: [SUCTF 2026](https://ctftime.org/event/3161/)
- Challenge: `SU_CyberTrack`
- Category: `OSINT`
- Original target(s): [https://evanlin-suctf.github.io/](https://evanlin-suctf.github.io/)


## Solve Path

**Analysis**
The strongest evidence chain is:

- The blog title identifies the person as `Evan Lin`: [site](https://evanlin-suctf.github.io/).
- The birthday post fixes `11/23`: [Happy birthday](https://evanlin-suctf.github.io/posts/Happy-birthday/).
- The public GitHub Pages repo leaks the commit author email `evanlin1123@foxmail.com`: [repo](https://github.com/EvanLin-SUCTF/EvanLin-SUCTF.github.io), [commit](https://github.com/EvanLin-SUCTF/EvanLin-SUCTF.github.io/commit/2796f3b4537dc0c1891da002dc9d02ab9f71b008).
- The site avatar’s Gravatar SHA-256 matches that email exactly, confirming the identity link.
- The Minecraft screenshot shows the old handle `Mnzn233`: [Play with me t_t](https://evanlin-suctf.github.io/posts/play-with-me-T_T/).

**Attack vectors**
- Site enumeration via `robots.txt`, `sitemap.xml`, posts, and search index.
- GitHub source/commit metadata for leaked identity data.
- Screenshot inspection for old username reuse.

**Execution logic**
- Name inference: `Evan Lin` -> surname first -> `linevan`.
- Discovered string: `Mnzn233` -> lowercase `mnzn233`.
- Constructed string: `linevan_mnzn233`.
- MD5: `4238abfd2c042c7a9756ca38deedc710`.

**Findings**
Flag: `SUCTF{4238abfd2c042c7a9756ca38deedc710}`

**Next pivot if needed**
If the platform rejects it, the only realistic ambiguity is OCR on the username in the Minecraft screenshot, but it reads as `Mnzn233`, not `Mn2n233`.
