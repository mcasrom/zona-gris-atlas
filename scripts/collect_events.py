#!/usr/bin/env python3
"""Recolector ligero de candidatos RSS para Atlas Zona Gris.

No descarga artículos completos, no usa IA y no publica. Genera candidatos
JSONL que después se revisan manualmente. Bing News RSS se usa como vía para
conservar la URL original del medio; Google News se conserva solo como
referencia de agregación y no se usa para publicar enlaces opacos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (compatible; AtlasZonaGris/0.2; +https://zonagris.pruebapublica.com/metodologia.html)"
QUERIES = [
    ("drones_aeropuertos", "drone airport"),
    ("amenazas_bomba", "bomb threat airport"),
    ("ciberataque", "cyberattack infrastructure"),
    ("ferroviario", "rail disruption"),
    ("gnss", "GPS jamming"),
    ("proteccion_civil", "airport emergency evacuation"),
]
CATEGORY_TERMS = {
    "drones_aeropuertos": ("drone", "dron", "uav", "airport"),
    "amenazas_bomba": ("bomb", "bomba", "evacuat", "threat"),
    "ciberataque": ("cyber", "ciber", "ransom", "hack", "outage"),
    "ferroviario": ("rail", "train", "ferrovi", "station"),
    "gnss": ("gps", "gnss", "jamming", "spoof"),
    "proteccion_civil": ("emergency", "evacuat", "civil protection"),
}


def fetch(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def parse_date(value: str) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        return value[:10] if re.match(r"\d{4}-\d{2}-\d{2}", value) else None


def decode_bing(link: str) -> str:
    """Bing RSS envuelve el enlace; devuelve la URL del medio cuando existe."""
    parsed = urllib.parse.urlparse(link)
    if "bing.com" in parsed.netloc and parsed.path.endswith("apiclick.aspx"):
        values = urllib.parse.parse_qs(parsed.query).get("url", [])
        if values:
            return urllib.parse.unquote(values[0])
    return link


def classify(text: str) -> str:
    low = text.casefold()
    scores = {key: sum(1 for term in terms if term in low) for key, terms in CATEGORY_TERMS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "proteccion_civil"


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^\wáéíóúüñ]+", " ", text.casefold()).split())


def item_id(url: str, title: str) -> str:
    return "CAND-" + hashlib.sha256((url + "|" + normalize(title)).encode()).hexdigest()[:12].upper()


def parse_feed(raw: bytes, source: str, category: str) -> list[dict]:
    root = ET.fromstring(raw)
    if root.tag not in {"rss", "feed"}:
        raise ValueError("feed RSS/Atom no reconocido")
    rows: list[dict] = []
    for item in root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        title = (item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        raw_link = (item.findtext("link") or item.findtext("{http://www.w3.org/2005/Atom}link") or "").strip()
        if not title or not raw_link:
            continue
        link = decode_bing(raw_link)
        published = parse_date(item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}updated") or "")
        rows.append({
            "id": item_id(link, title),
            "title": title,
            "url": link,
            "source": source,
            "published_at": published,
            "event_date": published,
            "date_precision": "publication",
            "category_guess": category if category else classify(title),
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_by_human": False,
            "demo": False,
        })
    return rows


def load_cached(directory: Path, days: int) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(directory.glob("*.xml")):
        source = "Bing News RSS"
        rows.extend(parse_feed(path.read_bytes(), source, ""))
    return rows


def dedupe(rows: list[dict], days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc).date().toordinal() - days
    seen: set[str] = set()
    out: list[dict] = []
    for row in sorted(rows, key=lambda x: x.get("published_at") or "", reverse=True):
        date = row.get("published_at")
        if date:
            try:
                if datetime.fromisoformat(date).date().toordinal() < cutoff:
                    continue
            except ValueError:
                pass
        key = row["url"].split("#")[0].rstrip("/").casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Recolector ligero de candidatos RSS")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "events" / "candidates.jsonl")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--cached-dir", type=Path, help="Directorio con XML ya descargados; no hace red")
    parser.add_argument("--limit", type=int, default=120)
    args = parser.parse_args()
    if args.cached_dir:
        rows = load_cached(args.cached_dir, args.days)
    else:
        rows = []
        for category, query in QUERIES:
            url = "https://www.bing.com/news/search?" + urllib.parse.urlencode({"q": query, "format": "RSS"})
            try:
                rows.extend(parse_feed(fetch(url), "Bing News RSS", category))
            except Exception as exc:  # el colector no debe silenciar la fuente
                print(f"error: {url}: {exc}", file=sys.stderr)
    rows = dedupe(rows, args.days)[: args.limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    print(f"candidatos: {len(rows)} → {args.out}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
