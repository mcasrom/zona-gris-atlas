#!/usr/bin/env python3
"""Informe interno de calidad, normalización y deduplicado.

No publica nada y no modifica el mapa. Usa TF-IDF como primer paso ligero;
sentence-transformers queda para cuando haga falta similitud multilingüe real.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "web" / "assets" / "data" / "events.json"
DEFAULT_OUT = ROOT / "data" / "quality"
THRESHOLD = 0.40
ANALYSIS_MARKERS = (
    "what to know", "what we know", "inside ", "explainer", "analysis", "report says",
    "what the industry", "could europe", "is europe next", "who is behind",
    "market", "forecast", "review",
)
CATEGORY_HINTS = {
    "ciberataque": ("cyber", "ransom", "hack", "breach", "ai-powered", "ai cyber", "freezer", "fridge", "data leak"),
    "amenazas_bomba": ("bomb", "hoax", "bomb threat"),
    "drones_aeropuertos": ("drone", "uav"),
    "gnss": ("gps", "gnss", "jamming", "spoof"),
    "ferroviario": ("rail", "train", "station"),
    "cables_submarinos": ("submarine cable", "subsea cable", "cable cut"),
    "ia_ataques": ("ai attack", "ai-powered attack", "artificial intelligence attack", "llm attack"),
    "migracion_instrumentalizada": ("instrumentalized migration", "weaponized migration", "border pressure"),
}


def norm(text: object) -> str:
    return " ".join(re.sub(r"[^a-z0-9áéíóúüñ]+", " ", str(text or "").casefold()).split())


def iso2(country: str | None) -> str | None:
    mapping = {
        "España": "ES", "Francia": "FR", "Alemania": "DE", "Italia": "IT", "Reino Unido": "GB",
        "Estados Unidos": "US", "China": "CN", "Japón": "JP", "India": "IN", "Brasil": "BR",
        "Corea del Sur": "KR", "Arabia Saudí": "SA", "Israel": "IL", "Polonia": "PL",
        "Dinamarca": "DK", "Chequia": "CZ", "Austria": "AT", "Rusia": "RU", "Colombia": "CO",
        "Canadá": "CA", "Australia": "AU", "México": "MX", "Nigeria": "NG", "Sudáfrica": "ZA",
        "Jersey": "JE", "Unión Europea": None, "OTAN (flanco este)": None,
    }
    return mapping.get(country or "")


def domains(item: dict) -> set[str]:
    out = set()
    for source in item.get("sources", []):
        host = (urlsplit(source.get("url") or "").hostname or "").lower().removeprefix("www.")
        if host:
            out.add(host)
    return out


def suggest_record_type(title: str, description: str) -> str:
    low = (title + " " + description).casefold()
    if any(marker in low for marker in ANALYSIS_MARKERS):
        return "analysis"
    if "report" in low or "brief" in low:
        return "report"
    return "unknown"


def suggest_category(title: str, description: str, current: str | None) -> str | None:
    low = (title + " " + description).casefold()
    scores = {key: sum(1 for term in terms if term in low) for key, terms in CATEGORY_HINTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] and best != current else None


def suggest_country(text: str) -> str | None:
    try:
        countries = json.loads((ROOT / "config" / "geo_countries.json").read_text(encoding="utf-8"))["countries"]
    except (OSError, ValueError, KeyError):
        return None
    low = " " + text.casefold() + " "
    for country in countries:
        for alias in country.get("aliases", []):
            if re.search(rf"\b(?:in|at|near|across|from|inside|outside|throughout|over)\s+(?:the\s+)?{re.escape(alias.casefold())}\b", low):
                return country["name"]
    return None


def normalize(item: dict, canonical: str) -> dict:
    sources = item.get("sources") or []
    return {
        "event_id": item.get("id"),
        "canonical_event_id": canonical,
        "title": item.get("title"),
        "description": item.get("description"),
        "event_date": item.get("event_date"),
        "published_at": item.get("published_at"),
        "event_at_utc": None,
        "published_at_utc": None,
        "date_precision": "day",
        "country": item.get("country"),
        "country_iso2": item.get("country_iso2") or iso2(item.get("country")),
        "city": item.get("city"),
        "place": item.get("place"),
        "airport_iata": None,
        "record_type": "unknown",
        "record_type_suggestion": suggest_record_type(item.get("title") or "", item.get("description") or ""),
        "incident_type": item.get("category"),
        "category_suggestion": suggest_category(item.get("title") or "", item.get("description") or "", item.get("category")),
        "country_suggestion": suggest_country((item.get("title") or "") + " " + (item.get("description") or "")),
        "category_label": item.get("category_label"),
        "verification_status": item.get("verification_status"),
        "attribution_status": (item.get("attribution") or {}).get("status"),
        "source_count": len(sources),
        "independent_domains": len(domains(item)),
        "sources": sources,
        "query_scope": item.get("query_scope"),
        "reviewed_by_human": bool(item.get("reviewed_by_human")),
        "missing": [
            name for name, value in (
                ("published_at_utc", None),
                ("event_at_utc", None),
                ("country_iso2", item.get("country_iso2") or iso2(item.get("country"))),
                ("city", item.get("city")),
                ("airport_iata", None),
            ) if not value
        ],
    }


def cluster(items: list[dict], threshold: float = THRESHOLD) -> list[list[int]]:
    text = [norm((x.get("title") or "") + " " + (x.get("description") or "")) for x in items]
    matrix = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1).fit_transform(text)
    sim = cosine_similarity(matrix)
    parent = list(range(len(items)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i].get("category") != items[j].get("category"):
                continue
            if sim[i, j] < threshold:
                continue
            try:
                di = date.fromisoformat(items[i].get("event_date") or "")
                dj = date.fromisoformat(items[j].get("event_date") or "")
            except ValueError:
                continue
            if abs((di - dj).days) > 2:
                continue
            ci, cj = items[i].get("country"), items[j].get("country")
            if ci and cj and ci != cj:
                continue
            union(i, j)

    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(items)):
        groups[find(i)].append(i)
    return sorted(groups.values(), key=lambda g: (-len(g), g[0]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--threshold", type=float, default=THRESHOLD)
    args = parser.parse_args()
    payload = json.loads(args.events.read_text(encoding="utf-8"))
    items = payload.get("events", [])
    groups = cluster(items, args.threshold)
    canonical_by_index = {}
    canonical_rows = []
    for group in groups:
        seed = min((items[i].get("id") or "" for i in group))
        canonical = "CAN-" + hashlib.sha256(seed.encode()).hexdigest()[:10].upper()
        for i in group:
            canonical_by_index[i] = canonical
        canonical_rows.append({
            "canonical_event_id": canonical,
            "event_ids": [items[i].get("id") for i in group],
            "titles": [items[i].get("title") for i in group],
            "category": items[group[0]].get("category"),
            "first_date": min(items[i].get("event_date") or "" for i in group),
            "last_date": max(items[i].get("event_date") or "" for i in group),
            "records": len(group),
        })
    normalized = [normalize(item, canonical_by_index[i]) for i, item in enumerate(items)]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "events_normalized.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in normalized) + "\n", encoding="utf-8"
    )
    (args.out / "canonical_events.json").write_text(
        json.dumps(canonical_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": len(items),
        "canonical_events": len(groups),
        "duplicates_collapsed": len(items) - len(groups),
        "groups_with_multiple_records": sum(1 for g in groups if len(g) > 1),
        "without_country": sum(1 for x in normalized if not x["country_iso2"]),
        "without_timestamp": sum(1 for x in normalized if not x["published_at_utc"]),
        "without_airport": sum(1 for x in normalized if not x["airport_iata"]),
        "unknown_record_type": sum(1 for x in normalized if x["record_type"] == "unknown"),
        "record_type_suggestions": dict(Counter(x["record_type_suggestion"] for x in normalized)),
        "category_mismatches": sum(1 for x in normalized if x["category_suggestion"]),
        "country_suggestions": sum(1 for x in normalized if x["country_suggestion"]),
        "categories": dict(Counter(x["incident_type"] for x in normalized)),
        "top_groups": canonical_rows[:12],
    }
    corrections = []
    for row in normalized:
        if row.get("category_suggestion"):
            corrections.append({
                "event_id": row["event_id"],
                "field": "incident_type",
                "current": row["incident_type"],
                "suggested": row["category_suggestion"],
                "reason": "términos del título/descripción",
                "title": row["title"],
            })
        if row.get("record_type_suggestion") in {"analysis", "report"}:
            corrections.append({
                "event_id": row["event_id"],
                "field": "record_type",
                "current": row["record_type"],
                "suggested": row["record_type_suggestion"],
                "reason": "marcadores editoriales del título/descripción",
                "title": row["title"],
            })
        if row.get("country_suggestion") and row["country_suggestion"] != row.get("country"):
            corrections.append({
                "event_id": row["event_id"],
                "field": "country",
                "current": row.get("country"),
                "suggested": row["country_suggestion"],
                "reason": "mención explícita con preposición de lugar; pendiente de revisión",
                "title": row["title"],
            })
    (args.out / "corrections.json").write_text(json.dumps(corrections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["corrections"] = len(corrections)
    (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Informe de calidad · Zona Gris", "",
        f"Generado: {report['generated_at']}", "",
        f"- Registros: **{report['records']}**",
        f"- Hechos canónicos: **{report['canonical_events']}**",
        f"- Duplicados colapsados: **{report['duplicates_collapsed']}**",
        f"- Grupos con más de un registro: **{report['groups_with_multiple_records']}**",
        f"- Sin país ISO: **{report['without_country']}**",
        f"- Sin timestamp: **{report['without_timestamp']}**",
        f"- Sin aeropuerto IATA: **{report['without_airport']}**",
        f"- Tipo de registro desconocido: **{report['unknown_record_type']}**", "",
        "## Categorías", "",
        *[f"- {k}: {v}" for k, v in report["categories"].items()],
        "", "## Calidad de campos", "",
        f"- Tipo de registro sugerido: {report['record_type_suggestions']}",
        f"- Posibles categorías mal asignadas: **{report['category_mismatches']}**",
        f"- Sugerencias de país: **{report['country_suggestions']}**",
        f"- Propuestas de corrección: **{report['corrections']}**",
        "", "## Propuestas de revisión", "",
        *[f"- `{x['event_id']}` · {x['field']}: {x['current']} → **{x['suggested']}** · {x['title'][:90]}" for x in corrections[:20]],
        "", "## Grupos principales", "",
    ]
    for group in canonical_rows[:12]:
        lines += [f"### {group['canonical_event_id']} · {group['records']} registros", "", f"- {group['first_date']} → {group['last_date']} · {group['category']}"]
        lines += [f"- {title}" for title in group["titles"][:5]]
        lines.append("")
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"registros {len(items)} · canónicos {len(groups)} · duplicados {len(items)-len(groups)}")
    print(f"sin país {report['without_country']} · sin timestamp {report['without_timestamp']} · tipo desconocido {report['unknown_record_type']}")
    print(f"salida {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
