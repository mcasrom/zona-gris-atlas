from __future__ import annotations

import json
import pickle  # nosec B403
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

TARGETS = ("domain", "severity", "reality")


@dataclass
class Prediction:
    text: str
    labels: dict[str, str]
    scores: dict[str, dict[str, float]]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _text(row: dict) -> str:
    return f"{row.get('title', '')} {row.get('text', '')}".strip()


def _model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1)),
            (
                "clf",
                LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            ),
        ]
    )


def train(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("el conjunto de entrenamiento está vacío")
    texts = [_text(row) for row in rows]
    models = {}
    for target in TARGETS:
        labels = [row.get(target, "desconocido") for row in rows]
        if len(set(labels)) < 2:
            model = Pipeline(
                [("tfidf", TfidfVectorizer()), ("clf", DummyClassifier(strategy="most_frequent"))]
            )
        else:
            model = _model()
        model.fit(texts, labels)
        models[target] = model
    return {"models": models, "version": "baseline-tfidf-logreg-0.1"}


def save(model: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(model, handle)


def load(path: Path) -> dict:
    with path.open("rb") as handle:
        return pickle.load(handle)  # nosec B301


def predict(model: dict, text: str) -> Prediction:
    labels = {}
    scores = {}
    for target, fitted in model["models"].items():
        labels[target] = str(fitted.predict([text])[0])
        if hasattr(fitted, "predict_proba"):
            probabilities = fitted.predict_proba([text])[0]
            classes = fitted.classes_
            scores[target] = {
                str(label): round(float(probability), 4)
                for label, probability in zip(classes, probabilities, strict=False)
            }
        else:
            scores[target] = {labels[target]: 1.0}
    return Prediction(text=text, labels=labels, scores=scores)


def top_score(scores: dict[str, dict[str, float]]) -> float:
    values = [value for group in scores.values() for value in group.values()]
    return round(float(np.max(values)), 4) if values else 0.0
