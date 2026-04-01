from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from textwrap import shorten


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_HOME = Path.home() / ".codex"
SESSION_ROOTS = [CODEX_HOME / "sessions", CODEX_HOME / "archived_sessions"]
POST_ROOT = REPO_ROOT / "content" / "post"
WRITEUPS_INDEX = REPO_ROOT / "content" / "page" / "writeups" / "index.md"


COMPETITION_ORDER = [
    "SUCTF 2026",
    "UpSideCTF",
    "BSidesSF CTF 2026",
    "Undutmaning 2026",
    "TAMUctf 2026",
    "TexSAW 2026",
    "KalmarCTF 2026",
    "0xV01D OSINT Lab",
    "HTB Cyber Apocalypse",
]


ITEMS = [
    {
        "sid": "019ceaa1-7759-7e41-8adc-bd6c5a5094c3",
        "slug": "suctf-su-theif",
        "title": "SUCTF 2026: SU_theif",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_theif",
        "category": "AI Security",
        "needle": "SUCTF{n0t_4ll_h1st0ry_t3lls_th3_truth_6a4e2b8d}",
    },
    {
        "sid": "019ceaa2-7be4-7a50-a5e8-b1d9921fc616",
        "slug": "suctf-su-babyai",
        "title": "SUCTF 2026: SU_babyAI",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_babyAI",
        "category": "Cryptography",
        "needle": "SUCTF{PyT0rch_m0del_c4n_h1d3_LWE_pr0bl3m}",
    },
    {
        "sid": "019ceab4-ad10-7f43-8bb5-9b603bc88718",
        "slug": "suctf-su-sqli",
        "title": "SUCTF 2026: SU_sqli",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_sqli",
        "category": "Web Exploitation",
        "needle": "SUCTF{P9s9L_!Nject!On_IS_3@$Y_RiGht}",
    },
    {
        "sid": "019ceab5-20c6-74d2-8771-0dbbc78a9566",
        "slug": "suctf-su-uri",
        "title": "SUCTF 2026: SU_uri",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_uri",
        "category": "Web Exploitation",
        "needle": "CloudHook SSRF",
    },
    {
        "sid": "019ceab5-6011-76f2-bb66-54516c0c33c5",
        "slug": "suctf-su-evbuffer",
        "title": "SUCTF 2026: SU_evbuffer",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_evbuffer",
        "category": "Binary Exploitation",
        "needle": "flag{80e59f78-d2a3-4e6a-bbbf-8027d25c2b9b}",
    },
    {
        "sid": "019ceccc-0af6-7162-8dd3-fad84030e5ec",
        "slug": "suctf-su-chronos-ring",
        "title": "SUCTF 2026: SU_Chronos_Ring",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_Chronos_Ring",
        "category": "Binary Exploitation",
        "needle": "SUCTF{VGhhc19BU19XSEFUX1Vfd0FudF9mbGFnX2ZsYWdfZmxhZyEhIQ==}",
    },
    {
        "sid": "019cf0c0-e076-74d0-824c-ca07031a7578",
        "slug": "suctf-su-cybertrack",
        "title": "SUCTF 2026: SU_CyberTrack",
        "competition": "SUCTF 2026",
        "competition_url": "https://ctftime.org/event/3161/",
        "challenge": "SU_CyberTrack",
        "category": "OSINT",
        "needle": "SUCTF{4238abfd2c042c7a9756ca38deedc710}",
    },
    {
        "sid": "019cfe5a-464e-7170-8d8e-6fba8cb66dfb",
        "slug": "0xv01d-lucy-exif-elephant",
        "title": "0xV01D OSINT: Lucy EXIF Elephant",
        "competition": "0xV01D OSINT Lab",
        "competition_url": "",
        "challenge": "lucy-exif-elephant",
        "category": "OSINT",
        "needle": "0xV01D{39.320710N_74.511443W_nrhp71000493}",
        "image_source": r"C:\Users\anas\Desktop\osint2\easy\lucy-exif-elephant\mystery_elephant.jpg",
        "image_dest": "mystery_elephant.jpg",
        "image_caption": "Original challenge image",
    },
    {
        "sid": "019d100e-4f1c-78d3-b4b4-c4327ae708c6",
        "slug": "undutmaning-undervattensstrommar",
        "title": "Undutmaning 2026: Undervattensströmmar",
        "competition": "Undutmaning 2026",
        "competition_url": "https://undutmaning.se/",
        "challenge": "Undervattensströmmar",
        "category": "Cryptography",
        "needle": "undut{lcg_w4s_n3v3r_s4f3}",
    },
    {
        "sid": "019d11f8-fca0-71a2-ab05-21099413094f",
        "slug": "undutmaning-undervattensgalleriet",
        "title": "Undutmaning 2026: Undervattensgalleriet",
        "competition": "Undutmaning 2026",
        "competition_url": "https://undutmaning.se/",
        "challenge": "Undervattensgalleriet",
        "category": "Web Exploitation",
        "needle": "undut{men_vi_hittar_alltid_svaren_28343229}",
    },
    {
        "sid": "019d1224-7f83-7131-b1f4-93c3452b146e",
        "slug": "bsidessf-ghostcrypt",
        "title": "BSidesSF CTF 2026: ghostcrypt",
        "competition": "BSidesSF CTF 2026",
        "competition_url": "https://ctf.bsidessf.net/challenges",
        "challenge": "ghostcrypt",
        "category": "Cryptography",
        "needle": "CTF{murmursfromthebeyond}",
    },
    {
        "sid": "019d1224-bd05-7f50-a884-24eddd2bd0a6",
        "slug": "bsidessf-doremi",
        "title": "BSidesSF CTF 2026: doremi",
        "competition": "BSidesSF CTF 2026",
        "competition_url": "https://ctf.bsidessf.net/challenges",
        "challenge": "doremi",
        "category": "Mobile",
        "needle": "CTF{sl1ce_and_d1c3_th3m}",
    },
    {
        "sid": "019d2415-ff50-7d80-8d0a-e87170de68d7",
        "slug": "upsidectf-ghost-in-the-machine",
        "title": "UpSideCTF: Ghost In The Machine",
        "competition": "UpSideCTF",
        "competition_url": "https://upsidectf.online/challenges",
        "challenge": "Ghost in the Machine",
        "category": "Misc",
        "needle": "CTF{Dr_n0_br3nn3R}",
    },
    {
        "sid": "019d26fb-2081-79c3-ac7e-cc5a6e58cc5a",
        "slug": "upsidectf-the-gate",
        "title": "UpSideCTF: The Gate",
        "competition": "UpSideCTF",
        "competition_url": "https://upsidectf.online/challenges",
        "challenge": "The Gate",
        "category": "Web Exploitation",
        "needle": "CTF{should_i_stay_or_should_i_head}",
    },
    {
        "sid": "019d26fb-7ef2-76e0-9c49-38568c1c8197",
        "slug": "upsidectf-max-mayfield-tape",
        "title": "UpSideCTF: The Max Mayfield Tape",
        "competition": "UpSideCTF",
        "competition_url": "https://upsidectf.online/challenges",
        "challenge": "The Max Mayfield Tape",
        "category": "Forensics",
        "needle": "CTF{V3cn4_1s_L1st3n1ng}",
        "image_source": r"C:\Users\anas\Downloads\cursed_tape_spectrogram.png",
        "image_dest": "cursed_tape_spectrogram.png",
        "image_caption": "Spectrogram used to recover the hidden text",
    },
    {
        "sid": "019d279f-2a1f-70d0-b74a-48d554abbb53",
        "slug": "upsidectf-mindflayers-gambit",
        "title": "UpSideCTF: Mindflayer's Gambit",
        "competition": "UpSideCTF",
        "competition_url": "https://upsidectf.online/challenges",
        "challenge": "Mindflayer's Gambit",
        "category": "Web Exploitation",
        "needle": "1. **Vuln chain**",
        "prompt_fallback": "Exploit the raw websocket exposed by the scoreboard box, force the service into the losing path, and peel the XOR layer keyed by `vecna` to recover the final flag.",
    },
    {
        "sid": "019d15ed-26a5-7ca1-a5d8-400a32e40d43",
        "slug": "tamuctf-tinyball",
        "title": "TAMUctf 2026: tinyball",
        "competition": "TAMUctf 2026",
        "competition_url": "https://tamuctf.com/",
        "challenge": "tinyball",
        "category": "Cryptography",
        "needle": "gigem{t1ny_l34ks_4_b1g_W1N5!11!!1!11!!eleven!1}",
    },
    {
        "sid": "019d3080-3902-7ac0-84af-1d6fa7bdc655",
        "slug": "texsaw-broken-quest",
        "title": "TexSAW 2026: Broken Quest",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "Broken Quest",
        "category": "Reverse Engineering",
        "needle": "texsaw{1t_ju5t_work5_m0r3_l1k3_!t_d0e5nt_w0rk}",
    },
    {
        "sid": "019d30ad-b9c8-7c51-9649-f5785438f7c4",
        "slug": "texsaw-switcheroo-read",
        "title": "TexSAW 2026: Switcheroo Read",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "Switcheroo Read",
        "category": "Reverse Engineering",
        "needle": "The checker is underconstrained",
    },
    {
        "sid": "019d30c9-f14a-73c0-bca7-b7d64829b9c1",
        "slug": "texsaw-drawing",
        "title": "TexSAW 2026: drawing",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "drawing",
        "category": "Reverse Engineering",
        "needle": "texsaw{VVhYd_U_M4k3_mE_s0_4n6ry}",
    },
    {
        "sid": "019d30d5-d3d3-79f0-8e44-879b0a4c004e",
        "slug": "texsaw-whats-the-time",
        "title": "TexSAW 2026: What's the Time?",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "What's the Time?",
        "category": "Binary Exploitation",
        "needle": "texsaw{7h4nk_u_f0r_y0ur_71m3}",
    },
    {
        "sid": "019d30d7-7975-75c3-80d4-4d2a7d7030e0",
        "slug": "kalmarctf-0racle",
        "title": "KalmarCTF 2026: 0racle",
        "competition": "KalmarCTF 2026",
        "competition_url": "https://kalmarc.tf/",
        "challenge": "0racle",
        "category": "Reverse Engineering",
        "needle": "KALMAR{M15S_TH3_S1GN5_4ND_3NTER_TH3_M4Z3}",
    },
    {
        "sid": "019d30e5-f80b-78e2-bbc9-40669fd9a79e",
        "slug": "texsaw-journaling",
        "title": "TexSAW 2026: Journaling",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "Journaling",
        "category": "Forensics",
        "needle": "texsaw{u5njOurn@l_unc0v3rs_4lter3d_f1les_3fd19982505363d0}",
    },
    {
        "sid": "019d30e6-ef0d-7d32-9346-19cdcc8f9ac7",
        "slug": "texsaw-model-heist",
        "title": "TexSAW 2026: Model Heist",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "Model Heist",
        "category": "Binary Exploitation",
        "needle": "texsaw{sm@sh_st4ck_2_r3turn_to_4nywh3re_y0u_w4nt}",
    },
    {
        "sid": "019d30f2-df1d-7ee1-a209-7e79451e5bc2",
        "slug": "texsaw-docker-ception",
        "title": "TexSAW 2026: Docker-ception",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "Docker-ception",
        "category": "Web Exploitation",
        "needle": "texsaw{4N_1dE4_12_L1Ke_a_V1Ru2_r351l1eN7_h19HlY_c0n74910u2}",
    },
    {
        "sid": "019d3042-46ab-74c3-85c3-36fb0eda2ccc",
        "slug": "kalmarctf-rbg-plus",
        "title": "KalmarCTF 2026: RBG+",
        "competition": "KalmarCTF 2026",
        "competition_url": "https://kalmarc.tf/",
        "challenge": "RBG+",
        "category": "Cryptography",
        "needle": "kalmar{GCD_is_handy_like_always}",
    },
    {
        "sid": "019d336a-8ce7-7723-96d8-623bdbf26e36",
        "slug": "texsaw-sigbovik-i",
        "title": "TexSAW 2026: SIGBOVIK I",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "SIGBOVIK I",
        "category": "Binary Exploitation",
        "needle": "texsaw{ezpzlmnsqzy_didyoulikethepaper?_23948102938409}",
    },
    {
        "sid": "019d33a1-84e8-7e13-a38f-2609eec245de",
        "slug": "texsaw-sigbovik-ii-errata",
        "title": "TexSAW 2026: SIGBOVIK II - Errata",
        "competition": "TexSAW 2026",
        "competition_url": "https://ctf.txs3c.com/",
        "challenge": "SIGBOVIK II - Errata",
        "category": "Binary Exploitation",
        "needle": "texsaw{primapply_ftw_02934801932840981203498}",
    },
]


