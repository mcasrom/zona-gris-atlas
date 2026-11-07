from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import config, db
from .classify import baseline
from .export import write_atom, write_json
from .ingest import gdelt, rss


def _connection(path: str | None):
    connection = db.connect(path)
    db.init_db(connection)
    return connection


def cmd_init(_args) -> int:
    with _connection(None) as connection:
        db.init_db(connection)
        print(json.dumps(db.stats(connection), ensure_ascii=False))
    return 0


def cmd_ingest(args) -> int:
    with _connection(args.db) as connection:
        if args.source in {"gdelt", "all"}:
            if not args.query:
                raise SystemExit("--query es obligatorio para GDELT")
            inserted = gdelt.ingest(connection, args.query, args.maxrecords, args.timespan)
            print(f"gdelt: {inserted} nuevos")
        if args.source in {"rss", "all"}:
            print(f"rss: {rss.ingest(connection)} nuevos")
    return 0


def cmd_dedupe(args) -> int:
    with _connection(args.db) as connection:
        rows = connection.execute("SELECT id, url, title FROM raw_items").fetchall()
        duplicates = 0
        seen = set()
        for row in rows:
            if row["url"] in seen:
                duplicates += 1
            seen.add(row["url"])
        print(f"items: {len(rows)} · duplicados por URL: {duplicates}")
    return 0


def cmd_classify(args) -> int:
    sample = Path(args.gold)
    if not sample.exists():
        raise SystemExit(f"no existe la muestra opcional: {sample}")
    rows = baseline.load_jsonl(sample)
    model = baseline.train(rows)
    baseline.save(model, Path(args.model))
    print(f"modelo guardado: {args.model} · ejemplos: {len(rows)}")
    for row in rows[: args.show]:
        prediction = baseline.predict(model, f"{row.get('title', '')} {row.get('text', '')}")
        print(json.dumps({"id": row.get("id"), "labels": prediction.labels}, ensure_ascii=False))
    return 0


def cmd_export(args) -> int:
    with _connection(args.db) as connection:
        out = Path(args.out)
        incidents = write_json(connection, out / "incidents.json")
        write_atom(connection, out / "feed.xml")
        print(json.dumps({"incidents": len(incidents), "demo": all(i["demo"] for i in incidents)}, ensure_ascii=False))
    return 0


def cmd_stats(args) -> int:
    with _connection(args.db) as connection:
        print(json.dumps(db.stats(connection), ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zonagris", description="Atlas Zona Gris")
    parser.add_argument("--db", default=None, help="ruta alternativa a SQLite")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("initdb")
    init.set_defaults(func=cmd_init)

    ingest = sub.add_parser("ingest")
    ingest.add_argument("--source", choices=["gdelt", "rss", "all"], default="gdelt")
    ingest.add_argument("--query", default="")
    ingest.add_argument("--maxrecords", type=int, default=50)
    ingest.add_argument("--timespan", default="24h")
    ingest.set_defaults(func=cmd_ingest)

    dedupe = sub.add_parser("dedupe")
    dedupe.set_defaults(func=cmd_dedupe)

    classify = sub.add_parser("classify")
    classify.add_argument("--gold", required=True, help="JSONL opcional de muestra para clasificar")
    classify.add_argument("--model", default=str(config.ROOT / "models" / "baseline.pkl"))
    classify.add_argument("--show", type=int, default=3)
    classify.set_defaults(func=cmd_classify)

    export = sub.add_parser("export")
    export.add_argument("--out", default=str(config.ROOT / "web" / "assets" / "data"))
    export.set_defaults(func=cmd_export)

    stats = sub.add_parser("stats")
    stats.set_defaults(func=cmd_stats)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
