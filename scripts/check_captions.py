#!/usr/bin/env python3
"""
check_captions.py - Cek apakah video YouTube punya caption (SC 1.2.2 Captions Prerecorded).

Metode: ambil halaman `watch?v=<id>` lalu parse `captionTracks` dari `ytInitialPlayerResponse`.
Tidak memakai YouTube Data API (butuh API key berbayar). Read-only GET, jeda >= 1 detik.

Penting: yang dicek hanya KETERSEDIAAN caption (apakah ada track Bahasa Indonesia dan/atau
Inggris, apakah hasil auto-generated). Kualitas akurasi caption tetap perlu ditinjau manual.

Output: results/automated/caption-check-YYYYMMDD/
  - caption-check.csv
  - caption-check-results.json
  - summary.md

Idempotent: cache per video id di inventory/.cache/caption-<id>.json

Usage:
    python scripts/check_captions.py
    python scripts/check_captions.py --no-cache --delay 2
"""

import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).parent.parent
MEDIA_CSV = PROJECT_ROOT / "inventory" / "media.csv"
CACHE_DIR = PROJECT_ROOT / "inventory" / ".cache"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "automated"

REQUEST_DELAY = 1.5
TIMEOUT = 45
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

VIDEO_ID_RE = re.compile(r"(?:embed/|v=|youtu\.be/|/shorts/)([A-Za-z0-9_-]{11})")


def video_id_from(url):
    m = VIDEO_ID_RE.search(url or "")
    return m.group(1) if m else None


def cache_path(vid):
    return CACHE_DIR / f"caption-{vid}.json"


def load_cache(vid):
    p = cache_path(vid)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def save_cache(vid, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(vid).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def extract_json_array(text, key):
    """Ambil array JSON setelah `"key":[` dengan pencocokan kurung kurawal."""
    marker = f'"{key}":['
    start = text.find(marker)
    if start == -1:
        return None
    i = start + len(marker) - 1
    depth = 0
    in_str = False
    escape = False
    for j in range(i, len(text)):
        ch = text[j]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[i:j + 1])
                except ValueError:
                    return None
    return None


def extract_playability_status(text):
    """Baca status dari blok playabilityStatus di ytInitialPlayerResponse.

    Regex `"status":"..."` terlalu longgar: halaman penuh JSON lain yang punya
    field status (LIKE/INDIFFERENT/OK). Kalau YouTube menyajikan interstitial bot
    check, statusnya LOGIN_REQUIRED dengan alasan "konfirmasi Anda bukan bot" - itu
    TIDAK boleh dihitung sebagai "video tanpa caption".
    """
    start = text.find("ytInitialPlayerResponse")
    segment = text[start:start + 200000] if start != -1 else text
    m = re.search(r'"playabilityStatus":\{"status":"([A-Z_]+)"', segment)
    if m:
        reason = re.search(r'"reason":"([^"]{0,120})"', segment)
        return m.group(1), (reason.group(1) if reason else "")
    m2 = re.search(r'"status":"([A-Z_]+)"', segment)
    return (m2.group(1) if m2 else "UNKNOWN"), ""


