#!/usr/bin/env python3
"""Grafo temporal interno: co-ocurrencia por categoría y ventana horaria.

No es atribución. Usa la hora de publicación de la fuente, no la hora del hecho.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL = ROOT / "data" / "quality" / "reviewed" / "canonical_events.json"
DEFAULT_EVENTS = ROOT / "data" / "quality" / "reviewed" / "enriched_sources.jsonl"
DEFAULT_OUT = ROOT / "data" / "quality" / "reviewed"


def stamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    groups = json.loads(args.canonical.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in args.events.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_event = {row.get("event_id"): row for row in rows}
    nodes, edges = {}, []
    for group in groups:
        cid = group["canonical_event_id"]
        member_rows = [by_event.get(eid) for eid in group.get("event_ids", [])]
        member_rows = [x for x in member_rows if x]
        timestamps = [stamp(x.get("published_at_utc")) for x in member_rows]
        timestamps = [x for x in timestamps if x]
        first_ts = min(timestamps) if timestamps else None
        nodes[cid] = {
            "id": cid,
            "type": "event",
            "label": (group.get("titles") or ["—"])[0],
            "category": group.get("category"),
            "first_date": group.get("first_date"),
            "first_published_at": first_ts.isoformat() if first_ts else None,
            "records": group.get("records", 0),
            "country": next((x.get("country") for x in member_rows if x.get("country")), None),
            "source_timestamp": bool(first_ts),
        }
        cat = group.get("category")
        if cat:
            key = "category:" + cat
            nodes.setdefault(key, {"id": key, "type": "category", "label": cat})
            edges.append({"source": cid, "target": key, "type": "tipo", "weight": 1.0,
                          "note": "categoría asignada; no relación"})
        country = nodes[cid].get("country")
        if country:
            key = "country:" + country
            nodes.setdefault(key, {"id": key, "type": "country", "label": country})
            edges.append({"source": cid, "target": key, "type": "lugar", "weight": 0.7,
                          "note": "país documentado o sugerido; no atribución"})
    pairs = set()
    for left, right in combinations(groups, 2):
        a, b = nodes[left["canonical_event_id"]], nodes[right["canonical_event_id"]]
        ta, tb = stamp(a.get("first_published_at")), stamp(b.get("first_published_at"))
        if not ta or not tb or a.get("category") != b.get("category"):
            continue
        hours = abs((ta - tb).total_seconds()) / 3600
        if hours <= 6:
            etype, weight = "co_ocurrencia_6h", round(1.0 - hours / 12, 3)
        elif hours <= 24:
            etype, weight = "co_ocurrencia_24h", round(0.5 - (hours - 6) / 72, 3)
        else:
            continue
        pair = (a["id"], b["id"])
        if pair in pairs:
            continue
        pairs.add(pair)
        edges.append({"source": pair[0], "target": pair[1], "type": etype, "weight": weight,
                      "note": "misma categoría y ventana temporal de publicación; hipótesis, no atribución"})
    payload = {
        "scope": "interno; hora de publicación; co-ocurrencia; no atribución",
        "counts": {
            "events": len(groups),
            "events_with_timestamp": sum(1 for n in nodes.values() if n.get("source_timestamp")),
            "nodes": len(nodes),
            "edges": len(edges),
            "edge_types": dict(Counter(e["type"] for e in edges)),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "graph_temporal.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.out / "graph_temporal_edges.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "target", "type", "weight", "note"])
        writer.writeheader()
        writer.writerows(edges)
    dot = ["digraph zona_gris_temporal {", "  rankdir=LR;", "  node [shape=box, style=rounded];"]
    for node in nodes.values():
        dot.append(f'  "{node["id"]}" [label="{str(node.get("label") or node["id"]).replace(chr(34), chr(39))[:80]}"];')
    for edge in edges:
        dot.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="{edge["type"]}", weight={edge["weight"]}];')
    dot.append("}")
    (args.out / "graph_temporal.dot").write_text("\n".join(dot) + "\n", encoding="utf-8")
    print(payload["counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
