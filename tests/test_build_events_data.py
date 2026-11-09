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


def test_relation_followup_is_not_counted_as_independent() -> None:
    parent = {
        "id": "EV-PARENT",
        "event_date": "2026-11-06",
        "published_at": "2026-11-06",
        "captured_at": "2026-11-06T16:00:00Z",
        "title": "Bomb threat at Malpensa",
        "sources": [{"url": "https://example.com/a"}],
    }
    follow = {
        "id": "EV-FOLLOW",
        "event_date": "2026-11-09",
        "published_at": "2026-11-09",
        "captured_at": "2026-11-09T16:00:00Z",
        "title": "Follow-up on the same wave",
        "sources": [{"url": "https://example.com/b"}],
    }
    out = builder.apply_relations(
        [parent, follow],
        {"EV-FOLLOW": {"type": "seguimiento", "of": "EV-PARENT", "note": "misma ola"}},
    )
    assert [row["id"] for row in out] == ["EV-PARENT"]
    assert out[0]["follow_up_sources"][0]["url"] == "https://example.com/b"
    assert "misma ola" in out[0]["observations"]


def test_future_dates_are_quarantined() -> None:
    assert not builder.valid_dates({
        "event_date": "2026-12-04",
        "published_at": "2026-11-04",
        "captured_at": "2026-11-09T00:00:00Z",
    })
    assert builder.valid_dates({
        "event_date": "2026-11-05",
        "published_at": "2026-11-06",
        "captured_at": "2026-11-09T00:00:00Z",
    })
