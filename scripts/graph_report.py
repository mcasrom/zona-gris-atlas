#!/usr/bin/env python3
"""Grafo interno de co-ocurrencia. No es atribución y no se publica."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "data" / "quality" / "canonical_events.json"
DEFAULT_NORMALIZED = ROOT / "data" / "quality" / "events_normalized.jsonl"
DEFAULT_OUT = ROOT / "data" / "quality"


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, default=DEFAULT_IN)
    parser.add_argument("--normalized", type=Path, default=DEFAULT_NORMALIZED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    groups = json.loads(args.canonical.read_text(encoding="utf-8"))
    normalized = [json.loads(line) for line in args.normalized.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_canonical = {row["canonical_event_id"]: row for row in normalized}
    nodes = {}
    edges = []

    for group in groups:
        cid = group["canonical_event_id"]
        row = by_canonical.get(cid, {})
        nodes[cid] = {
            "id": cid,
            "type": "event",
            "label": (group.get("titles") or ["—"])[0],
            "category": group.get("category"),
            "date": group.get("first_date"),
            "country": row.get("country"),
            "place": row.get("place"),
            "status": row.get("verification_status"),
        }
        category = group.get("category")
        if category:
            key = "category:" + category
            nodes.setdefault(key, {"id": key, "type": "category", "label": category})
            edges.append({"source": cid, "target": key, "type": "tipo", "weight": 1.0,
                          "note": "pertenece a la categoría; no implica relación"})
        country = row.get("country")
        if country:
            key = "country:" + country
            nodes.setdefault(key, {"id": key, "type": "country", "label": country})
            edges.append({"source": cid, "target": key, "type": "lugar_mencionado", "weight": 0.7,
                          "note": "país documentado o sugerido para el registro; no atribución"})

    for left, right in combinations(groups, 2):
        a, b = left["canonical_event_id"], right["canonical_event_id"]
        if left.get("category") != right.get("category"):
            continue
        da, db = parse_date(left.get("first_date") or ""), parse_date(right.get("first_date") or "")
        if not da or not db:
            continue
        delta = abs((da - db).days)
        if delta > 2:
            continue
        weight = round(1.0 / (1 + delta), 3)
        edges.append({"source": a, "target": b, "type": "co_ocurrencia", "weight": weight,
                      "note": "misma categoría y cercanía temporal; hipótesis de trabajo, no atribución"})

    args.out.mkdir(parents=True, exist_ok=True)
    payload = {
        "scope": "interno; co-ocurrencia; no atribución",
        "nodes": list(nodes.values()),
        "edges": edges,
        "counts": {"events": len(groups), "nodes": len(nodes), "edges": len(edges)},
    }
    (args.out / "graph.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.out / "graph_nodes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "type", "label", "category", "date", "country", "place", "status"])
        writer.writeheader()
        writer.writerows(nodes.values())
    with (args.out / "graph_edges.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "target", "type", "weight", "note"])
        writer.writeheader()
        writer.writerows(edges)
    dot = ["digraph zona_gris {", "  rankdir=LR;", "  node [shape=box, style=rounded];"]
    for node in nodes.values():
        dot.append(f'  "{node["id"]}" [label="{str(node.get("label") or node["id"]).replace(chr(34), chr(39))[:80]}"];')
    for edge in edges:
        dot.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="{edge["type"]}", weight={edge["weight"]}];')
    dot.append("}")
    (args.out / "graph.dot").write_text("\n".join(dot) + "\n", encoding="utf-8")
    print(f"grafo: {payload['counts']} → {args.out / 'graph.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
