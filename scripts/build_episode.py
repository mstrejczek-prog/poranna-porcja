#!/usr/bin/env python3
"""Zamienia scenariusz odcinka (episodes/RRRR-MM-DD.md) na MP3 i odświeża feed podcastu.

Format scenariusza:
---
title: Tytuł odcinka
description: Krótki opis (1-2 zdania)
---
MAREK: kwestia
ZOFIA: kwestia
...

Uruchamiane przez GitHub Actions. Wymaga: edge-tts, ffmpeg.
"""
import asyncio
import email.utils
import html
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
EPISODES = ROOT / "episodes"
DOCS = ROOT / "docs"
AUDIO = DOCS / "episodes"
BASE_URL = os.environ.get("BASE_URL", "https://mstrejczek-prog.github.io/poranna-porcja").rstrip("/")
KEEP_AUDIO = 30  # ile ostatnich odcinków trzymać w feedzie

VOICES = {
    "MAREK": "pl-PL-MarekNeural",
    "ZOFIA": "pl-PL-ZofiaNeural",
}
PAUSE_SAME = 0.25   # pauza między kwestiami tej samej osoby (s)
PAUSE_SWITCH = 0.45  # pauza przy zmianie mówiącego (s)


def parse(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    meta = {"title": md_path.stem, "description": ""}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
        text = text[m.end():]
    lines = []
    for raw in text.splitlines():
        mm = re.match(r"^\s*(MAREK|ZOFIA)\s*:\s*(.+)$", raw.strip(), re.I)
        if mm:
            lines.append((mm.group(1).upper(), mm.group(2).strip()))
    if not lines:
        raise SystemExit(f"Brak kwestii MAREK:/ZOFIA: w {md_path}")
    return meta, lines


async def tts(text: str, voice: str, out: Path, retries: int = 3):
    for attempt in range(retries):
        try:
            await edge_tts.Communicate(text, voice, rate="+5%").save(str(out))
            if out.stat().st_size > 0:
                return
        except Exception as e:  # noqa: BLE001
            print(f"TTS retry {attempt + 1}: {e}", file=sys.stderr)
            await asyncio.sleep(3)
    raise RuntimeError(f"TTS nie powiodło się dla: {text[:60]}")


def silence(path: Path, seconds: float):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "anullsrc=r=24000:cl=mono", "-t", str(seconds), "-q:a", "9",
                    "-acodec", "libmp3lame", str(path)], check=True)


async def build_audio(lines, out_mp3: Path):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        s_same, s_switch = tmp / "s1.mp3", tmp / "s2.mp3"
        silence(s_same, PAUSE_SAME)
        silence(s_switch, PAUSE_SWITCH)
        parts, prev = [], None
        for i, (who, txt) in enumerate(lines):
            seg = tmp / f"{i:04d}.mp3"
            await tts(txt, VOICES[who], seg)
            if prev is not None:
                parts.append(s_switch if who != prev else s_same)
            parts.append(seg)
            prev = who
        listfile = tmp / "list.txt"
        listfile.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(listfile), "-ac", "1", "-ar", "24000", "-b:a", "64k",
                        str(out_mp3)], check=True)


def duration(mp3: Path) -> int:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(mp3)], capture_output=True, text=True)
    try:
        return int(float(r.stdout.strip()))
    except ValueError:
        return 0


def build_feed():
    items = []
    mp3s = sorted(AUDIO.glob("*.mp3"), reverse=True)
    for old in mp3s[KEEP_AUDIO:]:
        old.unlink()
    for mp3 in mp3s[:KEEP_AUDIO]:
        md = EPISODES / f"{mp3.stem}.md"
        meta, _ = parse(md) if md.exists() else ({"title": mp3.stem, "description": ""}, None)
        day = datetime.strptime(mp3.stem, "%Y-%m-%d").replace(hour=5, tzinfo=timezone.utc)
        secs = duration(mp3)
        url = f"{BASE_URL}/episodes/{mp3.name}"
        items.append(f"""    <item>
      <title>{html.escape(meta['title'])}</title>
      <description>{html.escape(meta.get('description', ''))}</description>
      <enclosure url="{url}" length="{mp3.stat().st_size}" type="audio/mpeg"/>
      <guid isPermaLink="false">poranna-porcja-{mp3.stem}</guid>
      <pubDate>{email.utils.format_datetime(day)}</pubDate>
      <itunes:duration>{secs // 60}:{secs % 60:02d}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Poranna porcja</title>
    <link>{BASE_URL}/</link>
    <language>pl</language>
    <description>Codzienny, prywatny podcast: architektura, triathlon, biznes, giełda, sztuka, geopolityka, technologie, wynalazki i podróże.</description>
    <itunes:author>Poranna porcja</itunes:author>
    <itunes:image href="{BASE_URL}/cover.png"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
    <itunes:category text="Education"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (DOCS / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"feed.xml: {len(items)} odcinków")


def main():
    AUDIO.mkdir(parents=True, exist_ok=True)
    for md in sorted(EPISODES.glob("*.md")):
        out = AUDIO / f"{md.stem}.mp3"
        if out.exists() and "--force" not in sys.argv:
            continue
        if (datetime.now() - datetime.strptime(md.stem, "%Y-%m-%d")).days > KEEP_AUDIO:
            continue
        print(f"Generuję {md.name}")
        _, lines = parse(md)
        asyncio.run(build_audio(lines, out))
    build_feed()


if __name__ == "__main__":
    main()
