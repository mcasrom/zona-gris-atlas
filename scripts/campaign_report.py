#!/usr/bin/env python3
"""Campañas/oleadas sugeridas con entidades compartidas. No es atribución."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "data" / "quality" / "reviewed" / "canonical_events.json"
DEFAULT_EVENTS = ROOT / "data" / "quality" / "reviewed" / "events.jsonl"
DEFAULT_OUT = ROOT / "data" / "quality" / "reviewed"
WAVE = re.compile(r"\b(wave|oleada|third|second|segunda|tercera|nueva oleada|new wave)\b", re.I)
CAMPAIGN_KEYS = {
    "ciberataque": ("freezer", "fridge", "refriger", "blood bank", "supermarket"),
    "amenazas_bomba": ("bomb threat", "hoax", "bomb hoax"),
}


def load_entities() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    countries = {}
    try:
        for country in json.loads((ROOT / "config" / "geo_countries.json").read_text(encoding="utf-8"))["countries"]:
            countries[country["name"]] = {a.casefold() for a in [country["name"], *country.get("aliases", [])]}
    except (OSError, ValueError, KeyError):
        pass
    places = {}
    try:
        for place in json.loads((ROOT / "data" / "event_places.json").read_text(encoding="utf-8"))["places"]:
            places[place["place"]] = {a.casefold() for a in [place["name"], *place.get("aliases", [])]}
    except (OSError, ValueError, KeyError):
        pass
    return countries, places


def entity_sets(group: dict, by_event: dict, countries: dict, places: dict) -> tuple[set[str], bool]:
    rows = [by_event.get(eid, {}) for eid in group.get("event_ids", [])]
    text = " ".join(group.get("titles") or []).casefold()
    found = set()
    for name, aliases in countries.items():
        if any(re.search(r"\b" + re.escape(alias) + r"\b", text) for alias in aliases):
            found.add("country:" + name)
    for name, aliases in places.items():
        if any(re.search(r"\b" + re.escape(alias) + r"\b", text) for alias in aliases):
            found.add("place:" + name)
    for row in rows:
        for source in row.get("sources", []):
            host = (urlsplit(source.get("url") or "").hostname or "").lower().removeprefix("www.")
            if host:
                found.add("domain:" + host)
    return found, bool(WAVE.search(text))


def campaign_keys(group: dict) -> set[str]:
    text = " ".join(group.get("titles") or []).casefold()
    category = group.get("category")
    return {"key:" + key for key in CAMPAIGN_KEYS.get(category, ()) if key in text}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="source", type=Path, default=DEFAULT_IN)
    parser.add_argument("--events", dest="events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--out", dest="out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    groups = json.loads(args.source.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in args.events.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_event = {row.get("event_id"): row for row in events}
    countries, places = load_entities()
    candidates = []
    for group in groups:
        if group.get("category") not in CAMPAIGN_KEYS:
            continue
        member_types = [by_event.get(eid, {}).get("record_type") for eid in group.get("event_ids", [])]
        if member_types and all(t in {"analysis", "report"} for t in member_types):
            continue
        entities, wave = entity_sets(group, by_event, countries, places)
        keys = campaign_keys(group)
        if not wave and not keys:
            continue
        candidates.append({**group, "_entities": entities, "_keys": keys, "_wave": wave})
    candidates.sort(key=lambda x: (x.get("category") or "", x.get("first_date") or ""))
    output = []
    used = set()
    for i, group in enumerate(candidates):
        if i in used:
            continue
        cluster = [i]
        used.add(i)
        changed = True
        while changed:
            changed = False
            for j in range(i + 1, len(candidates)):
                if j in used or candidates[j].get("category") != group.get("category"):
                    continue
                try:
                    gap = abs((date.fromisoformat(candidates[j]["first_date"]) - date.fromisoformat(group["last_date"])).days)
                except (ValueError, KeyError, TypeError):
                    continue
                if gap > 5:
                    continue
                shared = candidates[j]["_entities"] & group["_entities"]
                shared_keys = candidates[j]["_keys"] & group["_keys"]
                shared_wave = candidates[j]["_wave"] and group["_wave"]
                if shared or shared_keys or shared_wave:
                    cluster.append(j)
                    used.add(j)
                    group["_entities"] |= candidates[j]["_entities"]
                    group["_keys"] |= candidates[j]["_keys"]
                    group["_wave"] = group["_wave"] or candidates[j]["_wave"]
                    changed = True
        rows = [candidates[k] for k in cluster]
        ids = [c["canonical_event_id"] for c in rows]
        cid = "CMP-" + hashlib.sha256("|".join(sorted(ids)).encode()).hexdigest()[:10].upper()
        titles = [t for c in rows for t in (c.get("titles") or [])]
        output.append({
            "campaign_id": cid,
            "category": group.get("category"),
            "canonical_events": len(rows),
            "first_date": min(c.get("first_date") or "" for c in rows),
            "last_date": max(c.get("last_date") or "" for c in rows),
            "label": titles[0][:120] if titles else group.get("category"),
            "shared_entities": sorted(group["_entities"]),
            "shared_keys": sorted(group["_keys"]),
            "wave_marker": bool(group["_wave"]),
            "canonical_ids": ids,
            "titles": titles[:10],
            "note": "co-ocurrencia y entidades compartidas; hipótesis, no atribución",
        })
    output.sort(key=lambda x: (-x["canonical_events"], x["first_date"]))
    (args.out / "campaigns.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Campañas/oleadas sugeridas", "", "Hipótesis interna; entidades compartidas, no atribución.", ""]
    for c in output:
        lines += [f"## {c['campaign_id']} · {c['category']} · {c['canonical_events']} hechos", "",
                  f"- {c['first_date']} → {c['last_date']}", f"- {c['label']}",
                  f"- Claves: {', '.join(c['shared_keys']) or '—'}",
                  f"- Entidades: {', '.join(c['shared_entities'][:8]) or '—'}", ""]
        lines += [f"- {t}" for t in c["titles"][:5]]
        lines.append("")
    (args.out / "campaigns.md").write_text("\n".join(lines), encoding="utf-8")
    print("campañas:", [(x["category"], x["canonical_events"], x["shared_keys"]) for x in output])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
