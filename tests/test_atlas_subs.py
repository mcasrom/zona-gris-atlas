from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_subs", ROOT / "scripts" / "atlas_subs.py")
subs = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(subs)


def test_double_opt_in_lifecycle(tmp_path) -> None:
    subs.DB_PATH = tmp_path / "subs.db"
    subs.init_db()
    token, created = subs.subscribe("persona@example.com", page="/", utm_source="test")
    assert created is True
    assert token
    assert subs.mark(token, "confirmed") == "ok"
    assert subs.mark(token, "confirmed") == "already"
    assert subs.mark(token, "unsubscribed") == "ok"
    assert subs.mark(token, "confirmed") == "missing"


def test_invalid_email_is_rejected() -> None:
    try:
        subs.subscribe("no-es-email")
    except ValueError:
        return
    raise AssertionError("email inválido aceptado")