HTB_POSTS = [
    ("HTB Cyber Apocalypse: Regularity", "/p/htb-regularity/"),
    ("HTB Cyber Apocalypse: Blueprint Heist", "/p/htb-blueprint-heist/"),
    ("HTB Cyber Apocalypse: OmniWatch", "/p/htb-omniwatch/"),
]


def find_session_path(sid: str) -> Path:
    for root in SESSION_ROOTS:
        hit = next(root.rglob(f"*{sid}.jsonl"), None)
        if hit:
            return hit
    raise FileNotFoundError(f"Session {sid} not found")


def load_messages(path: Path) -> tuple[list[str], list[str], dict]:
    assistants: list[str] = []
    users: list[str] = []
    session_meta: dict = {}

    for line in path.open("r", encoding="utf-8"):
        obj = json.loads(line)
        if obj.get("type") == "session_meta":
            session_meta = obj.get("payload", {})
        if obj.get("type") != "response_item":
            continue
        payload = obj.get("payload", {})
        if payload.get("type") != "message":
            continue
        text = "\n".join(
            (part.get("text") or part.get("content") or "")
            for part in payload.get("content", [])
        ).strip()
        if not text:
            continue
        role = payload.get("role")
        if role == "assistant":
            assistants.append(text)
        elif role == "user":
            users.append(text)

    return assistants, users, session_meta


