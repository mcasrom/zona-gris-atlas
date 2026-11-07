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
SOURCE_ID = "cert-eu"
SOURCE_NAME = "CERT-EU"
SOURCE_URL = "https://cert.europa.eu/publications/threat-intelligence-rss"
LICENSE = "CC BY 4.0"
LICENSE_URL = "https://cert.europa.eu/legal-notice"
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


def parse_feed(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)  # nosec B314
    if root.tag != "rss":
        raise ValueError("feed RSS no reconocido")
    documents = []
    for item in root.findall(".//item"):
        title = clean(item.findtext("title"))
        url = clean(item.findtext("link"))
        if not title or not url:
            continue
        summary = clean(item.findtext("description"))
        published = parse_date(item.findtext("pubDate"))
        guid = clean(item.findtext("guid"))
        documents.append({
            "id": document_id(guid, url),
            "kind": "primary_document",
            "is_incident": False,
            "tier": "primary",
            "source_id": SOURCE_ID,
            "source": SOURCE_NAME,
            "title": title,
            "url": url,
            "summary": summary,
            "published_at": published,
            "language": "en",
            "license": LICENSE,
            "license_url": LICENSE_URL,
            "tlp": "CLEAR" if "TLP:CLEAR" in summary else None,
        })
    return documents


def main() -> int:
    parser = argparse.ArgumentParser(description="Capa de documentos primarios CERT-EU")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    try:
        documents = parse_feed(fetch())
    except Exception as exc:  # noqa: BLE001 - la fuente no debe tumbar el build
        print(f"error CERT-EU: {exc}", file=sys.stderr)
        return 1
    documents = documents[: args.limit]
    if not documents:
        print("error CERT-EU: feed sin documentos; se conserva la capa anterior", file=sys.stderr)
        return 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_id": SOURCE_ID,
        "source": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "count": len(documents),
        "documents": documents,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"documentos primarios: {len(documents)} → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
