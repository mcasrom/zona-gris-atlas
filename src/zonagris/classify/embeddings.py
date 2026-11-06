"""Clasificador opcional por embeddings.

No descarga modelos ni se usa en la v0.1. Para activarlo:
  pip install -e ".[ml]"
y descargar un modelo local de forma explícita y revisada.
"""
from __future__ import annotations


def available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return False
    return True


def classify(texts: list[str], model_name: str | None = None) -> list[list[float]]:
    if not available():
        raise RuntimeError('instala el extra [ml] y un modelo local antes de usar embeddings')
    if not model_name:
        raise RuntimeError("indica un modelo local; no se descarga ninguno automáticamente")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    return [vector.tolist() for vector in model.encode(texts, normalize_embeddings=True)]
