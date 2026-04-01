---
title: "UTCTF 2026: Hidden in Plain Sight"
description: "Writeup for Hidden in Plain Sight from UTCTF 2026. Challenge weight: 990 points."
slug: utctf-hidden-in-plain-sight
date: 2026-03-13 01:03:18.764+0000
competition: "UTCTF 2026"
categories:
    - Misc
tags:
    - writeup
    - utctf-2026
    - hidden-in-plain-sight
---

## Challenge

- Competition: `UTCTF 2026`
- Challenge: `Hidden in Plain Sight`
- Category: `Misc`
- Points: `990`


## Solve Path

1) Category detection

- Detected category: `misc`
- Confidence: high
- Evidence: there was no challenge file, so the only local artifact tied to this challenge was the Chrome history entry for the UTCTF challenge page. That URL fragment contains percent-encoded Unicode tag characters hidden inside `Hidden ... in Plain Sight`.

2) Attack strategy

- Primary hypothesis: the hidden message is embedded directly in the challenge page title/URL using invisible Unicode characters.
- Why it is minimal: the challenge name is literally `Hidden in Plain Sight`, and Chrome history already contained the exact `utctf.live/challenges#...` fragment.
- Validation test: extract the history URL, percent-decode it, then convert Unicode tag characters `U+E0000..U+E007F` back to ASCII.

3) Execution steps

- Repro:
```powershell
@'
import os, shutil, sqlite3
from pathlib import Path
from urllib.parse import unquote

hist = Path(os.environ['LOCALAPPDATA']) / 'Google/Chrome/User Data/Default/History'
tmp = Path(r'`Temp/hist_hidden_plain_sight.db`')
shutil.copy2(hist, tmp)

con = sqlite3.connect(tmp)
url = con.execute(
    "select url from urls where url like '%utctf.live/challenges#Hidden%' "
    "order by last_visit_time desc limit 1"
).fetchone()[0]
con.close()

print('URL:', url)

frag = url.split('#', 1)[1]
decoded = unquote(frag)
print('Decoded:', decoded.encode('unicode_escape').decode())

hidden = ''.join(
    chr(ord(c) - 0xE0000)
    for c in decoded
    if 0xE0000 <= ord(c) <= 0xE007F
)
print('Hidden:', hidden)
'@ | python -
```
- Key output:
  - URL fragment contained:
    `Hidden %F3%A0%81%B5...%F3%A0%81%BDin Plain Sight-25`
  - Decoded Unicode sequence:
    `\U000e0075\U000e0074\U000e0066...`
  - Final extracted text:
    `utflag{1nv1s1bl3_un1c0d3}`

4) FLAG

`utflag{1nv1s1bl3_un1c0d3}`

5) Writeup

The solve path was hidden in the challenge page reference itself, not in a downloadable file. Chrome history contained the UTCTF challenge URL for `Hidden in Plain Sight`, and that URL fragment included invisible Unicode tag characters between the visible words `Hidden` and `in Plain Sight`.

Those characters are in the Unicode tag block (`U+E0000`-style values such as `U+E0075`, `U+E0074`, ...), which encode plain ASCII when you subtract `0xE0000`. Decoding the sequence reveals the flag directly:

`utflag{1nv1s1bl3_un1c0d3}`