def choose_text(assistant_messages: list[str], needle: str) -> str:
    matches = [msg for msg in assistant_messages if needle in msg]
    if not matches:
        raise ValueError(f"Could not find assistant message containing {needle!r}")
    matches.sort(key=len, reverse=True)
    return matches[0]


def first_user_prompt(user_messages: list[str], fallback: str = "") -> str:
    for text in user_messages:
        if any(skip in text for skip in ("<environment_context>", "AGENTS.md", "Automation:")):
            continue
        if text.startswith("You are "):
            continue
        return text
    return fallback


URL_RE = re.compile(r"https?://[^\s)]+")
LOCAL_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(((?:/?[A-Za-z]:[\\/]|/Users/)[^)]+)\)")
LOCAL_PATH_RE = re.compile(r"(?<![A-Za-z])(?:(?:[A-Za-z]:[\\/]|/Users/)[^\s`\"')]+)")


def path_label(raw_path: str) -> str:
    normalized = raw_path.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part and part != ":"]
    if not parts:
        return raw_path
    return "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]


def sanitize_markdown(text: str, asset_map: dict[str, str]) -> str:
    text = text.replace("\r\n", "\n")

    for source, dest in asset_map.items():
        windows_source = source.replace("/", "\\")
        unix_source = source.replace("\\", "/")
        text = text.replace(windows_source, dest)
        text = text.replace(unix_source, dest)

    text = LOCAL_MD_LINK_RE.sub(lambda m: f"`{m.group(1)}`", text)
    text = LOCAL_PATH_RE.sub(lambda m: f"`{path_label(m.group(0))}`", text)
    return text.strip()


