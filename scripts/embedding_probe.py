#!/usr/bin/env python3
"""Prueba de embeddings latentes TF-IDF+SVD. No usa red neuronal."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "quality" / "reviewed" / "events.jsonl"
OUT = ROOT / "data" / "quality" / "reviewed" / "embedding_probe.json"


def clusters(rows: list[dict], matrix, threshold: float, max_days: int = 2) -> int:
    sim = cosine_similarity(matrix)
    parent = list(range(len(rows)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if rows[i].get("incident_type") != rows[j].get("incident_type") or sim[i, j] < threshold:
                continue
            try:
                d = abs((date.fromisoformat(rows[i]["event_date"]) - date.fromisoformat(rows[j]["event_date"])).days)
            except (ValueError, KeyError, TypeError):
                continue
            if d > max_days:
                continue
            a, b = find(i), find(j)
            if a != b:
                parent[b] = a
    return len({find(i) for i in range(len(rows))})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="source", type=Path, default=IN)
    parser.add_argument("--out", dest="out", type=Path, default=OUT)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.source.read_text(encoding="utf-8").splitlines() if line.strip()]
    text = [" ".join((str(row.get("title") or "") + " " + str(row.get("description") or "")).split()) for row in rows]
    tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    matrix = tfidf.fit_transform(text)
    components = min(20, max(2, matrix.shape[1] - 1), max(2, len(rows) - 1))
    svd = TruncatedSVD(n_components=components, random_state=42)
    latent = normalize(svd.fit_transform(matrix))
    result = {
        "method": "tfidf_char_wb_3_5+svd",
        "records": len(rows),
        "components": components,
        "explained_variance": round(float(svd.explained_variance_ratio_.sum()), 4),
        "thresholds": {
            str(t): clusters(rows, latent, t) for t in (0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7)
        },
        "note": "LSA no neuronal; los grupos siguen siendo exploratorios",
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