def main():
    ap = argparse.ArgumentParser(description="Cek ketersediaan caption video YouTube")
    ap.add_argument("--delay", type=float, default=REQUEST_DELAY)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    if not MEDIA_CSV.exists():
        print("[ERROR] inventory/media.csv tidak ada. Jalankan crawl_inventory.py dulu.", file=sys.stderr)
        return 1

    date_str = datetime.now().strftime("%Y%m%d")
    out_dir = OUTPUT_ROOT / f"caption-check-{date_str}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(MEDIA_CSV, encoding="utf-8")))
    video_rows = [r for r in rows if r.get("platform") == "embed-video"]

    targets = {}
    for r in video_rows:
        vid = video_id_from(r["url"])
        if vid and vid not in targets:
            targets[vid] = r

    print(f"[CAPTION] {len(targets)} video unik dari {len(video_rows)} embed")
    print(f"[CAPTION] output: {out_dir}\n")

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"})

    results = []
    stats = {"checked": 0, "cache": 0, "no_captions": 0, "manual_only": 0,
             "auto_only": 0, "with_id": 0, "with_en": 0, "failed": 0, "undetermined": 0}
    start = time.time()

    for i, (vid, row) in enumerate(sorted(targets.items()), 1):
        cached = None if args.no_cache else load_cache(vid)
        if cached:
            stats["cache"] += 1
        else:
            time.sleep(args.delay)
            try:
                resp = session.get(f"https://www.youtube.com/watch?v={vid}",
                                   timeout=TIMEOUT, allow_redirects=True)
                if resp.status_code != 200:
                    cached = {"video_id": vid, "error": f"HTTP {resp.status_code}",
                              "has_captions": None, "tracks": []}
                else:
                    tracks = extract_json_array(resp.text, "captionTracks") or []
                    player_status, reason = extract_playability_status(resp.text)
                    summary = []
                    for t in tracks:
                        base = t.get("baseUrl", "")
                        m = re.search(r"&lang=([^&]+)", base)
                        summary.append({
                            "lang": m.group(1) if m else t.get("languageCode", ""),
                            "kind": t.get("kind", ""),
                            "name": ((t.get("name") or {}).get("simpleText")
                                     or ((t.get("name") or {}).get("runs") or [{}])[0].get("text", "")),
                        })
                    # Player response LOGIN_REQUIRED/UNPLAYABLE tidak memuat captionTracks
                    # sama sekali. Jangan dianggap "tanpa caption" - statusnya tidak bisa
                    # dipastikan tanpa login (age-restricted atau member-only).
                    determinable = player_status == "OK"
                    cached = {
                        "video_id": vid,
                        "player_status": player_status,
                        "status_reason": reason,
                        "has_captions": bool(tracks) if determinable else None,
                        "tracks": summary,
                        "auto_generated": any(t["kind"] == "asr" for t in summary),
                        "manual": [t["lang"] for t in summary if t["kind"] != "asr"],
                        "auto": [t["lang"] for t in summary if t["kind"] == "asr"],
                    }
            except requests.RequestException as e:
                cached = {"video_id": vid, "error": str(e), "has_captions": None, "tracks": []}
            save_cache(vid, cached)

        cached["source_page"] = row.get("source_page", "")
        cached["embed_title"] = row.get("frame_title", "")
        cached["checked_at"] = datetime.now().isoformat(timespec="seconds")
        results.append(cached)

        langs = cached.get("tracks") and [t["lang"] for t in cached["tracks"]] or []
        if cached.get("error"):
            stats["failed"] += 1
            state = f"ERROR {cached['error'][:40]}"
        elif cached.get("player_status") != "OK":
            stats["undetermined"] += 1
            reason = (cached.get("status_reason") or "")[:40]
            state = f"TIDAK bisa dipastikan ({cached.get('player_status')}" + (f": {reason}" if reason else "") + ")"
        elif not cached.get("has_captions"):
            stats["no_captions"] += 1
            state = "TIDAK ADA caption"
        else:
            stats["checked"] += 1
            if cached.get("manual"):
                stats["manual_only"] += 1
            if cached.get("auto"):
                stats["auto_only"] += 1
            if any(l.startswith("id") for l in cached.get("manual", []) + cached.get("auto", [])):
                stats["with_id"] += 1
            if any(l.startswith("en") for l in cached.get("manual", []) + cached.get("auto", [])):
                stats["with_en"] += 1
            state = ",".join(langs) + (" (auto)" if cached.get("auto_generated") else " (manual)")

        print(f"[{i}/{len(targets)}] {state}  {vid} {cached.get('embed_title', '')[:40]}")

    results.sort(key=lambda r: (r.get("has_captions") is not False, r["video_id"]))

    fields = ["video_id", "has_captions", "track_count", "languages", "manual_langs",
              "auto_langs", "auto_generated", "embed_title", "source_page", "error"]
    with open(out_dir / "caption-check.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow({
                "video_id": r["video_id"],
                "has_captions": {True: "Y", False: "N", None: "?"}[r.get("has_captions")],
                "track_count": len(r.get("tracks") or []),
                "languages": ";".join(t["lang"] for t in (r.get("tracks") or [])),
                "manual_langs": ";".join(r.get("manual") or []),
                "auto_langs": ";".join(r.get("auto") or []),
                "auto_generated": "Y" if r.get("auto_generated") else "N",
                "embed_title": r.get("embed_title", ""),
                "source_page": r.get("source_page", ""),
                "error": r.get("error", ""),
            })

    (out_dir / "caption-check-results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    total = len(results)
    no_cap = [r for r in results if r.get("has_captions") is False]
    unknown = [r for r in results if r.get("has_captions") is None]
    auto_only = [r for r in results if r.get("has_captions") and not r.get("manual")]
    id_cap = [r for r in results if r.get("has_captions") and
              any(t["lang"].startswith("id") for t in r.get("tracks", []))]

    status_counts = defaultdict(int)
    for r in results:
        status_counts[r.get("player_status") or "ERROR"] += 1

    lines = [
        "# Cek Caption Video (SC 1.2.2 Captions, Prerecorded)",
        "",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}  ",
        f"Video unik diperiksa: {total}  ",
        f"Durasi: {(time.time() - start) / 60:.1f} menit",
        "",
        "Metode: baca halaman `youtube.com/watch?v=<id>`, parse `captionTracks` dari "
        "`ytInitialPlayerResponse`. Tidak memakai API key. Yang dicek hanya ketersediaan "
        "track, bukan akurasi isinya.",
        "",
        "## Ringkasan",
        "",
        "| Aspek | Jumlah |",
        "|-------|--------|",
        f"| Video diperiksa | {total} |",
        f"| Bisa dipastikan (player status OK) | {stats['checked'] + len(no_cap)} |",
        f"| Punya caption | {stats['checked']} |",
        f"| **Pasti tanpa caption** | **{len(no_cap)}** |",
        f"| **Tidak bisa dipastikan (butuh login)** | **{len(unknown)}** |",
        f"| Hanya auto-generated (ASR), tanpa track manual | {len(auto_only)} |",
        f"| Punya caption Bahasa Indonesia | {len(id_cap)} |",
        f"| Punya caption Inggris | {stats['with_en']} |",
        f"| Gagal diperiksa | {stats['failed']} |",
        "",
        "## Status player YouTube",
        "",
        "| Status | Video | Arti |",
        "|--------|-------|------|",
    ]
    status_meaning = {
        "OK": "bisa diputar tanpa login, captionTrack bisa dibaca",
        "LOGIN_REQUIRED": "age-restricted atau member-only; caption tidak bisa dibaca tanpa login",
        "UNPLAYABLE": "tidak bisa diputar dari luar",
        "ERROR": "halaman tidak mengembalikan player response",
    }
    for st, cnt in sorted(status_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| `{st}` | {cnt} | {status_meaning.get(st, '-')} |")

    if no_cap:
        lines += ["", "## Video yang pasti tidak punya caption", "",
                  "| Video ID | Judul embed | Halaman |", "|---------|-------------|---------|"]
        for r in no_cap[:40]:
            lines.append(f"| `{r['video_id']}` | {r.get('embed_title', '')} | "
                         f"{r.get('source_page', '')} |")
        if len(no_cap) > 40:
            lines.append(f"| ... | dan {len(no_cap) - 40} lainnya | "
                         f"lihat `caption-check.csv` |")
        lines.append("")

    if unknown:
        lines += ["## Video yang tidak bisa dipastikan", "",
                  f"{len(unknown)} video membalas `LOGIN_REQUIRED` (kemungkinan age-restricted "
                  "atau member-only). Player response-nya tidak memuat `captionTracks`, jadi "
                  "tidak boleh simpul \"tanpa caption\". Tapi ini tetap temuan tersendiri: "
                  "video yang hanya bisa dilihat setelah login berarti pengguna tidak bisa "
                  "mengaksesnya tanpa akun, dan perlu workaround subtitle atau transkrip di luar "
                  "YouTube.", ""]

    lines += ["", "## Yang BELUM diperiksa", "",
              "- Akurasi isi caption: auto-generated dari ASR untuk Bahasa Indonesia "
              "biasanya salah pada nama diri dan istilah teknis.",
              "- Transkrip teks sebagai alternatif non-audio.",
              "- Apakah audio video punya informasi yang hanya disampaikan lewat suara "
              "(SC 1.2.1 dan 1.2.3).",
              ""]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n[CAPTION] total {total} | dengan caption {stats['checked']} | "
          f"tanpa caption {len(no_cap)} | hanya auto {len(auto_only)} | "
          f"punya ID {len(id_cap)} | error {stats['failed']}")
    print(f"[CAPTION] output: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())