def parse_prompt(prompt: str) -> dict:
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    lines = [line for line in lines if not line.startswith("# Files mentioned")]
    urls = URL_RE.findall(prompt)

    prompt_excerpt_parts: list[str] = []
    for line in lines:
        if line.startswith("## "):
            continue
        if URL_RE.search(line):
            continue
        if line.lower() == "flag":
            continue
        if "Solves" in line or "% liked" in line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if line in {"My request for Codex:", "Flag"}:
            continue
        if len(line) < 2:
            continue
        prompt_excerpt_parts.append(line)
    prompt_excerpt = " ".join(prompt_excerpt_parts[:6]).strip()

    points = next((line for line in lines if re.fullmatch(r"\d{2,4}", line)), "")
    return {
        "urls": urls,
        "points": points,
        "excerpt": shorten(prompt_excerpt, width=280, placeholder="..."),
    }


def description_for(item: dict, prompt_meta: dict) -> str:
    base = f"Reconstructed Codex writeup for {item['challenge']} from {item['competition']}."
    if prompt_meta["points"]:
        base += f" Original prompt weight: {prompt_meta['points']} points."
    return base


def copy_assets(item: dict, post_dir: Path) -> dict[str, str]:
    asset_map: dict[str, str] = {}
    source = item.get("image_source")
    dest = item.get("image_dest")
    if source and dest:
        source_path = Path(source)
        if source_path.exists():
            shutil.copy2(source_path, post_dir / dest)
            asset_map[str(source_path)] = dest
            asset_map[str(source_path).replace("\\", "/")] = dest
    return asset_map


