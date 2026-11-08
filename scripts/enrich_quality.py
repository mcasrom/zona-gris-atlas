#!/usr/bin/env python3
"""Enriquece la capa interna sin inventar hora ni geolocalización."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "data" / "quality" / "reviewed" / "events.jsonl"
DEFAULT_OUT = ROOT / "data" / "quality" / "reviewed"
ISO = {
    "España": "ES", "Francia": "FR", "Alemania": "DE", "Italia": "IT", "Reino Unido": "GB",
    "Estados Unidos": "US", "China": "CN", "Japón": "JP", "India": "IN", "Brasil": "BR",
    "Corea del Sur": "KR", "Arabia Saudí": "SA", "Israel": "IL", "Polonia": "PL",
    "Dinamarca": "DK", "Chequia": "CZ", "Austria": "AT", "Rusia": "RU", "Colombia": "CO",
    "Canadá": "CA", "Australia": "AU", "México": "MX", "Nigeria": "NG", "Sudáfrica": "ZA",
    "Jersey": "JE",
}
IATA = {
    "Copenhague": "CPH", "Copenhagen": "CPH", "Praga": "PRG", "Prague": "PRG",
    "Malpensa": "MXP", "Milan": "MXP", "París": "CDG", "Paris": "CDG",
    "Jersey": "JER", "Leipzig": "LEJ", "Dammam": "DMM", "Tel Aviv": "TLV",
    "Madrid": "MAD", "Londres": "LHR", "London": "LHR", "Manchester": "MAN",
    "Birmingham": "BHX", "Viena": "VIE", "Vienna": "VIE", "Ámsterdam": "AMS",
    "Bruselas": "BRU", "Roma": "FCO", "Lisboa": "LIS", "Dublín": "DUB",
    "Sofía": "SOF", "Oslo": "OSL", "Estocolmo": "ARN", "Helsinki": "HEL",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="source", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", dest="out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.source.read_text(encoding="utf-8").splitlines() if line.strip()]
    enriched = []
    for row in rows:
        item = dict(row)
        published = str(row.get("published_at") or "")
        item["published_date"] = published[:10] if published else None
        item["published_at_utc"] = published if "T" in published else None
        item["event_at_utc"] = row.get("event_at_utc") or None
        item["time_precision"] = "day" if item["published_at_utc"] is None else "timestamp"
        captured = row.get("captured_at")
        try:
            item["captured_at_utc"] = datetime.fromisoformat(str(captured).replace("Z", "+00:00")).astimezone(timezone.utc).isoformat(timespec="seconds") if captured else None
        except ValueError:
            item["captured_at_utc"] = None
        country = row.get("country")
        item["country_iso2"] = row.get("country_iso2") or ISO.get(country or "")
        place = str(row.get("place") or "")
        city = row.get("city")
        airport = row.get("airport_iata")
        if not airport:
            for name, code in IATA.items():
                if name.casefold() in (place + " " + str(city or "")).casefold():
                    airport = code
                    break
        item["airport_iata"] = airport
        item["geo_status"] = "located" if (item["country_iso2"] or city or airport) else "unlocated"
        item["analysis_ready"] = bool(item["published_at_utc"] and item["country_iso2"])
        enriched.append(item)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "enriched.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in enriched) + "\n", encoding="utf-8")
    report = {
        "records": len(enriched),
        "with_country_iso2": sum(1 for x in enriched if x["country_iso2"]),
        "with_airport_iata": sum(1 for x in enriched if x["airport_iata"]),
        "with_timestamp": sum(1 for x in enriched if x["published_at_utc"]),
        "time_precision": dict(Counter(x["time_precision"] for x in enriched)),
        "geo_status": dict(Counter(x["geo_status"] for x in enriched)),
        "analysis_ready": sum(1 for x in enriched if x["analysis_ready"]),
    }
    (args.out / "enriched_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
