#!/usr/bin/env python3
"""Compara fotos diarias. No publica y no inventa tendencia con pocos días."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HISTORY = ROOT / "data" / "quality" / "baseline" / "history.jsonl"
DEFAULT_OUT = ROOT / "data" / "quality" / "baseline"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-days", type=int, default=7)
    args = parser.parse_args()
    rows = []
    if args.history.exists():
        rows = [json.loads(line) for line in args.history.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = rows[-30:]
    if len(rows) < 2:
        result = {"status": "insufficient", "snapshots": len(rows), "min_days": args.min_days,
                  "message": "Se necesitan al menos 2 fotos para un delta y 7 para una tendencia mínima."}
    else:
        last, prev = rows[-1], rows[-2]
        def delta(field: str) -> int | None:
            if last.get(field) is None or prev.get(field) is None:
                return None
            return int(last[field]) - int(prev[field])
        result = {
            "status": "insufficient_window" if len(rows) < args.min_days else "ready",
            "snapshots": len(rows),
            "latest": last.get("snapshot_date"),
            "previous": prev.get("snapshot_date"),
            "delta_records": delta("records"),
            "delta_documented": (last.get("by_status", {}).get("DOCUMENTADO", 0) - prev.get("by_status", {}).get("DOCUMENTADO", 0)),
            "delta_pending": (last.get("by_status", {}).get("PENDIENTE", 0) - prev.get("by_status", {}).get("PENDIENTE", 0)),
            "note": "Delta de fotos; no interpretar como tendencia hasta alcanzar la ventana mínima.",
        }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "trend.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Tendencia de la línea base", "", f"Estado: **{result['status']}**", f"Fotos: **{result['snapshots']}**", ""]
    if result.get("message"):
        lines += [result["message"], ""]
    else:
        lines += [f"Última: {result.get('latest')} · anterior: {result.get('previous')}",
                  f"Registros: Δ {result.get('delta_records')}",
                  f"Documentados: Δ {result.get('delta_documented')}",
                  f"Pendientes: Δ {result.get('delta_pending')}", "",
                  result["note"], ""]
    (args.out / "trend.md").write_text("\n".join(lines), encoding="utf-8")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
