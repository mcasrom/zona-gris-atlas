from __future__ import annotations

import json
from pathlib import Path

from sklearn.metrics import classification_report, confusion_matrix, f1_score


def load(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def evaluate(gold: list[dict], predictions: list[dict], field: str = "domain") -> dict:
    truth = [row[field] for row in gold]
    pred = [row[field] for row in predictions]
    labels = sorted(set(truth) | set(pred))
    return {
        "field": field,
        "macro_f1": round(float(f1_score(truth, pred, labels=labels, average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(truth, pred, labels=labels, average="weighted", zero_division=0)), 4),
        "report": classification_report(truth, pred, labels=labels, zero_division=0, output_dict=True),
        "confusion": confusion_matrix(truth, pred, labels=labels).tolist(),
        "labels": labels,
    }


def check_threshold(result: dict, threshold: float) -> bool:
    return result["macro_f1"] >= threshold
