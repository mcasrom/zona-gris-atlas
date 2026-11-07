from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_events_data", ROOT / "scripts" / "build_events_data.py")
builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(builder)


def _auto(status: str = "DOCUMENTADO", reviewed: bool = False) -> dict:
    return {
        "id": "AUTO-TEST",
        "title": "Bomb threat at Test Airport",
        "automated": True,
        "reviewed_by_human": reviewed,
        "verification_status": status,
        "status_reason": "4 dominios citados",
        "sources": [{"url": "https://example.com/a"}],
    }


def test_unreviewed_automatic_record_is_demoted_to_pending() -> None:
    rows = builder.merge([], [_auto()])
    assert rows[0]["verification_status"] == "PENDIENTE"
    assert rows[0]["reviewed_by_human"] is False
    assert "revisión humana" in rows[0]["status_reason"]


def test_human_reviewed_automatic_record_keeps_documented() -> None:
    rows = builder.merge([], [_auto(reviewed=True)])
    assert rows[0]["verification_status"] == "DOCUMENTADO"
