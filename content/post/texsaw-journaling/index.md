---
title: "TexSAW 2026: Journaling"
description: "Reconstructed Codex writeup for Journaling from TexSAW 2026. Original prompt weight: 366 points."
slug: texsaw-journaling
date: 2026-03-27 20:04:30.869+0000
categories:
    - Forensics
tags:
    - codex-archive
    - texsaw-2026
    - journaling
---

## Challenge

- Competition: [TexSAW 2026](https://ctf.txs3c.com/)
- Challenge: `Journaling`
- Category: `Forensics`
- Points: `366`

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

Prompt snapshot: Challenge Journaling Written by Wulfyrn I was using this Windows machine for journaling and notetaking, but I think malware got onto it. Can you take a look and put together any evidence left on disk? Note 1: Sufficient information is provided to figure out the order of flag...


## Solve Path

1) Category detection

Windows DFIR / NTFS artifact recovery. High confidence: the artifact is a raw NTFS disk image, and the useful evidence came from live files, ADS, deleted MFT entries, `$UsnJrnl`, and `$LogFile`.

2) Attack strategy

Recover every `flagsegment_*` value from the filesystem and NTFS metadata, then order them using the journal timeline plus the note in `tasks.txt` saying to “find out where part 5 is...”.

3) Execution steps

- `icat -o 128 evidence.001 945-128-3` on `Users/user/Notes/tasks.txt:source` returned `flagsegment_3fd19982505363d0`.
- `usnjls -o 128 evidence.001 | grep flagsegment` showed:
  - `flagsegment_u5njOurn@l` directory creation.
  - `flagsegment_unc0v3rs.txt` creation, then rename to `notetoself.txt`.
  - `flagsegment_f1les.txt` creation, then deletion.
- `icat -o 128 evidence.001 2-128-1 | strings -el | grep flagsegment_` revealed `flagsegment_4lter3d`.
- The `tasks.txt` content says `find out where part 5 is...`, so the ADS value is the fifth segment.
- I infer the final ordering as `u5njOurn@l_unc0v3rs_4lter3d_f1les_3fd19982505363d0` from the NTFS timeline and the only coherent phrase formed by the recovered segments.

4) FLAG

`texsaw{u5njOurn@l_unc0v3rs_4lter3d_f1les_3fd19982505363d0}`

5) Writeup

The malware staged data under a fake `Program Files/Microsoft/OneDrive/ListSync` path, renamed `flagsegment_unc0v3rs.txt` into `notetoself.txt` containing stolen creds, created and deleted `flagsegment_f1les.txt`, and hid the last segment in the ADS of `tasks.txt`. The NTFS journals preserved the deleted/transient names, which is the key to reconstructing the flag.
