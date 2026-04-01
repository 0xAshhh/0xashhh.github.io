---
title: "UTCTF 2026: Silent Archive"
description: "Writeup for Silent Archive from UTCTF 2026. Challenge weight: 989 points."
slug: utctf-silent-archive
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Forensics
tags:
    - writeup
    - utctf-2026
    - silent-archive
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Silent Archive`
- Category: `Forensics`
- Points: `989`


## Solve Path

1) Category detection

- Detected category: `misc`
- Confidence: high
- Evidence: `freem4.zip` contains two forensic-style branches:
  `File1.tar` with two near-identical JPEGs
  `File2.tar` with a 999-level nested tar chain ending in an encrypted ZIP

2) Attack strategy

- Primary hypothesis: the JPEG branch contains the password or instructions, and the deep archive branch contains the final encoded payload.
- Why it is minimal:
  the two JPEGs differ only in appended telemetry after the JPEG `FFD9` marker
  the deep chain ends in `Noo.txt`, which is actually a ZIP, so the two branches naturally fit as `hint/password` plus `payload`
- Validation tests:
  extract the differing telemetry from the JPEG pair
  use any decoded fragment as ZIP password candidates
  decode the decrypted payload using the simplest visible scheme first

3) Execution steps

- Outer ZIP contents:
  `File1.tar`
  `File2.tar`
  `README.txt`
- `File1.tar` contains:
  `cam_300.jpg`
  `cam_301.jpg`
- Both JPEGs are valid images with identical image data and identical appended telemetry except one line:
```text
AUTH_FRAGMENT_B64:QWx3YXlzX2NoZWNrX2JvdGhfaW1hZ2Vz
AUTH_FRAGMENT_B64:MHI0bmczX0FyQ2gxdjNfVDRiU3A0Y2Uh
```
- Decoding those gives:
  `Always_check_both_images`
  `0r4ng3_ArCh1v3_T4bSp4ce!`
- `File2.tar` is a nested tar chain:
  `999.tar -> 998.tar -> ... -> 1.tar -> Noo.txt`
- `Noo.txt` begins with `PK`, so it is a ZIP archive, not text.
- That terminal ZIP contains:
  `NotaFlag.txt`
  `notes.md`
- The correct ZIP password is:
  `0r4ng3_ArCh1v3_T4bSp4ce!`
- `NotaFlag.txt` decrypts to 58 lines of 8 whitespace characters each.
- Interpreting `space = 0` and `tab = 1` per line yields bytes that decode directly to:
  `utflag{d1ff_th3_tw1ns_unt4r_th3_st0rm_r34d_th3_wh1t3sp4c3}`

Repro script:
```powershell
@'
import io, tarfile, zipfile, base64

# branch 1: get password fragment from differing JPEG telemetry
with zipfile.ZipFile(r'`Downloads/freem4.zip`') as z:
    file1 = z.read('File1.tar')
with tarfile.open(fileobj=io.BytesIO(file1)) as t:
    a = t.extractfile('cam_300.jpg').read()
    b = t.extractfile('cam_301.jpg').read()

tail_a = a[a.rfind(b'\xff\xd9')+2:].decode()
tail_b = b[b.rfind(b'\xff\xd9')+2:].decode()
frag = [line.split(':',1)[1] for line in tail_b.splitlines() if line.startswith('AUTH_FRAGMENT_B64:')][0]
pwd = base64.b64decode(frag).decode()

# branch 2: walk tar chain and decrypt terminal zip
with zipfile.ZipFile(r'`Downloads/freem4.zip`') as z:
    data = z.read('File2.tar')
for _ in range(1000):
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        m = t.getmembers()[0]
        data = t.extractfile(m).read()
        if not m.name.endswith('.tar'):
            break

zf = zipfile.ZipFile(io.BytesIO(data))
ws = zf.read('NotaFlag.txt', pwd=pwd.encode())
flag = ''.join(chr(int(''.join('1' if c == 9 else '0' for c in line), 2)) for line in ws.splitlines())
print(flag)
'@ | python -
```

4) FLAG

`utflag{d1ff_th3_tw1ns_unt4r_th3_st0rm_r34d_th3_wh1t3sp4c3}`

5) Writeup

The JPEG branch was the password trail. The two files were intentionally “duplicate captures,” but they differed in a single appended telemetry field after the JPEG end marker. Decoding the differing base64 fragment from `cam_301.jpg` produced the password `0r4ng3_ArCh1v3_T4bSp4ce!`.

The deep archive branch was the payload trail. `File2.tar` unwraps through 999 nested tars until `Noo.txt`, which is actually a ZIP archive. Using the password from the camera branch decrypts `NotaFlag.txt`, whose contents are pure spaces and tabs. Mapping spaces to `0` and tabs to `1` per 8-character line yields the final token:
`utflag{d1ff_th3_tw1ns_unt4r_th3_st0rm_r34d_th3_wh1t3sp4c3}`.
