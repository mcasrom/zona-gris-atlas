#!/usr/bin/env python3
"""Genera la matriz pública desde el mismo events.json del mapa.

Así la portada, el mapa y la API comparten una sola fuente y un solo total.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.events.read_text(encoding="utf-8"))
    rows = []
    for event in payload.get("events", []):
        sources = event.get("sources") or []
        domains = Counter(
            (urlsplit(s.get("url") or "").hostname or "").lower().removeprefix("www.")
            for s in sources
            if s.get("url")
        )
        rows.append({
            "id": event.get("id"),
            "title": event.get("title"),
            "description": event.get("description"),
            "event_date": event.get("event_date"),
            "published_at": event.get("published_at"),
            "category": event.get("category"),
            "category_label": event.get("category_label"),
            "place": event.get("place") or "No documentado",
            "country": event.get("country"),
            "country_iso2": event.get("country_iso2"),
            "verification_status": event.get("verification_status") or "PENDIENTE",
            "attribution": event.get("attribution") or {"status": "none", "note": "No se atribuye autoría ni intención."},
            "sources": sources,
            "source_count": len(sources),
            "independent_domains": len([d for d in domains if d]),
            "record_type": "incident",
            "member_count": 1,
            "query_scope": event.get("query_scope"),
            "note": "ficha compartida con el mapa; pendiente de revisión humana cuando corresponda",
        })
    rows.sort(key=lambda x: (x.get("event_date") or "", x.get("id") or ""), reverse=True)
    out = {"generated_at": payload.get("generated_at"), "count": len(rows), "events": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"matriz: {len(rows)} registros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
