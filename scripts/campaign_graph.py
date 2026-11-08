#!/usr/bin/env python3
"""Añade campañas revisadas al grafo temporal como hipótesis interna."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data" / "quality" / "reviewed" / "graph_temporal.json"
CAMPAIGNS = ROOT / "data" / "quality" / "reviewed" / "campaigns_reviewed.json"
OUT = ROOT / "data" / "quality" / "reviewed" / "graph_campaigns.json"


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    campaigns = json.loads(CAMPAIGNS.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = list(graph["edges"])
    for campaign in campaigns:
        cid = "campaign:" + campaign["campaign_id"]
        review = campaign.get("review", {})
        nodes[cid] = {
            "id": cid,
            "type": "campaign",
            "label": campaign.get("label") or campaign["campaign_id"],
            "category": campaign.get("category"),
            "confidence": review.get("confidence"),
            "decision": review.get("decision"),
        }
        for canonical in campaign.get("canonical_ids", []):
            if canonical in nodes:
                edges.append({
                    "source": cid,
                    "target": canonical,
                    "type": "campaign_member",
                    "weight": 1.0,
                    "note": "pertenece a una campaña sugerida; no atribución",
                })
    payload = {
        "scope": "interno; campañas sugeridas; co-ocurrencia; no atribución",
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "campaigns": sum(1 for n in nodes.values() if n.get("type") == "campaign"),
            "edge_types": dict(Counter(e["type"] for e in edges)),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dot = ["digraph zona_gris_campaigns {", "  rankdir=LR;", "  node [shape=box, style=rounded];"]
    for node in nodes.values():
        dot.append(f'  "{node["id"]}" [label="{str(node.get("label") or node["id"]).replace(chr(34), chr(39))[:80]}"];')
    for edge in edges:
        dot.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="{edge["type"]}"];')
    dot.append("}")
    (OUT.with_suffix(".dot")).write_text("\n".join(dot) + "\n", encoding="utf-8")
    print(payload["counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
