#!/usr/bin/env python3
"""Capa de documentos primarios. No crea incidentes ni entra en el mapa.

Fuente inicial: CERT-EU Threat Intelligence RSS.
Licencia: CC BY 4.0 (aviso legal de CERT-EU).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET  # nosec B405
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "events" / "primary" / "documents.json"
SOURCES = (
    {"id": "cert-eu", "name": "CERT-EU", "url": "https://cert.europa.eu/publications/threat-intelligence-rss",
     "country": "EU", "language": "en", "license": "CC BY 4.0", "license_url": "https://cert.europa.eu/legal-notice"},
    {"id": "jpcert", "name": "JPCERT/CC", "url": "https://www.jpcert.or.jp/rss/jpcert.rdf",
     "country": "JP", "language": "ja", "license": "Revisar condiciones", "license_url": "https://www.jpcert.or.jp/english/"},
    {"id": "cert-br", "name": "CERT.br", "url": "https://www.cert.br/rss/",
     "country": "BR", "language": "pt", "license": "Revisar condiciones", "license_url": "https://www.cert.br/"},
    {"id": "ncsc-uk", "name": "NCSC-UK", "url": "https://www.ncsc.gov.uk/api/1/services/v1/report-rss-feed.xml",
     "country": "GB", "language": "en", "license": "Revisar condiciones", "license_url": "https://www.ncsc.gov.uk/"},
    {"id": "easa", "name": "EASA", "url": "https://www.easa.europa.eu/en/newsroom-and-events/news/rss.xml",
     "country": "EU", "language": "en", "license": "Revisar condiciones", "license_url": "https://www.easa.europa.eu/"},
    {"id": "cert-fr", "name": "CERT-FR", "url": "https://www.cert.ssi.gouv.fr/feed/",
     "country": "FR", "language": "fr", "license": "Revisar condiciones", "license_url": "https://www.cert.ssi.gouv.fr/"},
)
SOURCE_ID = "cert-eu"
SOURCE_NAME = "CERT-EU"
SOURCE_URL = SOURCES[0]["url"]
LICENSE = SOURCES[0]["license"]
LICENSE_URL = SOURCES[0]["license_url"]
UA = "Mozilla/5.0 (compatible; AtlasZonaGris/0.4; +https://zonagris.pruebapublica.com/metodologia.html)"
MAX_BYTES = 2_000_000


def fetch(url: str = SOURCE_URL) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml"})
    with urllib.request.urlopen(request, timeout=20) as response:  # nosec B310
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("feed demasiado grande")
    return raw


def clean(value: str | None) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return " ".join(value.split())


def parse_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value.strip()).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        return value[:10] if re.match(r"\d{4}-\d{2}-\d{2}", value) else None


def document_id(guid: str, url: str) -> str:
    return "DOC-" + hashlib.sha256((guid or url).encode()).hexdigest()[:12].upper()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(item: ET.Element, names: tuple[str, ...]) -> str:
    for child in list(item):
        if local_name(child.tag) in names and (child.text or "").strip():
            return clean(child.text)
    return ""


def parse_feed(raw: bytes, meta: dict | None = None) -> list[dict]:
    meta = meta or SOURCES[0]
    root = ET.fromstring(raw)  # nosec B314
    documents = []
    for item in root.iter():
        if local_name(item.tag) != "item":
            continue
        title = child_text(item, ("title",))
        link = child_text(item, ("link",))
        if not link:
            for child in list(item):
                if local_name(child.tag) == "link":
                    link = clean(child.attrib.get("href") or child.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"))
                    if link:
                        break
        if not title or not link:
            continue
        summary = child_text(item, ("description", "summary", "content"))
        published = parse_date(child_text(item, ("pubDate", "date", "updated")))
        guid = child_text(item, ("guid", "identifier", "id"))
        documents.append({
            "id": document_id(guid, link),
            "kind": "primary_document",
            "is_incident": False,
            "tier": "primary",
            "source_id": meta["id"],
            "source": meta["name"],
            "source_country": meta["country"],
            "source_language": meta["language"],
            "title": title,
            "url": link,
            "summary": summary,
            "published_at": published,
            "language": meta["language"],
            "license": meta["license"],
            "license_url": meta["license_url"],
            "tlp": "CLEAR" if "TLP:CLEAR" in summary else None,
        })
    return documents


def main() -> int:
    parser = argparse.ArgumentParser(description="Capa de documentos primarios CERT-EU")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=160)
    args = parser.parse_args()

    documents = []
    for meta in SOURCES:
        try:
            documents.extend(parse_feed(fetch(meta["url"]), meta))
        except Exception as exc:  # noqa: BLE001 - una fuente no debe tumbar la capa
            print(f"error {meta['name']}: {exc}", file=sys.stderr)
    documents = documents[: args.limit]
    if not documents:
        print("error capa primaria: ninguna fuente devolvió documentos; se conserva la anterior", file=sys.stderr)
        return 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [{"id": m["id"], "name": m["name"], "country": m["country"], "language": m["language"]} for m in SOURCES],
        "count": len(documents),
        "documents": documents,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"documentos primarios: {len(documents)} → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
