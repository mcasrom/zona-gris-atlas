#!/usr/bin/env python3
"""Genera un grafo de eventos, fuentes, lugares y categorías.

No atribuye autoría: solo representa relaciones documentales.
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
    nodes = {}
    edges = []

    def node(node_id, kind, label, **extra):
        nodes[node_id] = {"id": node_id, "type": kind, "label": label, **extra}

    def edge(source, target, kind):
        key = (source, target, kind)
        if key not in seen:
            seen.add(key)
            edges.append({"source": source, "target": target, "type": kind})

    seen = set()
    for event in payload.get("events", []):
        eid = event.get("id")
        node(eid, "event", event.get("title"), status=event.get("verification_status"), date=event.get("event_date"))
        cat = event.get("category") or "sin_categoria"
        node(f"category:{cat}", "category", event.get("category_label") or cat)
        edge(eid, f"category:{cat}", "categoria")
        place = event.get("place")
        if place and place != "No documentado":
            node(f"place:{place}", "place", place, country=event.get("country"))
            edge(eid, f"place:{place}", "lugar")
        domains = Counter()
        for source in event.get("sources") or []:
            host = (urlsplit(source.get("url") or "").hostname or "").lower().removeprefix("www.")
            if not host:
                continue
            domains[host] += 1
            node(f"source:{host}", "source", host)
            edge(eid, f"source:{host}", "fuente")
    result = {
        "generated_at": payload.get("generated_at"),
        "nodes": list(nodes.values()),
        "edges": edges,
        "counts": {
            "events": sum(1 for n in nodes.values() if n["type"] == "event"),
            "sources": sum(1 for n in nodes.values() if n["type"] == "source"),
            "places": sum(1 for n in nodes.values() if n["type"] == "place"),
            "categories": sum(1 for n in nodes.values() if n["type"] == "category"),
            "edges": len(edges),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("grafo", result["counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
