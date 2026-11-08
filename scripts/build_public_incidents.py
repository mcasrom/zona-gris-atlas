#!/usr/bin/env python3
"""Genera la matriz pública de hechos revisados, sin análisis ni informes."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data" / "quality" / "reviewed" / "canonical_events.json"
EVENTS = ROOT / "data" / "quality" / "reviewed" / "events.jsonl"
OUT = ROOT / "data" / "quality" / "reviewed" / "public_incidentes.json"


def main() -> int:
    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_event = {row.get("event_id"): row for row in events}
    rows = []
    for group in canonical:
        members = [by_event.get(eid) for eid in group.get("event_ids", [])]
        members = [x for x in members if x]
        factual = [x for x in members if x.get("record_type") not in {"analysis", "report"}]
        if not factual:
            continue
        rep = factual[0]
        sources = []
        seen = set()
        for member in members:
            for source in member.get("sources", []):
                url = source.get("url")
                if url and url not in seen:
                    seen.add(url)
                    sources.append(source)
        domains = Counter((urlsplit(s.get("url") or "").hostname or "").lower().removeprefix("www.") for s in sources)
        statuses = {x.get("verification_status") for x in members}
        attribution = next((x.get("attribution") for x in members if (x.get("attribution") or {}).get("status") not in (None, "none")), None)
        rows.append({
            "id": group["canonical_event_id"],
            "title": rep.get("title"),
            "description": rep.get("description"),
            "event_date": group.get("first_date"),
            "published_at": rep.get("published_at"),
            "category": group.get("category"),
            "category_label": rep.get("category_label") or group.get("category"),
            "place": rep.get("place") or "No documentado",
            "country": rep.get("country"),
            "country_iso2": rep.get("country_iso2"),
            "verification_status": "DOCUMENTADO" if "DOCUMENTADO" in statuses else ("PENDIENTE" if "PENDIENTE" in statuses else "PENDIENTE"),
            "attribution": attribution or {"status": "none", "note": "No se atribuye autoría ni intención."},
            "sources": sources,
            "source_count": len(sources),
            "independent_domains": len([d for d in domains if d]),
            "record_type": "incident",
            "member_count": len(members),
            "query_scope": rep.get("query_scope"),
            "note": "hecho canónico revisado; no incluye análisis ni informes",
        })
    rows.sort(key=lambda x: (x.get("event_date") or "", x.get("title") or ""), reverse=True)
    payload = {"generated_at": None, "count": len(rows), "events": rows}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"matriz pública: {len(rows)} hechos canónicos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
