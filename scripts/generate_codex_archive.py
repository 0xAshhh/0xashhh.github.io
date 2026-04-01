from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from textwrap import shorten


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_HOME = Path.home() / ".codex"
SESSION_ROOTS = [CODEX_HOME / "sessions", CODEX_HOME / "archived_sessions"]
HISTORY_PATH = CODEX_HOME / "history.jsonl"
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
        "category": "Model Exploitation",
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


CURATED_HISTORY_ITEMS = [
    {
        "sid": "019c530f-a7e4-7fd1-b89a-cc5d721cd425",
        "slug": "0xfunctf-tony-toolkit",
        "title": "0xFunCTF: Tony Toolkit",
        "competition": "0xFunCTF",
        "competition_url": "",
        "challenge": "Tony Toolkit",
        "category": "Web Exploitation",
        "flag": "0xfun{T0ny'5_T00ly4rd._1_H0p3_Y0u_H4d_Fun_SQL1ng,_H45H_Cr4ck1ng,_4nd_W1th_C00k13_M4n1pu74t10n}",
        "prompt_override": "Tony Toolkit\n500\nmedium\nhttp://chall.0xfun.org:11588",
    },
    {
        "sid": "019c84da-4485-7fe0-85e5-9c2299aadb10",
        "slug": "bkctf-appreciating-graphic-design",
        "title": "BKCTF: Appreciating Graphic Design",
        "competition": "BKCTF",
        "competition_url": "",
        "challenge": "Appreciating Graphic Design",
        "category": "Misc",
        "flag": "bkctf{4rt_h4z_l4y3rz_l1k3_0ni0n}",
    },
    {
        "sid": "019c81c1-8726-7c51-8017-7248d766570c",
        "slug": "bkctf-gotham-microsystems",
        "title": "BKCTF: Gotham MicroSystems",
        "competition": "BKCTF",
        "competition_url": "",
        "challenge": "Gotham MicroSystems",
        "category": "Cryptography",
        "flag": "bkctf{b4rb4r4_g0rd0ns_f4v0r1t3_4tt4ck}",
    },
    {
        "sid": "019cc513-59ef-7c00-9f59-2f4d01883c9c",
        "slug": "bkctf-hello-agent",
        "title": "BKCTF: Hello Agent",
        "competition": "BKCTF",
        "competition_url": "",
        "challenge": "Hello Agent",
        "category": "OSINT",
        "flag": "bkctf{sup3rv3ryt074llyc00l}",
    },
    {
        "sid": "019c7f85-9a6d-7543-a0ec-cac095cbe831",
        "slug": "bkctf-speedrunning",
        "title": "BKCTF: Speedrunning",
        "competition": "BKCTF",
        "competition_url": "",
        "challenge": "Speedrunning",
        "category": "Misc",
        "flag": "bkctf{m1nc3dr4ft_m4nhunt_0n3_hunt3r}",
    },
    {
        "sid": "019ca989-56fa-7d63-8d40-49a986c07d7f",
        "slug": "cert-crypto-sanity-check-rotted",
        "title": "CERT: Crypto Sanity Check - rotted",
        "competition": "CERT",
        "competition_url": "",
        "challenge": "Crypto Sanity Check rotted",
        "category": "Cryptography",
        "flag": "CERT{symm37ric_r0747i0n}",
    },
    {
        "sid": "019ca9bf-5a66-75d0-8c2d-c67077df463d",
        "slug": "cert-span-sniff",
        "title": "CERT: SPAN sniff",
        "competition": "CERT",
        "competition_url": "",
        "challenge": "SPAN sniff",
        "category": "Forensics",
        "flag": "CERT{h1DD3n_1n_pl41n7eX7_n37Fl0w}",
    },
    {
        "sid": "019cc4c3-32e5-7993-8f12-8e18afd8f7cc",
        "slug": "jsec-wip-stage",
        "title": "JSEC: Wip Stage",
        "competition": "JSEC",
        "competition_url": "",
        "challenge": "Wip Stage",
        "category": "Cryptography",
        "flag": "JSEC{m3rs3nn3_tw1st3r_1s_n0t_s3cur3_3939}",
    },
    {
        "sid": "019ce95a-cb76-75e2-8f3e-ecaba751643b",
        "slug": "mctf-beneath-the-fourth-moon",
        "title": "MCTF: Beneath the Fourth Moon",
        "competition": "MCTF",
        "competition_url": "",
        "challenge": "Beneath the Fourth Moon",
        "category": "Cryptography",
        "flag": "MCTF{eb9b65f02ff7443a1b260247d90e36700b7a54a18446527dbdb8377d285f61a30c2564de1e42696e5826c92d95f41eae8f1f8769aeeecbf46bc98689c893615a}",
    },
    {
        "sid": "019c9f4f-7a36-78a3-ad1b-34fd964520ed",
        "slug": "uvt-satellua",
        "title": "UVT: satellua",
        "competition": "UVT",
        "competition_url": "",
        "challenge": "satellua",
        "category": "Reverse Engineering",
        "flag": "UVT{R3turn_8y_Thr0w_Del1v3r3r}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-qrecreate",
        "title": "UTCTF 2026: QRecreate",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "QRecreate",
        "category": "Misc",
        "flag": "utflag{s3cr3ts_@re_@lw@ys_w1th1n_s3cr3ts}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-silent-archive",
        "title": "UTCTF 2026: Silent Archive",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Silent Archive",
        "category": "Forensics",
        "flag": "utflag{d1ff_th3_tw1ns_unt4r_th3_st0rm_r34d_th3_wh1t3sp4c3}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-half-awake",
        "title": "UTCTF 2026: Half Awake",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Half Awake",
        "category": "Forensics",
        "flag": "utflag{h4lf_aw4k3_s33_th3_pr0t0c0l_tr1ck}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-cold-workspace",
        "title": "UTCTF 2026: Cold Workspace",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Cold Workspace",
        "category": "Forensics",
        "flag": "utflag{m3m0ry_r3t41ns_wh4t_d1sk_l053s}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-fortune-teller",
        "title": "UTCTF 2026: Fortune Teller",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Fortune Teller",
        "category": "Cryptography",
        "flag": "utflag{pr3d1ct_th3_futur3_lcg}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-hidden-in-plain-sight",
        "title": "UTCTF 2026: Hidden in Plain Sight",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Hidden in Plain Sight",
        "category": "Misc",
        "flag": "utflag{1nv1s1bl3_un1c0d3}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-jail-break",
        "title": "UTCTF 2026: Jail Break",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Jail Break",
        "category": "Misc",
        "flag": "utflag{py_ja1l_3sc4p3_m4st3r}",
    },
    {
        "sid": "019ce537-ccfe-77b2-b035-32bda09fc434",
        "slug": "utctf-landfall",
        "title": "UTCTF 2026: Landfall",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Landfall",
        "category": "Forensics",
        "flag": "utflag{4774ck3r5_h4v3_m4d3_l4ndf4ll}",
    },
    {
        "sid": "019ce537-ccfe-77b2-b035-32bda09fc434",
        "slug": "utctf-landfall-missing-link",
        "title": "UTCTF 2026: Landfall Missing Link",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Landfall Missing Link",
        "category": "Forensics",
        "flag": "utflag{pr1v473_3y3-m1551n6_l1nk}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-last-byte-standing",
        "title": "UTCTF 2026: Last Byte Standing",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Last Byte Standing",
        "category": "Forensics",
        "flag": "utflag{d1g_t0_th3_l4st_byt3}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-oblivious-error",
        "title": "UTCTF 2026: Oblivious Error",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Oblivious Error",
        "category": "Cryptography",
        "flag": "utflag{my_obl1v10u5_fr13nd_ru1n3d_my_c0de}",
    },
    {
        "sid": "019ce4b8-22de-7672-bc00-91eccfa0ed6a",
        "slug": "utctf-smooth-criminal",
        "title": "UTCTF 2026: Smooth Criminal",
        "competition": "UTCTF 2026",
        "competition_url": "",
        "challenge": "Smooth Criminal",
        "category": "Cryptography",
        "flag": "utflag{sm00th_cr1m1nal_caught}",
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


def load_assistant_records(path: Path) -> tuple[list[dict], dict]:
    assistants: list[dict] = []
    session_meta: dict = {}

    for line in path.open("r", encoding="utf-8"):
        obj = json.loads(line)
        if obj.get("type") == "session_meta":
            session_meta = obj.get("payload", {})
        if obj.get("type") != "response_item":
            continue
        payload = obj.get("payload", {})
        if payload.get("type") != "message" or payload.get("role") != "assistant":
            continue
        text = "\n".join(
            (part.get("text") or part.get("content") or "")
            for part in payload.get("content", [])
        ).strip()
        if not text:
            continue
        assistants.append(
            {
                "timestamp": obj.get("timestamp", ""),
                "text": text,
            }
        )

    return assistants, session_meta


def load_history_by_sid() -> dict[str, list[dict]]:
    history_by_sid: dict[str, list[dict]] = defaultdict(list)
    if not HISTORY_PATH.exists():
        return history_by_sid

    with HISTORY_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            obj = json.loads(line)
            sid = obj.get("session_id")
            if not sid:
                continue
            history_by_sid[sid].append(
                {
                    "ts": int(obj.get("ts", 0)),
                    "text": obj.get("text", ""),
                }
            )

    for sid in history_by_sid:
        history_by_sid[sid].sort(key=lambda item: item["ts"])

    return history_by_sid


def prompt_seed_candidates(history_items: list[dict]) -> list[dict]:
    candidates: list[dict] = []
    previous_norm = ""

    for item in history_items:
        text = item["text"].strip()
        if not text:
            continue
        if text.startswith("# AGENTS") or text.startswith("<environment_context>"):
            continue
        normalized = re.sub(r"\s+", " ", text)
        if normalized == previous_norm:
            continue
        if len(text) < 18:
            continue
        if text.lower() in {"challenge", "flag", "download", "downloads"}:
            continue

        score = 0
        if "\n" in text:
            score += 1
        if re.search(r"\b(solves?|points?|easy|medium|hard|crypto|pwn|misc|web|osint|forensics|rev|mobile)\b", text, re.I):
            score += 2
        if re.search(r"https?://|[A-Za-z]:\\", text):
            score += 1
        if re.search(r"Challenge|Downloads?|Flag|0 حل", text, re.I):
            score += 1
        if len(text) > 80:
            score += 1
        if score < 2:
            continue

        candidates.append(item)
        previous_norm = normalized

    return candidates


def choose_history_prompt(history_items: list[dict], assistant_timestamp: str) -> str:
    if not history_items or not assistant_timestamp:
        return ""

    target_ts = int(datetime.fromisoformat(assistant_timestamp.replace("Z", "+00:00")).timestamp())
    candidates = [item for item in prompt_seed_candidates(history_items) if item["ts"] <= target_ts]
    if not candidates:
        return ""
    return candidates[-1]["text"]


def choose_assistant_record(records: list[dict], flag: str) -> dict:
    matches = [record for record in records if flag in record["text"]]
    if not matches:
        raise ValueError(f"Could not find assistant message containing {flag!r}")
    matches.sort(key=lambda record: (len(record["text"]), record["timestamp"]), reverse=True)
    return matches[0]


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
    base = f"Writeup for {item['challenge']} from {item['competition']}."
    if prompt_meta["points"]:
        base += f" Challenge weight: {prompt_meta['points']} points."
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

    image_caption = item.get("image_caption")
    image_dest = item.get("image_dest")
    image_block = f"![{image_caption}]({image_dest})\n" if image_dest and image_caption and (POST_ROOT / item["slug"] / image_dest).exists() else ""

    body = sanitize_markdown(text, asset_map)

    image_block = f"![{image_caption}]({image_dest})\n" if image_dest and image_caption and (POST_ROOT / item["slug"] / image_dest).exists() else ""

    return f"""---
title: "{item['title']}"
description: "{description_for(item, prompt_meta)}"
slug: {item['slug']}
date: {date_value}
competition: "{item['competition']}"
categories:
    - {item['category']}
tags:
    - writeup
    - {item['competition'].lower().replace(' ', '-')}
    - {item['challenge'].lower().replace(' ', '-').replace('_', '-')}
---

## Challenge

{chr(10).join(challenge_lines)}

{image_block}
## Solve Path

{body}
"""


def count_published_posts() -> int:
    return sum(1 for path in POST_ROOT.iterdir() if path.is_dir() and (path / "index.md").exists())


def generate_posts() -> list[dict]:
    history_by_sid = load_history_by_sid()
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

    for item in CURATED_HISTORY_ITEMS:
        session_path = find_session_path(item["sid"])
        assistant_records, session_meta = load_assistant_records(session_path)
        chosen_record = choose_assistant_record(assistant_records, item["flag"])
        prompt = item.get("prompt_override") or choose_history_prompt(history_by_sid.get(item["sid"], []), chosen_record["timestamp"])
        prompt_meta = parse_prompt(prompt)

        post_dir = POST_ROOT / item["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)

        content = build_post(item, prompt, prompt_meta, session_meta, chosen_record["text"], {})
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
    archive_count = count_published_posts()
    lines = [
        "---",
        'title: "Writeups"',
        'slug: "writeups"',
        'description: "Challenge writeups and solve notes organized by competition."',
        'layout: "writeups"',
        "menu:",
        "    main:",
        "        weight: 1",
        "        params:",
            "            icon: archives",
        "---",
        "",
        "# Writeups",
        "",
        f"This archive currently exposes `{archive_count}` published writeups collected from solved challenges and preserved notes.",
        "",
        "The cards below are generated from the live post collection, so anything published into the archive appears here automatically.",
        "",
        "## Notes",
        "",
        "- Every post in this archive is grounded in local files, saved solve notes, or both.",
        "- External competition links are provided only to identify the event and challenge.",
        "- Use [Archives](/archives/) for chronological browsing and [Search](/search/) if you want to jump by challenge title.",
        "",
    ]

    WRITEUPS_INDEX.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    generated = generate_posts()
    write_index(generated)
    print(f"Generated {len(generated)} posts")


if __name__ == "__main__":
    main()