def build_post(item: dict, prompt: str, prompt_meta: dict, session_meta: dict, text: str, asset_map: dict[str, str]) -> str:
    date_value = session_meta.get("timestamp") or session_meta.get("updated_at") or ""
    date_value = date_value.replace("T", " ").replace("Z", "+0000")

    competition_line = (
        f"- Competition: [{item['competition']}]({item['competition_url']})"
        if item.get("competition_url")
        else f"- Competition: `{item['competition']}`"
    )

    challenge_links = prompt_meta["urls"]
    challenge_lines = [competition_line, f"- Challenge: `{item['challenge']}`", f"- Category: `{item['category']}`"]
    if prompt_meta["points"]:
        challenge_lines.append(f"- Points: `{prompt_meta['points']}`")
    if challenge_links:
        challenge_lines.append(f"- Original target(s): {', '.join(f'[{url}]({url})' for url in challenge_links[:3])}")

    prompt_excerpt = prompt_meta["excerpt"] or item.get("prompt_fallback", "")
    image_caption = item.get("image_caption")
    image_dest = item.get("image_dest")
    image_block = f"![{image_caption}]({image_dest})\n" if image_dest and image_caption and (POST_ROOT / item["slug"] / image_dest).exists() else ""

    body = sanitize_markdown(text, asset_map)

    prompt_block = f"Prompt snapshot: {prompt_excerpt}" if prompt_excerpt else ""
    image_block = f"![{image_caption}]({image_dest})\n" if image_dest and image_caption and (POST_ROOT / item["slug"] / image_dest).exists() else ""

    return f"""---
title: "{item['title']}"
description: "{description_for(item, prompt_meta)}"
slug: {item['slug']}
date: {date_value}
categories:
    - {item['category']}
tags:
    - codex-archive
    - {item['competition'].lower().replace(' ', '-')}
    - {item['challenge'].lower().replace(' ', '-').replace('_', '-')}
---

## Challenge

{chr(10).join(challenge_lines)}

## Reconstruction Note

This post is reconstructed from the local Codex session log and the challenge artifacts stored in this workspace.

{prompt_block}

{image_block}
## Solve Path

{body}
"""


def generate_posts() -> list[dict]:
    generated: list[dict] = []
    for item in ITEMS:
        session_path = find_session_path(item["sid"])
        assistants, users, session_meta = load_messages(session_path)
        chosen_text = choose_text(assistants, item["needle"])
        prompt = first_user_prompt(users, item.get("prompt_fallback", ""))
        prompt_meta = parse_prompt(prompt)

        post_dir = POST_ROOT / item["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)
        asset_map = copy_assets(item, post_dir)

        content = build_post(item, prompt, prompt_meta, session_meta, chosen_text, asset_map)
        (post_dir / "index.md").write_text(content, encoding="utf-8")

        generated.append(
            {
                **item,
                "date": session_meta.get("timestamp") or session_meta.get("updated_at") or "",
                "prompt_meta": prompt_meta,
            }
        )
    return generated


def write_index(generated: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in generated:
        grouped[item["competition"]].append(item)

    for items in grouped.values():
        items.sort(key=lambda x: x["title"].lower())

    lines = [
        "---",
        'title: "Writeups"',
        'slug: "writeups"',
        'description: "Recovered Codex archive of locally solved challenges, organized by competition."',
        "menu:",
        "    main:",
        "        weight: 1",
        "        params:",
        "            icon: archives",
        "---",
        "",
        "# Writeups",
        "",
        f"This archive currently exposes `{len(generated)}` reconstructed posts pulled directly from local Codex solve sessions and challenge artifacts in this workspace.",
        "",
        "## By Competition",
        "",
    ]

    for competition in COMPETITION_ORDER:
        if competition == "HTB Cyber Apocalypse":
            continue
        items = grouped.get(competition)
        if not items:
            continue
        url = items[0].get("competition_url", "")
        heading = f"### [{competition}]({url})" if url else f"### {competition}"
        lines.extend([heading, ""])
        for item in items:
            lines.append(
                f"- [{item['title']}](/p/{item['slug']}/)  "
                f"`{item['category']}`"
            )
        lines.append("")

    lines.extend(
        [
            "### HTB Cyber Apocalypse",
            "",
            "Earlier local posts already on the site:",
            "",
        ]
    )
    for title, url in HTB_POSTS:
        lines.append(f"- [{title}]({url})")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Every post in this archive is derived from a local Codex session log, a local artifact bundle, or both.",
            "- External competition links are provided only to identify the event. The actual exploit chains are reconstructed from your local history.",
            "- Use [Archives](/archives/) for chronological browsing and [Search](/search/) if you want to jump by challenge title.",
            "",
        ]
    )

    WRITEUPS_INDEX.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    generated = generate_posts()
    write_index(generated)
    print(f"Generated {len(generated)} posts")


if __name__ == "__main__":
    main()
